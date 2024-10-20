from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def get_professor_url(school_id, professor_name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no UI)
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
    chrome_options.add_argument("--ignore-ssl-errors")  # Ignore SSL errors
    chrome_options.add_argument('--disable-web-security')  # Disable web security
    chrome_options.add_argument('--allow-running-insecure-content')  # Allow insecure content
    chrome_options.add_argument('--no-sandbox')  # No sandbox mode

    # Initialize ChromeDriver using the path to chromedriver.exe
    driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=chrome_options)

    # Search for the professor within the school using the known search URL format
    prof_search_url = f"https://www.ratemyprofessors.com/search/professors/{school_id}?q={professor_name.replace(' ', '%20')}"
    print(f"Professor search URL: {prof_search_url}")
    driver.get(prof_search_url)

    # Wait for the page to load
    time.sleep(3)

    try:
        # Find the first professor link in the search result (adjust class name if needed)
        prof_tag = driver.find_element(By.CLASS_NAME, 'TeacherCard__StyledTeacherCard-syjs0d-0')  # Class name for professor cards
        prof_url = prof_tag.get_attribute('href')  # Extract the professor's URL
        print(f"Professor URL: {prof_url}")
        return prof_url

    except Exception as e:
        print("Professor not found.")
        return None

    finally:
        driver.quit()

def get_professor_ratings(professor_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no UI)
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
    chrome_options.add_argument("--ignore-ssl-errors")  # Ignore SSL errors
    chrome_options.add_argument('--disable-web-security')  # Disable web security
    chrome_options.add_argument('--allow-running-insecure-content')  # Allow insecure content
    chrome_options.add_argument('--no-sandbox')  # No sandbox mode

    # Initialize ChromeDriver using the path to chromedriver.exe
    driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=chrome_options)

    # Directly visit the professor's page using the URL
    driver.get(professor_url)

    # Wait for the page to load
    time.sleep(3)

    try:
        # Locate professor's information
        prof_name = driver.find_element(By.CLASS_NAME, 'NameTitle__NameWrapper-dowf0z-2').text
        rating = driver.find_element(By.CLASS_NAME, 'RatingValue__Numerator-qw8sqy-2').text
        difficulty = difficulty = driver.find_element(By.XPATH, "//div[text()='Level of Difficulty']/preceding-sibling::div").text
        num_ratings = driver.find_element(By.CLASS_NAME, 'RatingValue__NumRatings-qw8sqy-0').text

        return {
            "name": prof_name,
            "rating": rating,
            "difficulty": difficulty,
            "num_ratings": num_ratings
        }

    except Exception as e:
        print("Professor information not found.")
        return

    finally:
        driver.quit()

# Example test
if __name__ == "__main__":
    # Step 1: Find professor's URL using school ID and professor name
    school_id = "18418"  # University of Wisconsin - Madison
    professor_name = "Gary Dahl"  # Replace with the name you're searching for

    # Get professor's URL from the search results
    professor_url = get_professor_url(school_id, professor_name)

    # If professor is found, scrape their ratings
    if professor_url:
        professor_info = get_professor_ratings(professor_url)
        if professor_info:
            print(professor_info)
