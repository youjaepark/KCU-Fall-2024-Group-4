from flask import Flask, request, jsonify
import json
from aiRating import analyze_schedule

app = Flask(__name__)

@app.route('/evaluate', methods=['POST'])
def return_output():
    try:
        req_data = request.get_json()
        if req_data is None:
            return jsonify({"error": "Invalid JSON data"}), 400
        result = analyze_schedule(json.dumps(req_data))
        return jsonify(result)
    except json.JSONDecodeError as je:
        print(f"JSON parsing error: {je}")
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)