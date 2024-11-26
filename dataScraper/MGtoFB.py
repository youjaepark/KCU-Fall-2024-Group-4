import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import firebase_admin
from firebase_admin import credentials, firestore
import sys

# Firebase setup
if not firebase_admin._apps:
    cred = credentials.Certificate("ratemyschedule-c9fab-firebase-adminsdk-v1sj7-d91099d3cd.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Global variables
BASE_URL = "https://madgrades.com"
SEARCH_URL = "https://madgrades.com/search?sort=number&query=&page=1"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

MAX_PAGES = 400  # Adjust the number of pages to scrape

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=chrome_options)

def get_course_gpa(driver, course_url):
    try:
        driver.get(course_url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "recharts-wrapper"))
        )
        gpa = driver.execute_script("""
            var legendItems = document.querySelectorAll('.recharts-legend-item-text');
            for (var item of legendItems) {
                if (item.textContent.includes('Cumulative')) {
                    var match = item.textContent.match(/Cumulative - ([\d.]+) GPA/);
                    return match ? parseFloat(match[1]) : null;
                }
            }
            return null;
        """)
        return gpa
    except Exception:
        sys.exit("An error occurred while getting course GPA.")

def process_course_links(driver, course_links):
    courses_to_process = []
    for link in course_links:
        try:
            course_url = link.get_attribute('href')
            course_info = driver.execute_script("""
                var link = arguments[0];
                var nameSpan = link.querySelector('span');
                var subHeader = link.querySelector('div.sub.header');
                var deptSpans = subHeader.querySelectorAll('span span');
                
                var courseCodes = [];
                var courseNumber = null;

                var headerText = subHeader.textContent.trim();
                var numberMatch = headerText.match(/\\b\\d+\\b/);
                if (numberMatch) {
                    courseNumber = parseInt(numberMatch[0], 10);
                }
                
                deptSpans.forEach(function(span) {
                    var deptText = span.textContent.trim().replace(/[\/\d]/g, '').trim();
                    if (deptText) {
                        courseCodes.push(deptText);
                    }
                });
                
                return {
                    name: nameSpan ? nameSpan.textContent.trim() : '',
                    courseCodes: courseCodes,
                    courseNumber: courseNumber
                };
            """, link)
            
            if course_url and course_info['courseCodes']:
                courses_to_process.append({
                    'url': course_url,
                    'info': course_info
                })
        except Exception as e:
            sys.exit(f"Error processing course link: {str(e)}")
    return courses_to_process

def scrape_courses():
    driver = setup_driver()
    page_number = 326
    try:
        while page_number <= MAX_PAGES:
            current_page_url = f"https://madgrades.com/search?sort=number&query=&page={page_number}"
            driver.get(current_page_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "app-content"))
            )
            print(f"\nProcessing page {page_number}...")
            course_links = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ui.blue.segment a.content"))
            )
            courses_to_process = process_course_links(driver, course_links)
            
            for idx, course in enumerate(courses_to_process):
                try:
                    course_url = course['url']
                    course_info = course['info']

                    print(f"\rProcessing course {idx + 1}/{len(courses_to_process)} ", end="")

                    gpa = get_course_gpa(driver, course_url)
                    subject_codes = course_info['courseCodes']
                    course_number = course_info['courseNumber']
                    
                    if not subject_codes or not course_number:
                        continue
                    
                    course_data = {
                        'courseName': course_info['name'],
                        'subjectCode': subject_codes,
                        'courseNumber': course_number,
                        'courseUrl': course_url,
                        'cumulativeGpa': gpa if gpa else "N/A"
                    }
                    
                    save_to_firestore(course_data)
                    time.sleep(random.uniform(0.5, 1))
                except Exception as e:
                    sys.exit(f"Error processing course: {str(e)}")  # Stop the program on exception
            page_number += 1
            time.sleep(1)
    finally:
        driver.quit()

def save_to_firestore(course_data):
    try:
        doc_ref = db.collection('courses').document(f"{course_data['courseNumber']}_{'_'.join(course_data['subjectCode'])}")
        doc_ref.set(course_data)
    except Exception as e:
        sys.exit(f"Error saving to Firestore: {e}")  # Stop the program on exception

if __name__ == "__main__":
    scrape_courses()