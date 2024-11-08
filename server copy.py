from flask import Flask, request, jsonify

# Scraper와 AIRating 클래스를 불러오는 부분 추가
from scraper import Scraper
from AIRating import AIRating

class Server:
    def __init__(self):
        print("서버 초기화 중...")  # 디버깅용 출력
        self.app = Flask(__name__)
        self.scraper = Scraper()  # Scraper 클래스 인스턴스 생성
        self.ai_rating = AIRating()  # AIRating 클래스 인스턴스 생성

    def add_routes(self):
        print("라우트 추가 중...")  # 디버깅용 출력

        # 기본 경로("/")에 대한 라우트 추가
        @self.app.route('/')
        def home():
            return "서버 정상 실행 중"  # 기본 메시지 출력
    
        # 확장 프로그램에서 데이터를 받는 엔드포인트
        @self.app.route('/receive_data', methods=['POST'])
        def receive_data():
            print("POST /receive_data 요청 처리 중...")  # 디버깅용 출력
            data = request.json
            print("Received data:", data)
            
            # 스크래핑 데이터 처리
            scraped_info = self.scraper.scrape_info(data)
            print("스크래핑 데이터 처리 완료:", scraped_info)  # 디버깅용 출력
            
            # AI 평가 점수 계산
            rating = self.ai_rating.calculate_rating(scraped_info)
            print("AI 평가 점수 계산 완료:", rating)  # 디버깅용 출력
            
            # 처리된 결과 반환
            return jsonify({
                "scraped_info": scraped_info,
                "ai_rating": rating
            })

        # 스크래핑된 정보 반환
        @self.app.route('/get_scraped_info', methods=['GET'])
        def get_scraped_info():
            print("GET /get_scraped_info 요청 처리 중...")  # 디버깅용 출력
            return jsonify(self.scraper.scrape_info(None))

        # AI 평가 점수 반환
        @self.app.route('/get_ai_rating', methods=['POST'])
        def get_ai_rating():
            print("POST /get_ai_rating 요청 처리 중...")  # 디버깅용 출력
            scraped_data = request.json
            rating = self.ai_rating.calculate_rating(scraped_data)
            print("AI 평가 점수 계산 완료:", rating)  # 디버깅용 출력
            return jsonify({"ai_rating": rating})

    def run(self):
        print("서버 실행 준비 중...")  # 디버깅용 출력
        self.add_routes()
        print("Flask 서버 실행 시작")  # 디버깅용 출력
        self.app.run(debug=True, port =5001)

# 서버 실행 코드 추가
if __name__ == '__main__':
    server = Server()  # Server 클래스 인스턴스 생성
    server.run()  # 서버 실행