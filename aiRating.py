import openai
import json
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import certifi


load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


# Initialize MongoDB client




# ... existing code ...


# Initialize MongoDB client
client = MongoClient(os.getenv('MONGODB_URI'), tlsCAFile=certifi.where())


# ... rest of the code ...
db = client['schedule_database']
schedules_collection = db['schedules']
results_collection = db['results']


def store_schedule(schedule):
   """Store the schedule in MongoDB"""
   schedule_doc = {
       'schedule': schedule,
       'timestamp': datetime.now()
   }
   return schedules_collection.insert_one(schedule_doc)


def store_result(result):
   """Store the result in MongoDB"""
   result_doc = {
       'result': result,
       'timestamp': datetime.now()
   }
   return results_collection.insert_one(result_doc)


def get_similar_schedules(schedule, top_n=5):
   """Retrieve similar schedules from the database"""
   all_schedules = list(schedules_collection.find())
  
   if not all_schedules:
       return []


   vectorizer = TfidfVectorizer()
   schedule_texts = [json.dumps(s['schedule']) for s in all_schedules] + [json.dumps(schedule)]
   tfidf_matrix = vectorizer.fit_transform(schedule_texts)
  
   cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
   similar_indices = cosine_similarities.argsort()[:-top_n-1:-1]
  
   return [all_schedules[i] for i in similar_indices]


def rate_schedule(schedule):
   """Rate the schedule using OpenAI API with RAG"""
   similar_schedules = get_similar_schedules(schedule)
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
   return result_dict




def main():
   # Get user input (you can modify this to get input from a file or API)
   schedule = schedule = {
 "1": {
   "course": {
     "name": "INTER-LS 145",
     "credit": "1.00",
     "description": "How to Succeed in College",
     "percentageStudentsGettingA": "91.3%"
   },
   "time": {
     "LEC": "Online",
     "DIS": "None"
   },
   "instructor": {
     "name": "Leonora Neville",
     "instructorRating": "4.4/5"
   }
 },
 "2": {
   "course": {
     "name": "ED POL 140",
     "credit": "3.00",
     "description": "Introduction to Education",
     "percentageStudentsGettingA": "84.0%"
   },
   "time": {
     "LEC": "MW 11:00 AM–11:50 AM",
     "DIS": "F 9:55 AM–10:45 AM"
   },
   "instructor": {
     "name": "None",
     "instructorRating": "None"
   }
 },
 "3": {
   "course": {
     "name": "ENGL 100",
     "credit": "3.00",
     "description": "Introduction to College Composition",
     "percentageStudentsGettingA": "80.0%"
   },
   "time": {
     "LEC": "MW 2:30 PM–3:45 PM",
     "DIS": "None"
   },
   "instructor": {
     "name": "Vatcharit Chantajinda",
     "instructorRating": "None"
   }
 },
 "4": {
   "course": {
     "name": "ANTHRO 104",
     "credit": "3.00",
     "description": "Cultural Anthropology and Human Diversity",
     "percentageStudentsGettingA": "81.2%"
   },
   "time": {
     "LEC": "TR 11:00 AM–11:50 AM",
     "DIS": "R 12:05 PM–12:55 PM"
   },
   "instructor": {
     "name": "Claire Wendland",
     "instructorRating": "3.3/5"
   }
 },
 "5": {
   "course": {
     "name": "MATH 375",
     "credit": "5.00",
     "description": "Topics in Multi-Variable Calculus and Linear Algebra",
     "percentageStudentsGettingA": "50.0%"
   },
   "time": {
     "LEC": "TR 9:30 AM–10:45 AM",
     "DIS": "MW 12:05 PM–12:55 PM"
   },
   "instructor": {
     "name": "Caglar Uyanik",
     "instructorRating": "5/5"
   }
 },
 "6": {
   "course": {
     "name": "COMP SCI 300",
     "credit": "3.00",
     "description": "Programming II",
     "percentageStudentsGettingA": "56.1%"
   },
   "time": {
     "LEC": "MWF 1:20 PM–2:10 PM",
     "DIS": "None"
   },
   "instructor": {
     "name": "Hobbes Legault",
     "instructorRating": "4.6/5"
   }
 }
}
    
  


   # Store schedule in database
   store_schedule(schedule)
  
   # Rate the schedule
   result = rate_schedule(schedule)
  
   # Store result in database
   store_result(result)
  
   # Print the result
   print(json.dumps(result, indent=2))


if __name__ == "__main__":
   main()











