import cv2
import numpy as np
import pytesseract
from PIL import Image
import base64
import io
import time
from audio.voice import tts
from camera.webcam import WebcamStream

def decode_base64_image(image_b64):
    image_data = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def detect_light_status(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    red1 = cv2.inRange(hsv, (0, 70, 50), (10, 255, 255))
    red2 = cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))
    red_mask = red1 | red2
    green_mask = cv2.inRange(hsv, (40, 70, 70), (90, 255, 255))
    yellow_mask = cv2.inRange(hsv, (15, 100, 100), (35, 255, 255))

    red_pixels = cv2.countNonZero(red_mask)
    green_pixels = cv2.countNonZero(green_mask)
    yellow_pixels = cv2.countNonZero(yellow_mask)

    if green_pixels > 300:
        return "green"
    elif yellow_pixels > 300:
        return "yellow"
    elif red_pixels > 300:
        return "red"
    else:
        return "unknown"

def detect_timer_text(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config='--psm 6 digits')
    digits = ''.join(filter(str.isdigit, text))
    return digits

def analyze_crossing(image_b64):
    try:
        frame = decode_base64_image(image_b64)
        status = detect_light_status(frame)

        if status == "green":
            return "The pedestrian light is green. It's safe to cross the street."

        elif status in ["red", "yellow"]:
            tts("The pedestrian light is red. Do NOT cross now! I'll tell you when it's green.")
            print("🚦 Clark: monitoring for green light...")

            stream = WebcamStream().start()  # initialize stream here
            start_time = time.time()
            notified_low_timer = False
            unknown_counter = 0

            try:
                while time.time() - start_time < 30:
                    frame_bytes = stream.read(encode=False)
                    if frame_bytes is None:
                        time.sleep(0.5)
                        continue

                    frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
                    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                    if frame is None:
                        continue

                    status = detect_light_status(frame)
                    print(f"[DEBUG] Light status during monitoring: {status}")

                    if status == "green":
                        tts("The light is green now. You can cross safely.")
                        return "The light is green now. You can cross safely."

                    if status == "unknown":
                        unknown_counter += 1
                        if unknown_counter > 5:
                            tts("Clark can't see the signal clearly. Please try adjusting your view.")
                            return "Clark couldn't detect the signal clearly after several attempts."
                    else:
                        unknown_counter = 0

                    digits = detect_timer_text(frame)
                    if digits.isdigit() and not notified_low_timer:
                        seconds = int(digits[:2]) if len(digits) > 1 else int(digits)
                        if seconds <= 3:
                            tts("Only a few seconds left on the signal. Please wait.")
                            notified_low_timer = True
                        elif seconds <= 10:
                            tts(f"{seconds} seconds left. Cross if you're quick.")
                            notified_low_timer = True

                    time.sleep(1)
            finally:
                stream.stop()

            tts("The light is still red after 30 seconds. Please try again soon.")
            return "Clark monitored for green but it stayed red."

        else:
            return "I couldn't clearly detect the traffic light. Try pointing directly at the signal."

    except Exception as e:
        print("Clark crossing detection error:", e)
        return "Sorry, I couldn’t analyze the traffic light correctly."
