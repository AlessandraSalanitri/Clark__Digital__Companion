from flask import Blueprint, request, jsonify, send_file
from controllers.voice_controller import say, listen_once

voice_bp = Blueprint("voice", __name__)

@voice_bp.route("/voice/tts", methods=["POST"])
def voice_say():
    data = request.get_json()
    text = data.get("text", "") if data else ""

    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "No valid text provided."}), 400

    try:
        audio_stream = say(text)
        if not audio_stream:
            return jsonify({"error": "TTS failed to generate audio."}), 500

        return send_file(
            audio_stream,
            mimetype="audio/wav",
            as_attachment=False,
            download_name="clark_response.wav"
        )
        
    except Exception as e:
        print("[TTS send_file error]:", e)
        return jsonify({"error": str(e)}), 500


@voice_bp.route("/voice/listen", methods=["POST"])
def voice_listen():
    return listen_once()


