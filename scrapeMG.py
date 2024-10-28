from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Set Chrome options to suppress logs
chrome_options = Options()
chrome_options.add_argument("--headless") # Run Chrome in headless mode
chrome_options.add_argument("--log-level=3") # Suppresses many Chrome logs
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"]) # Hides USB errors on Windows

# Initialize Chrome with the modified options
service = Service("C:/Users/schae/OneDrive - UW-Madison/Documents/JS Apps/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

course_search = "anthro 104"

# URL for course page ** search된 코스도 되도록 수정
# url = "https://madgrades.com/courses/dda5359e-55e4-3269-81f4-8fbfe3da4c0a"
search_url = f"https://madgrades.com/search?query={course_search}"
driver.get(search_url)

# Wait for page to fully load
time.sleep(2)

try:
    # 검색된 코스 list page
    first_inList_link = driver.find_element(By.CSS_SELECTOR, "a[href^='/courses/']")
    first_inList_url = first_inList_link.get_attribute("href")

    driver.get(first_inList_url)
    time.sleep(2)

    # Get course name
    # finding a class attribute
    course_name_element = driver.find_element(By.CLASS_NAME, "sub.header")
    course_name = course_name_element.text
    print("Course name:", course_name)

    # Get cumulative GPA
    # finding a class attribute
    cum_GPA_element = driver.find_element(By.CLASS_NAME, "recharts-legend-item-text")
    cum_GPA = cum_GPA_element.text
    print("Cumulative GPA:", cum_GPA)

    # Get A-grade percentage
    # finding a tspan element
    a_percent_element = driver.find_element(By.CSS_SELECTOR, "tspan[font-size='80%'][font-weight='bold']")
    a_percent = a_percent_element.text
    print("A-Grade percentage:", a_percent)
    
except Exception as e:
    print("Error:", e)

# Close the browser
driver.quit()
