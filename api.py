import openai
import json
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import certifi
from madGrade import scrape_course_info  # Import the function to scrape course info
from RMF import get_professor_rating  # Import the function to get professor rating
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ratemyprofessor
from flask import Flask, request, jsonify
import json
from jsonFormat import addRating
from aiRating import analyze_schedule
#server setup
app = Flask(__name__)

@app.route('/')
def home():
    return "Server is Running..."

@app.route('/return', methods=['POST'])
def return_output():
    try:
        req_data = request.get_json()
        schedule_info = addRating(req_data)
        result = analyze_schedule(json.dumps(schedule_info))
        return jsonify(result)
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

#ratemyprofessor
def get_professor_rating(professor_name):
    if professor_name == "None":
        return "N/A"
        
    try:
        professor = ratemyprofessor.get_professor_by_school_and_name(
            ratemyprofessor.get_school_by_name("University of Wisconsin - Madison"), 
            professor_name
        )
        # Return "None" if professor not found or rating is null
        if professor is None or professor.rating is None:
            return "N/A"
        
        return professor.rating
    except:
        return "N/A"


#madgrades
def scrape_course_info(course_search) -> str:
    url = "https://api.madgrades.com/v1/courses"
    headers = {
        "Authorization": "Token token=492e91a9f7d74dbab647ec2bf11efd27"
    }
    params = {
        "query": course_search
    }
    
    # First API call using regular requests
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        courses = data.get("results", [])
        if courses:
            for course in courses:
                if isinstance(course, dict):
                    course_uuid = course.get("uuid")
                    break
        else:
            return "N/A"
    else:
        return "N/A"

    search_url = "https://madgrades.com/courses/" + course_uuid
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(search_url)
        
        # Wait for the GPA element to be present
        wait = WebDriverWait(driver, 10)
        cum_GPA_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "recharts-legend-item-text"))
        )
        
        if cum_GPA_element:
            gpa_text = cum_GPA_element.text.split('-')[-1].strip().replace(" GPA", "")
            if gpa_text == "Grades Received" or not gpa_text:
                return "N/A"
            return gpa_text
        return "N/A"
        
    except Exception as e:
        print(f"Error scraping course info: {e}")
        return "N/A"
        
    finally:
        try:
            driver.quit()
        except:
            pass




#addRating
def addRating(schedule):
    output = {"schedule": {}}  # Initialize the output structure

    # Extract and process each course in the schedule
    for key, value in schedule["schedule"].items():  # Update to access the nested "schedule"
        course_name = value['course']['name']  # Get the course name
        instructor_name = value['instructor']['name']  # Get the instructor name
        
        # Retrieve cumulative GPA and instructor rating
        cumulativeGPA = scrape_course_info(course_name)  # Use await here
        
        instructorRating = get_professor_rating(instructor_name)  # Get rating
        
        # Construct the output for the current course
        output["schedule"][key] = {
            "course": {
                "name": course_name,
                "credit": value['course']['credit'],
                "description": value['course']['description'],
                "cumulativeGPA": cumulativeGPA  # Add cumulative GPA as a string
            },
            "time": value['time'],
            "instructor": {
                "name": instructor_name,
                "instructorRating": instructorRating  # Add instructor rating
            }
        }
    return output

#aiRating
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
    Rate this college schedule:
    {schedule_json}
    
    Here are some similar schedules and their ratings for context:
    {context}

    Instructions:
    1. Analyze the given schedule and provide ratings for course difficulty, instructor quality, and schedule balance.
    2. Use the following guidelines for data interpretation:
    - Convert cumulativeGPA to a rating on a 10-point scale (e.g., 4.0 becomes 10.0, 3.0 becomes 7.5).
    - If instructorRating is out of 5, multiply by 2 to get the instructor quality rating on a 10-point scale (e.g., 4.4 * 2 = 8.8).
    - For missing data (marked as "N/A"), use the average from other courses or a neutral value:
        - Use 2.5 for cumulativeGPA.
        - Use 3 for instructorRating (quality rating of 6.0 after scaling).
    3. Consider these factors in your analysis:
    - Course Difficulty: Higher cumulativeGPA indicates an easier course.
    - Instructor Quality: Higher instructorRating indicates a better instructor.
    - Schedule Balance:
        - Even distribution of classes throughout the week: up to 3 points.
        - No overlapping class times: up to 3 points.
        - Balanced workload each day: up to 4 points.
    4. Provide ratings on a scale of 0.0 to 10.0, with one decimal place:
    - 0.0 - 2.0: Very Poor
    - 2.1 - 4.0: Poor
    - 4.1 - 6.0: Average
    - 6.1 - 8.0: Good
    - 8.1 - 10.0: Excellent
    5. Calculate the overall rating.
    6. In the comment section:
    - Summarize the overall schedule quality.
    - Highlight strengths and potential challenges.
    - Suggest improvements if applicable.
    - Mention any standout courses or potential conflicts Based on this information, provide ratings and a comprehensive comment.
    7. Please provide only the JSON output without any additional text, using the following format:
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

if __name__ == '__main__':
    app.run(debug=True)