# controllers/webcam_controller.py
from camera.webcam import WebcamStream
import time
import base64

webcam = WebcamStream()

def start_camera():
    if not webcam.running:
        webcam.start()
        time.sleep(1)  
    return True

def stop_camera():
    if webcam.running:
        webcam.stop()
    return True

def get_frame_bytes():
    return webcam.read()

def get_preview_base64():
    b64 = webcam.read(encode=True, for_ui=True)
    return b64

def save_preview_to_file(path="static/preview.jpg"):
    b64 = webcam.read(encode=True, for_ui=True)
    if not b64:
        return False
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))
    return True
