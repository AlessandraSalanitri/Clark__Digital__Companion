from flask import Blueprint, jsonify
from assistant.modules.calendar_module import get_active_reminder, clear_active_reminder

calendar_bp = Blueprint("calendar", __name__)

@calendar_bp.route("/check")
def check_reminder():
    reminder = get_active_reminder()
    if reminder:
        return jsonify({"reminder": reminder})
    return jsonify({"reminder": None})

@calendar_bp.route("/clear")
def clear_reminder():
    clear_active_reminder()
    return jsonify({"status": "cleared"})
