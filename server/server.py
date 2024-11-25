from flask import Flask, request, jsonify
import json
from aiRating import analyze_schedule
from addRating import add_rating
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Returns AI rating
@app.route('/evaluate', methods=['POST'])
def return_output():
    try:
        req_data = request.get_json()
        if req_data is None:
            return jsonify({"error": "Invalid JSON data"}), 400
        result = analyze_schedule(json.dumps(req_data))
        return jsonify(result)
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

# Find & add data from database and return full schedule with ratings, urls, etc.
@app.route('/returnrating', methods=['POST'])
def return_rating():
    try:
        req_data = request.get_json()
        if req_data is None:
            return jsonify({"error": "Invalid JSON data"}), 400
        result = add_rating(json.dumps(req_data))
        return jsonify(result)
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)