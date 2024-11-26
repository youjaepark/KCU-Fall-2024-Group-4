import firebase_admin
from firebase_admin import credentials, firestore
from collections import defaultdict

def initialize_firestore() -> firestore.Client:
    """Initialize and return Firestore client."""
    cred = credentials.Certificate('dataScraper/ratemyschedule-c9fab-firebase-adminsdk-v1sj7-2fcb3a43cf.json')
    firebase_admin.initialize_app(cred)
    return firestore.client()

def remove_duplicates(db: firestore.Client):
    """Remove duplicate professor documents based on URL."""
    professors_ref = db.collection('professors')
    professors = professors_ref.stream()
    
    url_map = {}  # Maps URL to (document_id, timestamp)
    duplicates_found = 0
    
    print("Starting duplicate removal process...")
    
    # First pass: collect all URLs and find duplicates
    for prof in professors:
        prof_data = prof.to_dict()
        # Set default values if data is missing
        if 'rating' not in prof_data:
            prof_data['rating'] = "N/A"
        if 'cumulativeGpa' not in prof_data:
            prof_data['cumulativeGpa'] = "N/A"
            
        if 'url' in prof_data:
            current_timestamp = prof_data.get('timestamp', 0)
            
            if prof_data['url'] in url_map:
                # Compare timestamps if available
                existing_id, existing_timestamp = url_map[prof_data['url']]
                
                # Keep the newer document (higher timestamp)
                if current_timestamp > existing_timestamp:
                    # Delete the older document
                    professors_ref.document(existing_id).delete()
                    url_map[prof_data['url']] = (prof.id, current_timestamp)
                else:
                    # Delete the current document
                    professors_ref.document(prof.id).delete()
                
                duplicates_found += 1
                print(f"Removed duplicate professor: {prof_data.get('name', 'Unknown')} "
                      f"(Department: {prof_data.get('department', 'Unknown')})")
            else:
                url_map[prof_data['url']] = (prof.id, current_timestamp)
    
    print(f"\nDuplicate removal complete:")
    print(f"Total duplicates removed: {duplicates_found}")

def main():
    db = initialize_firestore()
    remove_duplicates(db)

if __name__ == "__main__":
    main()