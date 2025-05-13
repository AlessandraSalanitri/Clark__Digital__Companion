from flask import Blueprint, request, jsonify
from controllers.crossing_controller import analyze_crossing_from_image

crossing_bp = Blueprint("crossing", __name__)

@crossing_bp.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    image_b64 = data.get("image_b64")

    if not image_b64:
        return jsonify({"error": "Missing image_b64"}), 400

    result = analyze_crossing_from_image(image_b64)
    return jsonify({"result": result})
