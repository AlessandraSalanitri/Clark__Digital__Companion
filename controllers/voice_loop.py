import time
from audio.voice import tts
from assistant.core import Assistant
from assistant.intent_router import detect_intent
from assistant.modules import crossing
from assistant.utils.logger import log_text, save_image_b64
from camera.webcam import WebcamStream
from langchain_openai import ChatOpenAI

webcam = WebcamStream()
model = ChatOpenAI(model="gpt-4o")
assistant = Assistant(model)

def clark_audio_callback(recognizer, audio):
    intent = None
    try:
        prompt = recognizer.recognize_whisper(audio, model="base", language="english")
        print("User:", prompt)

        if not prompt.strip():
            print("Clark: (empty input, skipping)")
            return

        intent = detect_intent(prompt)
        print(f"[INTENT CLASSIFIED]: {intent}")

        image_b64 = None

        if intent in ["vision", "ocr", "crossing"]:
            if not webcam.running:
                webcam.start()
                time.sleep(1)

            raw_b64 = webcam.read(encode=True, for_ui=False)
            image_b64 = raw_b64 if isinstance(raw_b64, str) else raw_b64.decode("utf-8")

        if detect_intent(prompt) not in ["web", "chat"]:
            assistant.last_results = None
            assistant.last_summary = None

        if intent in ["vision", "ocr"] and not image_b64:
            tts("Sorry, I couldn't capture anything from the camera.")
            return

        response = assistant.handle(prompt, image_b64)

        if image_b64:
            save_image_b64(image_b64, label=intent)
        log_text(prompt, intent, response)

        print("Clark:", response)
        tts(response if response else "Sorry, I didn't get that.")

    except Exception as e:
        print("Error:", e)
        tts("Something went wrong.")
    finally:
        if intent in ["vision", "ocr"] and webcam.running:
            webcam.stop()
