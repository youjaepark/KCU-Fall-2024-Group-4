import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_course_info(course_search) -> str:
    url = "https://api.madgrades.com/v1/courses"
    headers = {
        "Authorization": "Token token=492e91a9f7d74dbab647ec2bf11efd27"
    }
    params = {
        "query": course_search
    }
    
    # First API call using regular requests
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        courses = data.get("results", [])
        if courses:
            for course in courses:
                if isinstance(course, dict):
                    course_uuid = course.get("uuid")
                    break
        else:
            return "N/A"
    else:
        return "N/A"

    search_url = "https://madgrades.com/courses/" + course_uuid
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(search_url)
        
        # Wait for the GPA element to be present
        wait = WebDriverWait(driver, 10)
        cum_GPA_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "recharts-legend-item-text"))
        )
        
        if cum_GPA_element:
            gpa_text = cum_GPA_element.text.split('-')[-1].strip().replace(" GPA", "")
            if gpa_text == "Grades Received" or not gpa_text:
                return "N/A"
            return gpa_text
        return "N/A"
        
    except Exception as e:
        print(f"Error scraping course info: {e}")
        return "N/A"
        
    finally:
        try:
            driver.quit()
        except:
            pass