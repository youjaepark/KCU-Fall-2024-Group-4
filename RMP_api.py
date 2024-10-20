import requests
import json
import math
from professor import Professor

class RateMyProfApi:
    def __init__(self, school_id: str):
        self.school_id = school_id

    def scrape_professors(self):
        professors = []
        num_of_prof = self.get_num_of_professors(self.school_id)
        num_of_pages = math.ceil(num_of_prof / 20)

        for i in range(1, num_of_pages + 1):
            page = requests.get(
                f"http://www.ratemyprofessors.com/filter/professor/?&page={i}&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid={self.school_id}"
            )
            json_response = json.loads(page.content)
            for prof_data in json_response['professors']:
                professor = Professor(
                    prof_data['tid'],
                    prof_data['tFname'],
                    prof_data['tLname'],
                    prof_data['tNumRatings'],
                    prof_data['overall_rating']
                )
                professors.append(professor)
        return professors

    def get_num_of_professors(self, school_id):
        page = requests.get(
            f"http://www.ratemyprofessors.com/filter/professor/?&page=1&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid={school_id}"
        )
        temp_jsonpage = json.loads(page.content)
        return temp_jsonpage["remaining"] + 20