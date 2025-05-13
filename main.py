# main.py

import functions_framework
from flask import jsonify, request
from flask_cors import CORS            # enable CORS
from backend.rag_orchestrator import generate_response

# Create a dummy app so CORS decorator can attach headers
# The Functions Framework will ignore this Flask app; we just use CORS on our handler.
from flask import Flask
_dummy_app = Flask(__name__)
CORS(_dummy_app, resources={r"/*": {"origins": "*"}})  # allow any origin

@functions_framework.http
def app(request):
    # Handle CORS preflight
    if request.method == "OPTIONS":
        # Note: flask_cors would normally handle this, but Functions Framework requires manual OPTIONS support
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
        return ("", 204, headers)

    # Health check
    if request.method == "GET":
        return ("ok", 200)

    # RAG generate
    if request.method == "POST":
        data = request.get_json(silent=True)
        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query'"}), 400
        try:
            answer = generate_response(data["query"])
            # Include CORS header on the main response
            response = jsonify({"query": data["query"], "answer": answer})
            response.headers.set("Access-Control-Allow-Origin", "*")
            return response, 200
        except Exception as e:
            response = jsonify({"error": str(e)})
            response.headers.set("Access-Control-Allow-Origin", "*")
            return response, 500

    return (jsonify({"error": "Method not allowed"}), 405, {"Access-Control-Allow-Origin": "*"})
