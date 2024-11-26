from notusing.madGrade import scrape_course_info  # Import the function to scrape course info
from notusing.RMF import get_professor_rating  # Import the function to get professor rating

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