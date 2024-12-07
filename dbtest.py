from firebase_admin import credentials, firestore
import firebase_admin
import statistics

def calculate_mean_gpa():
    # Initialize Firebase (if not already initialized)
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate("ratemyschedule-c9fab-firebase-adminsdk-v1sj7-2fcb3a43cf.json")
        firebase_admin.initialize_app(cred)

    # Get Firestore database instance
    db = firestore.client()
    
    # Reference to the courses collection
    courses_ref = db.collection('courses')
    
    # Get all documents from the collection
    docs = courses_ref.stream()
    
    # Extract cumulativeGpa values
    gpa_list = []
    for doc in docs:
        gpa = doc.to_dict().get('cumulativeGpa')
        if gpa is not None and gpa != "N/A":  # Skip None and "N/A" values
            try:
                gpa_list.append(float(gpa))
            except ValueError:
                continue  # Skip if conversion to float fails
    
    # Calculate mean if there are any GPAs
    if gpa_list:
        mean_gpa = statistics.mean(gpa_list)
        return round(mean_gpa, 2)
    else:
        return 0.0

def calculate_mean_instructor_rating():
    # Initialize Firebase (if not already initialized)
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate("ratemyschedule-c9fab-firebase-adminsdk-v1sj7-2fcb3a43cf.json")
        firebase_admin.initialize_app(cred)

    # Get Firestore database instance
    db = firestore.client()
    
    # Reference to the courses collection
    courses_ref = db.collection('professors')

    # Get all documents from the collection
    docs = courses_ref.stream()
    
    # Extract cumulativeGpa values
    rating_list = []
    for doc in docs:
        rating = doc.to_dict().get('rating')
        if rating is not None and rating != "N/A":  # Skip None and "N/A" values
            try:
                rating_list.append(float(rating))
            except ValueError:
                continue  # Skip if conversion to float fails
    
    # Calculate mean if there are any ratings
    if rating_list:
        mean_rating = statistics.mean(rating_list)
        return round(mean_rating, 2)
    else:
        return 0.0

# Example usage
if __name__ == "__main__":
    mean_gpa = calculate_mean_gpa()
    print(f"Mean GPA: {mean_gpa}")
    mean_instructor_rating = calculate_mean_instructor_rating()
    print(f"Mean Instructor Rating: {mean_instructor_rating}")