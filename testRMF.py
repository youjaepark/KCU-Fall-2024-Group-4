import ratemyprofessor
# Get the school object for Case Western Reserve University
school = ratemyprofessor.get_school_by_name("University of Wisconsin - Madison")

# Find the professor by name at the specified school
input = input("Enter the name of the professor: ")
professor = ratemyprofessor.get_professor_by_school_and_name(school, input)

# Check if the professor was found
if professor is not None:
    # Print professor details
    print("%s works in the %s Department of %s." % (professor.name, professor.department, professor.school.name))
    print("Rating: %s / 5.0" % professor.rating)
    print("Difficulty: %s / 5.0" % professor.difficulty)
    print("Total Ratings: %s" % professor.num_ratings)
    
    # Check if the 'would take again' percentage is available
    if professor.would_take_again is not None:
        print(("Would Take Again: %s" % round(professor.would_take_again, 1)) + '%')
    else:
        print("Would Take Again: N/A")
else:
    print("Professor not found.")