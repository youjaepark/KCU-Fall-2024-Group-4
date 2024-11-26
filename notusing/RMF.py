import ratemyprofessor

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
