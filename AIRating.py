class AIRating:
    def calculate_rating(self, data):
        # 더미 AI 로직 (실제 AI 모델로 대체 가능)
        print("AI 평가 시작")
        difficulty = data['rating_info']['difficulty']
        usefulness = data['rating_info']['usefulness']
        # 간단한 평균 점수 계산
        rating = (difficulty + usefulness) / 2
        return rating
    
    # http://127.0.0.1:5001/get_scraped_info 또는 http://127.0.0.1:5001/get_ai_rating