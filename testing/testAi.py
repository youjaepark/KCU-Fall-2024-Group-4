from aiRating import analyze_schedule

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

result = analyze_schedule(schedule)
print(result)
