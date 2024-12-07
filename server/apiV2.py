# Flask
from flask import Flask, request, jsonify
import json
from flask_cors import CORS
# AI
import openai
import os
from dotenv import load_dotenv
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
        cred = credentials.Certificate({
            "type": os.getenv('FIREBASE_TYPE'),
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace(r'\n', '\n'),
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID'), 
            "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
            "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
            "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_CERT_URL'),
            "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL'),
            "universe_domain": os.getenv('FIREBASE_UNIVERSE_DOMAIN')
        })
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

    prompt = f"""
You are an expert academic advisor specializing in analyzing college course schedules. You have access to a JSON object containing the schedule and its associated data.

Your objective is to produce a reliable and data-driven evaluation of the schedule based on the criteria below. Carefully follow each step and perform all necessary calculations to ensure accuracy. If any data needed for calculations is missing (N/A), use the specified baseline values. After your analysis, provide only the final JSON output without any additional explanation, text, or formatting beyond the specified JSON structure.

Input:
{schedule_json}

Evaluation Criteria:

1. Course Load (0-10):
   - Determine a weighted rating based on historical GPA data for the courses.
   - GPA-to-rating conversion:
       4.0 GPA = 10.0 rating
       3.0 GPA = 7.5 rating
       2.0 GPA = 5.0 rating
   - For N/A GPA values, assume a GPA of 3.67 (which corresponds to a rating of 7.34).
   - Consider the total credit hours and the course level distribution when finalizing the Course Load rating.
     (Higher-level courses or a heavier credit load may slightly reduce the final rating if the difficulty is presumed higher.)

2. Instructor Quality (0-10):
   - Convert instructor ratings from RateMyProfessor by multiplying their rating by 2.
     Example: A 5.0 (out of 5) → 10.0 (out of 10).
   - For N/A or missing instructor ratings, use a baseline rating of 3.52 (which corresponds to 7.04 after multiplying by 2).
   - Weight these ratings proportionally by each course’s credit hours.

3. Schedule Balance (0-10):
   Break down into three subcategories and sum their points:
   - Time Distribution (0-6 points):
     * Are classes reasonably spaced out throughout the week?
     * Are there adequate breaks between classes?
     * Avoidance of excessively long back-to-back sessions (e.g., no 3+ hour back-to-back blocks).
   - Workload Balance (0-4 points):
     * Consider how credit hours are distributed across days.
     * Consider the difficulty levels and ensure no single day is overloaded.
   
   Assign points for each category based on how well the criteria are met, then sum them up for a final Schedule Balance rating.

4. Overall Rating:
   - The overall rating should be an approximate weighted average or balanced blend of the three criteria (Course Load, Instructor Quality, and Schedule Balance).
   - This can be a simple average unless you have reason to adjust weights due to special conditions (e.g., extremely skewed instructor ratings or extremely imbalanced schedules).

5. Comment:
   - Provide a brief comment summarizing the schedule’s strengths and weaknesses.
   - Keep it constructive, honest, and helpful.

Required Output Format:
Return only a single JSON object with the following keys and values:
{{
    "course": float,
    "instructor": float,
    "schedule balance": float,
    "overall": float,
    "comment": string
}}

Example Output:
{{
    "course": 8.5,
    "instructor": 9.0,
    "schedule balance": 8.0,
    "overall": 8.5,
    "comment": "The schedule offers a balanced workload with highly rated instructors..."
}}

Remember:
- Do not include any additional text or commentary outside the JSON.
- Be as accurate and data-driven as possible.
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
    app.run()