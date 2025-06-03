from flask import Blueprint, request, jsonify
from controllers.assistant_controller import handle_user_prompt

assistant_bp = Blueprint("assistant", __name__) 

@assistant_bp.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    message = data.get("message", "")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "No message provided."}), 400

    try:
        response = handle_user_prompt(message)

        # Normalize for frontend
        if isinstance(response, dict):
            return jsonify(response)
        else:
            return jsonify({ "text": response })
    except Exception as e:
        print("Error in /assistant/speak:", e)
        return jsonify({ "error": "Clark failed to respond." }), 500
