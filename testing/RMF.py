import ratemyprofessor

def get_professor_rating(professor_name):
    # Get the school object for UW Madison
    school = ratemyprofessor.get_school_by_name("University of Wisconsin - Madison")
    
    # Find the professor by name at the specified school
    professor = ratemyprofessor.get_professor_by_school_and_name(school, professor_name)
    
    # Check if the professor was found
    if professor is not None:
        return professor.rating
    else:
        return None
