import json
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Tuple, Set
from collections import defaultdict

def initialize_firestore() -> firestore.Client:
    """Initialize and return Firestore client."""
    cred = credentials.Certificate('dataScraper/ratemyschedule-c9fab-firebase-adminsdk-v1sj7-2fcb3a43cf.json')
    firebase_admin.initialize_app(cred)
    return firestore.client()

def read_jsonl_data(filepath: str) -> Dict[str, int]:
    """Read department data from JSONL file."""
    department_counts = {}
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                try:
                    data = json.loads(line)
                    if 'department' in data and ('professorCount' in data or 'professor_count' in data):
                        dept_name = data['department']
                        # Handle both possible field names
                        count = data.get('professorCount', data.get('professor_count', 0))
                        department_counts[dept_name] = count
                except json.JSONDecodeError:
                    continue
    return department_counts

def get_firestore_counts(db: firestore.Client) -> Dict[str, int]:
    """Query Firestore to get professor counts by department."""
    professors = db.collection('professors').stream()
    dept_counts = defaultdict(int)
    
    for prof in professors:
        prof_data = prof.to_dict()
        if 'department' in prof_data:
            dept_counts[prof_data['department']] += 1
    
    return dict(dept_counts)

def validate_data(jsonl_counts: Dict[str, int], firestore_counts: Dict[str, int]) -> Tuple[Set[str], Dict[str, Tuple[int, int]], Set[str]]:
    """Compare JSONL and Firestore data to find discrepancies."""
    missing_depts = set(jsonl_counts.keys()) - set(firestore_counts.keys())
    mismatched_counts = {
        dept: (jsonl_counts[dept], firestore_counts[dept])
        for dept in set(jsonl_counts.keys()) & set(firestore_counts.keys())
        if jsonl_counts[dept] != firestore_counts[dept]
    }
    matching_depts = {
        dept for dept in set(jsonl_counts.keys()) & set(firestore_counts.keys())
        if jsonl_counts[dept] == firestore_counts[dept]
    }
    
    return missing_depts, mismatched_counts, matching_depts

def print_validation_report(missing_depts: Set[str], mismatched_counts: Dict[str, Tuple[int, int]], matching_depts: Set[str]):
    """Print the validation report."""
    print("\n=== Data Validation Report ===\n")
    
    if missing_depts:
        print("Missing Departments in Firestore:")
        for dept in sorted(missing_depts):
            print(f"  - {dept}")
    else:
        print("No missing departments found.")
    
    print("\nDepartments with Mismatched Counts:")
    if mismatched_counts:
        for dept, (expected, actual) in sorted(mismatched_counts.items()):
            print(f"  - {dept}:")
            print(f"    Expected (JSONL): {expected}")
            print(f"    Actual (Firestore): {actual}")
    else:
        print("  No count mismatches found.")
    
    print(f"\nMatching Departments: {len(matching_depts)}")
    print(f"Missing Departments: {len(missing_depts)}")
    print(f"Mismatched Counts: {len(mismatched_counts)}")

def get_collection_count(db: firestore.Client, collection_name: str) -> int:
    """Get the total number of documents in a collection."""
    collection_ref = db.collection(collection_name)
    return len(list(collection_ref.stream()))

def check_and_remove_duplicates(db: firestore.Client):
    """Check for professors with duplicate URLs and remove duplicates."""
    professors = db.collection('professors').stream()
    url_map = {}  # Maps URL to (document_id, professor_data)
    duplicates_found = 0
    
    print("\nChecking for duplicate professors...")
    
    # First pass: collect all URLs and find duplicates
    for prof in professors:
        prof_data = prof.to_dict()
        if 'url' in prof_data:
            if prof_data['url'] in url_map:
                duplicates_found += 1
                # Delete the duplicate document
                db.collection('professors').document(prof.id).delete()
                print(f"Removed duplicate professor: {prof_data.get('name', 'Unknown')} "
                      f"(Department: {prof_data.get('department', 'Unknown')})")
            else:
                url_map[prof_data['url']] = (prof.id, prof_data)
    
    print(f"\nDuplicate check complete:")
    print(f"Total duplicates removed: {duplicates_found}")

def main():
    # Initialize Firestore
    db = initialize_firestore()
    # Check for and remove duplicates
    check_and_remove_duplicates(db)
    
    # Get total count of professors (after duplicate removal)
    total_professors = get_collection_count(db, 'professors')
    print(f"\nTotal professors in database after duplicate removal: {total_professors}")
    
    # Read data from JSONL file
    jsonl_counts = read_jsonl_data('scraping_state.jsonl')
    
    # Get counts from Firestore
    firestore_counts = get_firestore_counts(db)
    
    # Validate data
    missing_depts, mismatched_counts, matching_depts = validate_data(
        jsonl_counts, firestore_counts
    )
    
    # Print report
    print_validation_report(missing_depts, mismatched_counts, matching_depts)

if __name__ == "__main__":
    main()
