from flask import Blueprint, request, jsonify
from controllers.weather_controller import fetch_weather

weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/weather", methods=["POST"])
def get_weather():
    data = request.get_json()
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "Missing prompt."}), 400

    result = fetch_weather(prompt)
    return jsonify({"weather": result})
