# scraper_test.py

from server import Scraper

def test_scraper():
    scraper = Scraper()
    test_data = {"course": "COMP400", "info": "Sample HTML data"}
    
    # 스크래핑 결과가 예상대로 반환되는지 테스트
    result = scraper.scrape_info(test_data)
    print(result)

# 스크래핑 클래스 테스트 실행
if __name__ == "__main__":
    test_scraper()