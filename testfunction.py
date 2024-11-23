from aiRating import analyze_schedule
import json
from jsonFormat import addRating
from madGrade import scrape_course_info
from RMF import get_professor_rating
schedule = {
  "schedule": {
    "1": {
      "course": {
        "name": "INTER-LS 145",
        "credit": 1.0,
        "description": "How to Succeed in College",
      },
      "time": {
        "LEC": "Online",
        "DIS": "None"
      },
      "instructor": {
        "name": "Leonora Neville",
      }
    },
    "2": {
      "course": {
        "name": "ED POL 140",
        "credit": 3.0,
        "description": "Introduction to Education",
      },
      "time": {
        "LEC": "MW 11:00 AM–11:50 AM",
        "DIS": "F 9:55 AM–10:45 AM"
      },
      "instructor": {
        "name": "None",
      }
    },
    "3": {
      "course": {
        "name": "ENGL 100",
        "credit": 3.0,
        "description": "Introduction to College Composition",
      },
      "time": {
        "LEC": "MW 2:30 PM–3:45 PM",
        "DIS": "None"
      },
      "instructor": {
        "name": "Vatcharit Chantajinda",
      }
    },
    "4": {
      "course": {
        "name": "ANTHRO 104",
        "credit": 3.0,
        "description": "Cultural Anthropology and Human Diversity",
      },
      "time": {
        "LEC": "TR 11:00 AM–11:50 AM",
        "DIS": "R 12:05 PM–12:55 PM"
      },
      "instructor": {
        "name": "Claire Wendland",
      }
    },
    "5": {
      "course": {
        "name": "MATH 375",
        "credit": 5.0,
        "description": "Topics in Multi-Variable Calculus and Linear Algebra",
      },
      "time": {
        "LEC": "TR 9:30 AM–10:45 AM",
        "DIS": "MW 12:05 PM–12:55 PM"
      },
      "instructor": {
        "name": "Caglar Uyanik",
      }
    },
    "6": {
      "course": {
        "name": "COMP SCI 300",
        "credit": 3.0,
        "description": "Programming II",
      },
      "time": {
        "LEC": "MWF 1:20 PM–2:10 PM",
        "DIS": "None"
      },
      "instructor": {
        "name": "Hobbes Legault",
      }
    }
  }
}

#result = analyze_schedule(json.dumps(schedule))
#print(result)

result = get_professor_rating("GARY DAHL")
print(result)
#result = scrape_course_info("MATH 375")
#print(result)

#schedule_info = addRating(schedule)
#print(json.dumps(schedule_info,indent=2))
#result = analyze_schedule(json.dumps(schedule_info))

#print(result)