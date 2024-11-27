import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import FieldFilter

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