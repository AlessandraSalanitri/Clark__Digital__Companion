from flask import Blueprint, jsonify
from controllers.time_controller import fetch_time

time_bp = Blueprint("time", __name__)

@time_bp.route("/now", methods=["GET"])
def get_time():
    result = fetch_time()
    return jsonify({"time": result})
