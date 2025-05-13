from flask import Blueprint, request, jsonify
from controllers.intent_controller import get_intent_from_prompt

intent_bp = Blueprint("intent", __name__)

@intent_bp.route("/intent", methods=["POST"])
def detect():
    data = request.get_json()
    prompt = data.get("message")
    if not prompt:
        return jsonify({"intent": "chat"})  # fallback intent
    intent = get_intent_from_prompt(prompt)
    return jsonify({"intent": intent})
