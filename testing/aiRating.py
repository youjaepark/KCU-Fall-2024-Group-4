import openai
import json
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import certifi

def analyze_schedule(schedule):
    """
    Analyze a course schedule and return ratings and analysis
    
    Args:
        schedule (dict): Dictionary containing course schedule information
        
    Returns:
        dict: JSON formatted results with ratings and analysis
    """
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # Initialize MongoDB client
    client = MongoClient(os.getenv('MONGODB_URI'), tlsCAFile=certifi.where())
    db = client['schedule_database']
    schedules_collection = db['schedules']
    results_collection = db['results']

    # Store schedule
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
    {json.dumps(schedule, indent=2)}
    
    Here are some similar schedules and their ratings for context:
    {context}

    Instructions:
    1. Analyze the given schedule and provide ratings for course difficulty, instructor quality, and schedule balance.
    2. Use the following guidelines for data interpretation:
    - Convert percentageStudentsGettingA to a decimal and multiply by 10 to get the course difficulty rating (e.g., 91.3% becomes 0.913 * 10 = 9.1).
    - If instructorRating is out of 5, multiply by 2 to get the instructor quality rating on a 10-point scale (e.g., 4.4 * 2 = 8.8).
    - For missing data (marked as "None"), use the average from other courses or a neutral value:
        - Use 0.75 for percentageStudentsGettingA (difficulty rating of 7.5).
        - Use 3 for instructorRating (quality rating of 6.0 after scaling).
    3. Consider these factors in your analysis:
    - Course Difficulty: Higher percentageStudentsGettingA indicates an easier course.
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
    result_dict = json.loads(result_content)
    
    # Store result
    result_doc = {
        'result': result_dict,
        'timestamp': datetime.now()
    }
    results_collection.insert_one(result_doc)
    
    return result_dict