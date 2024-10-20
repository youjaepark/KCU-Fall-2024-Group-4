# ai_rating_test.py

from server import AIRating

def test_ai_rating():
    ai_rating = AIRating()
    test_data = {
        "rating_info": {
            "difficulty": 3.5,
            "usefulness": 4.0
        }
    }
    
    # AI 평가 점수 계산 테스트
    result = ai_rating.calculate_rating(test_data)
    print(f"AI Rating: {result}")

# AI 평가 클래스 테스트 실행
if __name__ == "__main__":
    test_ai_rating()