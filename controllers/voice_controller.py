from flask import request, jsonify, send_file
from audio.voice import tts_to_wav
from speech_recognition import Recognizer, Microphone
import tempfile
import os

recognizer = Recognizer()
mic = Microphone()


def say(text):
    try:
        audio_stream = tts_to_wav(text)
        if audio_stream is None:
            raise ValueError("Audio generation failed")

        audio_stream.seek(0)  
        return audio_stream
    except Exception as e:
        print("[say() error]:", e)
        return None

def listen_once():
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
        text = recognizer.recognize_google(audio)
        return jsonify({"status": "ok", "message": text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


