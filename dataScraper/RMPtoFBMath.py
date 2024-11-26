import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import firebase_admin
from firebase_admin import credentials, firestore
import sys
import os

# Firebase setup
if not firebase_admin._apps:
    cred = credentials.Certificate("dataScraper/ratemyschedule-c9fab-firebase-adminsdk-v1sj7-2fcb3a43cf.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--proxy-server="direct://"')
    options.add_argument('--proxy-bypass-list=*')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(300)  # 5 minutes
    driver.set_script_timeout(300)  # 5 minutes
    return driver

def extract_professor_data(card: BeautifulSoup, base_url: str) -> Optional[Dict]:
    try:
        prof_url = base_url + card['href']
        name = card.find('div', class_='CardName__StyledCardName-sc-1gyrgim-0').text.strip()
        department = card.find('div', class_='CardSchool__Department-sc-19lmz2k-0').text.strip()
        rating_element = card.find('div', class_='CardNumRating__CardNumRatingNumber-sc-17t4b9u-2')
        rating = float(rating_element.text.strip())
        
        ratings_text = card.find('div', class_='CardNumRating__CardNumRatingCount-sc-17t4b9u-3').text.strip()
        num_ratings = int(ratings_text.split()[0])

        feedback_items = card.find_all('div', class_='CardFeedback__CardFeedbackItem-lq6nix-1')
        
        take_again = None
        difficulty = None
        
        for item in feedback_items:
            text = item.text.strip().lower()
            number = item.find('div', class_='CardFeedback__CardFeedbackNumber-lq6nix-2').text.strip()
            if 'would take again' in text:
                take_again = 'N/A' if number == 'N/A' else number
            elif 'level of difficulty' in text:
                difficulty = float(number) if number != 'N/A' else None

        return {
            "name": name,
            "department": department,
            "rating": rating,
            "numRatings": num_ratings,
            "difficulty": difficulty,
            "takeAgain": take_again,
            "url": prof_url
        }
    except Exception as e:
        print(f"Error extracting professor data: {e}")
        return None

def save_to_firestore(professor_data: Dict):
    try:
        # Create a unique ID from the professor's URL
        prof_id = professor_data['url'].split('/')[-1]
        doc_ref = db.collection('professors').document(prof_id)
        doc_ref.set(professor_data)
    except Exception as e:
        sys.exit(f"Error saving to Firestore: {e}")

def load_scraping_state():
    try:
        if os.path.exists('scraping_state.jsonl'):
            states = []
            with open('scraping_state.jsonl', 'r') as f:
                for line in f:
                    if line.strip():  # Skip empty lines
                        states.append(json.loads(line))
            return states
        return []
    except Exception as e:
        print(f"Error loading scraping state: {e}")
        return []

def save_scraping_state(department: str, professor_count: int, department_num: int, letter: str):
    try:
        existing_states = load_scraping_state()
        for state in existing_states:
            if state.get('departmentNum') == department_num and state.get('letter') == letter:
                print(f"Department {department} letter {letter} already exists in state file")
                return

        new_state = {
            'department': department,
            'professorCount': professor_count,
            'departmentNum': department_num,
            'letter': letter
        }
        
        with open('scraping_state.jsonl', 'a') as f:
            f.write(json.dumps(new_state) + '\n')
        print(f"Successfully saved state for department: {department}, letter: {letter}")
    except Exception as e:
        print(f"Error saving scraping state: {e}")

def scrape_professors(base_url: str, search_url: str, dept_num: int, letter: str) -> None:
    driver = setup_driver()
    processed_urls = set()
    
    try:
        print("Starting browser session...")
        for attempt in range(3):
            try:
                driver.get(search_url)
                time.sleep(10)
                break
            except Exception as e:
                if attempt == 2:
                    raise
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(5)
                driver.quit()
                driver = setup_driver()

        # Get department info first
        header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='pagination-header-main-results']"))
        )
        
        department_element = header.find_element(By.CSS_SELECTOR, "span b")
        department = department_element.text.strip()
        
        # Check if this specific letter for this department has been scraped
        existing_states = load_scraping_state()
        for state in existing_states:
            if state.get('departmentNum') == dept_num and state.get('letter') == letter:
                print(f"Skipping {department} letter {letter} - already scraped")
                return set()

        # Get expected professor count and department info from header
        header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='pagination-header-main-results']"))
        )
        
        # Get professor count from the header text
        header_text = header.text
        expected_count = int(''.join(filter(str.isdigit, header_text.split('professors')[0])))
        
        print(f"Found {expected_count} professors in {department} department")

        # Load existing state
        state = load_scraping_state()
        processed_urls = set()

        # Click "Show More" until it disappears
        button_clicks = 0
        while True:
            try:
                button = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//button[text()='Show More']"))
                )
                driver.execute_script("window.scrollTo(0, arguments[0].offsetTop - 100);", button)
                time.sleep(3)
                driver.execute_script("arguments[0].click();", button)
                button_clicks += 1
                print(f"Clicked 'Show More' button {button_clicks} times")
                time.sleep(5)
                
            except TimeoutException:
                print(f"No more 'Show More' button found after {button_clicks} clicks - all professors loaded")
                break

        # Now scrape all professors
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = soup.find_all('a', class_='TeacherCard__StyledTeacherCard-syjs0d-0')
        
        for card in cards:
            prof_url = base_url + card.get('href', '')
            if prof_url not in processed_urls:
                prof_data = extract_professor_data(card, base_url)
                if prof_data:
                    save_to_firestore(prof_data)
                    processed_urls.add(prof_url)
                    print(f"Processed professor {len(processed_urls)} of {expected_count}")

        # After scraping is complete, save the state
        actual_count = len(processed_urls)
        if actual_count > 0:  # Only save state if we actually scraped professors
            save_scraping_state(department, actual_count, dept_num, letter)
            print(f"\nScraping Summary:")
            print(f"Department: {department}")
            print(f"Expected professors: {expected_count}")
            print(f"Actually scraped: {actual_count}")
            print(f"Match: {'Yes' if actual_count == expected_count else 'No'}")
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        raise
    finally:
        driver.quit()
    return processed_urls

def main():
    base_url = "https://www.ratemyprofessors.com"
    department_nums = [38]
    alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

    try:
        for dept_num in department_nums:
            print(f"\nProcessing department {dept_num}")
            for letter in alphabet:
                search_url = f"{base_url}/search/professors/18418?q={letter}&did={dept_num}"
                print(f"\nStarting scraping for letter '{letter}'...")
                try:
                    processed_urls = scrape_professors(base_url, search_url, dept_num, letter)
                    print(f"Successfully processed {len(processed_urls)} professors for letter '{letter}'")
                except Exception as e:
                    print(f"Error processing letter '{letter}': {str(e)}")
                    continue
                time.sleep(5)  # Delay between letters
            print(f"Completed processing for department {dept_num}")
        print("\nAll departments processing completed!")
    except Exception as e:
        print(f"Fatal error in main execution: {str(e)}")
    finally:
        if firebase_admin._apps:
            try:
                firebase_admin.delete_app(firebase_admin.get_app())
                print("Firebase connection closed successfully")
            except Exception as e:
                print(f"Error closing Firebase connection: {str(e)}")

if __name__ == "__main__":
    main()
