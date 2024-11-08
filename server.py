from flask import Flask, request, jsonify
import ratemyprofessor
from testing.aiRating import rate_schedule  # Import the rate_schedule function directly

class Server:
    def __init__(self):
        print("서버 초기화 중...")  # Initializing server
        self.app = Flask(__name__)
        self.school = ratemyprofessor.get_school_by_name("University of Wisconsin - Madison")

    def add_routes(self):
        print("라우트 추가 중...")  # Adding routes

        @self.app.route('/')
        def home():
            return "Server running"  # Basic status message
    
        @self.app.route('/analyze_schedule', methods=['POST'])
        def analyze_schedule():
            try:
                schedule_data = request.json
                
                # Step 1: Get professor ratings for each course
                professor_ratings = {}
                for course_id, course_info in schedule_data.items():
                    prof_name = course_info.get('instructor', {}).get('name')
                    if prof_name and prof_name.lower() != "none":
                        professor = ratemyprofessor.get_professor_by_school_and_name(self.school, prof_name)
                        if professor:
                            professor_ratings[course_id] = {
                                'rating': professor.rating,
                                'difficulty': professor.difficulty,
                                'would_take_again': professor.would_take_again,
                                'num_ratings': professor.num_ratings
                            }
                        else:
                            professor_ratings[course_id] = None
                
                # Step 2: Add professor ratings to schedule data
                for course_id in schedule_data:
                    if course_id in professor_ratings:
                        schedule_data[course_id]['instructor']['rmpRating'] = professor_ratings[course_id]
                
                # Step 3: Get AI rating
                ai_rating = rate_schedule(schedule_data)
                
                # Step 4: Return combined results
                return jsonify({
                    'professor_ratings': professor_ratings,
                    'ai_analysis': ai_rating,
                    'schedule_data': schedule_data
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def run(self):
        print("서버 실행 준비 중...")  # Preparing server
        self.add_routes()
        print("Flask 서버 실행 시작")  # Starting Flask server
        self.app.run(debug=True, port=5001)

if __name__ == '__main__':
    server = Server()
    server.run()
