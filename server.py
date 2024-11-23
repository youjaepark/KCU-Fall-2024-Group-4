from flask import Flask, request, jsonify
import json
from jsonFormat import addRating
from aiRating import analyze_schedule

app = Flask(__name__)

@app.route('/evaluate', methods=['POST'])
def return_output():
    try:
        req_data = request.get_json()
        schedule_info = addRating(req_data)
        result = analyze_schedule(json.dumps(schedule_info))
        return jsonify(result)
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)