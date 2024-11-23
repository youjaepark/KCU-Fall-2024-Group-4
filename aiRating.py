import openai
import json
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import certifi

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

    Output Format (JSON only):
    {
        "course": float,        // Course difficulty rating
        "instructor": float,    // Instructor quality rating
        "schedule_balance": float,  // Schedule organization rating
        "overall": float,       // Weighted average (35/35/30 split)
        "comment": string       // 2-3 sentences: strengths, concerns, suggestions
    }
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