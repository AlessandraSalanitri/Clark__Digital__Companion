from flask import Blueprint, request, jsonify
from controllers.ocr_controller import extract_text_from_image

ocr_bp = Blueprint("ocr", __name__)

@ocr_bp.route("/read", methods=["POST"])
def read():
    data = request.get_json()
    image_b64 = data.get("image_b64")
    
    if not image_b64:
        return jsonify({"error": "Missing image_b64"}), 400

    text = extract_text_from_image(image_b64)
    return jsonify({"text": text})
