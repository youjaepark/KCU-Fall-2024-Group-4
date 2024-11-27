# Flask
from flask import Flask, request, jsonify
import json
from flask_cors import CORS
# AI
import openai
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import certifi
# Firebase
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import FieldFilter

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Format course name
def format_input(course_name, instructor_name):
    # Format course name
    parts = course_name.split()
    course_number = None
    subject_code = []
    
    # Find the first part containing numbers
    for part in parts:
        if any(char.isdigit() for char in part):
            course_number = part
            break
        subject_code.append(part)
    
    if course_number and subject_code:
        # Format instructor name to camel case if provided
        if instructor_name and instructor_name != "No instructors":
            name_parts = instructor_name.split()
            formatted_name = ' '.join(part.capitalize() for part in name_parts)
            return ' '.join(subject_code), course_number, formatted_name
        return ' '.join(subject_code), course_number, instructor_name
    
    return None, None, instructor_name

def add_rating(schedule_json):
    if not firebase_admin._apps:
        cred = credentials.Certificate("ratemyschedule-c9fab-firebase-adminsdk-v1sj7-2fcb3a43cf.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    try:
        # Parse the JSON string into a dictionary
        schedule_data = json.loads(schedule_json)
        schedule = schedule_data.get('schedule', {})
        
        for course_id, course_data in schedule.items():
            course_name = course_data['course'].get('name')
            instructor_name = course_data['instructor'].get('name')
            
            # Parse course_name to get subject_code and course_number
            subject_code, course_number, instructor_name = format_input(course_name,instructor_name)
            
            # Query Firestore for course data
            if subject_code and course_number:
                course_ref = (db.collection('courses')
                    .where(filter=FieldFilter('courseNumber', '==', int(course_number)))
                    .where(filter=FieldFilter('subjectCode', 'array_contains', subject_code))
                    .limit(1))
                course_docs = course_ref.get()
                # Add course GPA if found, otherwise add "N/A"
                if course_docs:
                    doc_dict = course_docs[0].to_dict()
                    cumulativeGpa = doc_dict.get('cumulativeGpa')
                    url = doc_dict.get('courseUrl')
                    if cumulativeGpa:
                        course_data['course']['cumulativeGpa'] = str(cumulativeGpa)
                        course_data['course']['url'] = url
                else:
                    course_data['course']['cumulativeGpa'] = "N/A"
                    course_data['course']['url'] = "N/A"
          
            # Query Firestore for professor data if instructor name is not "No instructors"
            if instructor_name:
                professor_ref = (db.collection('professors')
                    .where(filter=FieldFilter('name', '==', instructor_name))
                    .limit(1))
                professor_docs = professor_ref.get()
                
                # Add instructor rating if found, otherwise add "N/A"
                if professor_docs:
                    doc_dict = professor_docs[0].to_dict()
                    rating = doc_dict.get('rating')
                    url = doc_dict.get('url')
                    if rating:
                        course_data['instructor']['instructorRating'] = str(rating)
                        course_data['instructor']['url'] = url
                else:
                    course_data['instructor']['instructorRating'] = "N/A"
                    course_data['instructor']['url'] = "N/A"
        return schedule_data
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}

# Analyze schedule
def analyze_schedule(schedule_json):
    """
    Analyze a course schedule and return ratings and analysis
    
    Args:
        schedule_json (str): JSON formatted string containing course schedule information
        
    Returns:
        result_json: JSON formatted results with ratings and analysis
    """
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # Initialize MongoDB client
    client = MongoClient(os.getenv('MONGODB_URI'), tlsCAFile=certifi.where())
    db = client['schedule_database']
    schedules_collection = db['schedules']
    results_collection = db['results']

    # Store schedule
    schedule = json.loads(schedule_json)
    schedule_doc = {
        'schedule': schedule,
        'timestamp': datetime.now()
    }
    schedules_collection.insert_one(schedule_doc)

    # Get similar schedules
    all_schedules = list(schedules_collection.find())
    
    if not all_schedules:
        similar_schedules = []
    else:
        vectorizer = TfidfVectorizer()
        schedule_texts = [json.dumps(s['schedule']) for s in all_schedules] + [json.dumps(schedule)]
        tfidf_matrix = vectorizer.fit_transform(schedule_texts)
        
        cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
        similar_indices = cosine_similarities.argsort()[:-6:-1]
        
        similar_schedules = [all_schedules[i] for i in similar_indices]

    # Get ratings for similar schedules
    similar_results = [results_collection.find_one({'_id': s['_id']}) for s in similar_schedules]
    
    context = "\n".join([
        f"Similar schedule: {json.dumps(s['schedule'])}\nRating: {json.dumps(r['result'])}"
        for s, r in zip(similar_schedules, similar_results) if r
    ])

    prompt = f"""
    You are an expert academic advisor specializing in analyzing college course schedules.
    
    Analyze this schedule:
    {schedule_json}
    
    Previous similar schedules and ratings for reference:
    {context}

    Evaluation Criteria:
    1. Course Load (0-10):
       - Base rating on cumulative GPA data
       - GPA conversion: 4.0 = 10.0, 3.0 = 7.5, 2.0 = 5.0
       - For N/A values, use department averages or 2.5 GPA (6.25 rating)
       - Consider total credit hours and course level distribution
    
    2. Instructor Quality (0-10):
       - Convert RateMyProfessor scores: multiply by 2 (5.0 → 10.0)
       - For N/A ratings, use 6.0 as baseline
       - Weight by course credits
    
    3. Schedule Balance (0-10):
       Time Distribution (4 points):
       - Adequate breaks between classes
       - Even spread across week
       - No back-to-back 3+ hour blocks
       
       Workload Balance (3 points):
       - Credit hours per day
       - Difficulty level distribution
       
       Logistics (3 points):
       - Campus travel time
       - Meal break opportunities
       - Study time blocks

    4. Please provide only the JSON output without any additional text, using the following format:
    {{
        "course": float,
        "instructor": float,
        "schedule balance": float,
        "overall": float,
        "comment": string
    }}

    Example Output:
    {{
        "course": 7.5,
        "instructor": 8.0,
        "schedule balance": 6.5,
        "overall": 7.3,
        "comment": "The schedule offers a balanced workload with highly rated instructors..."
    }}
    """
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant that rates college schedules."},
            {"role": "user", "content": prompt}
        ]
    )
    
    result_content = response.choices[0].message.content
    result_json = json.loads(result_content)
    
    # Store result
    result_doc = {
        'result': result_json,
        'timestamp': datetime.now()
    }
    results_collection.insert_one(result_doc)
    
    return result_json

# Returns AI rating
@app.route('/evaluate', methods=['POST'])
def return_output():
    try:
        req_data = request.get_json()
        if req_data is None:
            return jsonify({"error": "Invalid JSON data"}), 400
        result = analyze_schedule(json.dumps(req_data))
        return jsonify(result)
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

# Find & add data from database and return full schedule with ratings, urls, etc.
@app.route('/returnrating', methods=['POST'])
def return_rating():
    try:
        req_data = request.get_json()
        if req_data is None:
            return jsonify({"error": "Invalid JSON data"}), 400
        result = add_rating(json.dumps(req_data))
        return jsonify(result)
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)