from flask import Flask, jsonify, request
from scraper import get_professor_ratings

app = Flask(__name__)

@app.route('/professors', methods=['GET'])
def get_professors():
    school_name = request.args.get('school_name')
    professor_name = request.args.get('professor_name')
    if not school_name or not professor_name:
        return jsonify({"error": "school_name and professor_name are required"}), 400

    # Call the scraping function to get the professor data
    professor_info = get_professor_ratings(school_name, professor_name)

    if not professor_info:
        return jsonify({"error": "Professor not found."}), 404

    return jsonify(professor_info)

if __name__ == '__main__':
    app.run(debug=True)
