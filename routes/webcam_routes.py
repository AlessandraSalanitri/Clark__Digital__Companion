# routes/webcam_routes.py
from flask import Blueprint, Response, jsonify
from controllers.webcam_controller import start_camera, stop_camera, get_frame_bytes

import time

webcam_bp = Blueprint("webcam", __name__)

@webcam_bp.route("/video_feed")
def video_feed():
    def generate():
        while True:
            frame = get_frame_bytes()
            if frame:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )
            time.sleep(0.1)
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@webcam_bp.route("/start_camera", methods=["POST"])
def start_cam_route():
    start_camera()
    return jsonify({"status": "camera started"})

@webcam_bp.route("/stop_camera", methods=["POST"])
def stop_cam_route():
    stop_camera()
    return jsonify({"status": "camera stopped"})
