import os
import datetime
import base64

LOG_DIR = "logs"
IMG_DIR = os.path.join(LOG_DIR, "images")
TEXT_LOG = os.path.join(LOG_DIR, "clark_log.txt")

# Setup directories
os.makedirs(IMG_DIR, exist_ok=True)

def log_text(prompt: str, intent: str, result: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] INTENT: {intent}\nUSER: {prompt}\nCLARK: {result}\n{'-'*40}\n"

    with open(TEXT_LOG, "a", encoding="utf-8") as f:
        f.write(entry)

def save_image_b64(image_b64: bytes, label="frame"):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{label}_{timestamp}.jpg"
        path = os.path.join(IMG_DIR, filename)

        with open(path, "wb") as f:
            f.write(base64.b64decode(image_b64))
        
        return path
    except Exception as e:
        print("Clark image log error:", e)
        return None
