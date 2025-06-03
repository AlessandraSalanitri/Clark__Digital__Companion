from assistant.modules import crossing
from camera.webcam import WebcamStream

webcam = WebcamStream()  # fallback stream object for light monitoring

def analyze_crossing_from_image(image_b64: str) -> str:
    try:
        return crossing.analyze_crossing(image_b64)
    except Exception as e:
        print("[Crossing Controller Error]:", e)
        return "Clark had trouble analyzing the crossing light."
