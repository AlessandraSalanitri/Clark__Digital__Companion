from flask import Blueprint, request, jsonify
from controllers.logger_controller import log_interaction, save_image_from_b64

logger_bp = Blueprint("logger", __name__)

@logger_bp.route("/log", methods=["POST"])
def log_text():
    data = request.get_json()
    prompt = data.get("prompt")
    intent = data.get("intent")
    result = data.get("result")

    if not all([prompt, intent, result]):
        return jsonify({"error": "Missing required fields."}), 400

    return jsonify(log_interaction(prompt, intent, result))


@logger_bp.route("/log_image", methods=["POST"])
def log_image():
    data = request.get_json()
    image_b64 = data.get("image_b64")
    label = data.get("label", "frame")

    if not image_b64:
        return jsonify({"error": "Missing image_b64"}), 400

    return jsonify(save_image_from_b64(image_b64, label))
