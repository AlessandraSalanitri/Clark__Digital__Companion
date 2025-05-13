from flask import Blueprint, request, jsonify
from controllers.train_controller import book_train, confirm_booking

train_bp = Blueprint("train", __name__)

@train_bp.route("/book", methods=["POST"])
def book():
    data = request.get_json()
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "Missing prompt."}), 400

    result = book_train(prompt)
    return jsonify({"response": result})

@train_bp.route("/confirm", methods=["POST"])
def confirm():
    result = confirm_booking()
    return jsonify({"response": result})
