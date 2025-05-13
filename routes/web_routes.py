from flask import Blueprint, request, jsonify
from controllers.web_controller import handle_web_command, confirm_checkout

web_bp = Blueprint("web", __name__)

@web_bp.route("/browse", methods=["POST"])
def browse():
    data = request.get_json()
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    result = handle_web_command(prompt)
    return jsonify(result)

@web_bp.route("/checkout", methods=["POST"])
def checkout():
    result = confirm_checkout()
    return jsonify(result)
