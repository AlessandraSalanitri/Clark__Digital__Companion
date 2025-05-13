# THIS FILE WAS THE ENTRY POINT OF CLARK WHEN WAS ONLY BACKEND
# AFTER THE DEVELOPMENT OF FRONT END, MAIN WAS RENAMED IN CLI.PY
# HIS FUNCTION IS TO RUN CLARK AS A LOCAL, TERMINAL-BASED VOICE ASSISTANT FOR DEBUGGING
# AND OFFLINE USAGE, WITH LIVE WEBCAM AND MIC
# THE CURRENT ENTRY POINT IS NOW APP.PY WHICH START CLARK WITH FLASK IN A USER-FRIENDLY INTERFACE 


import cv2
import time
import re
from camera.webcam import WebcamStream
from audio.voice import start_listening, tts
from assistant.core import Assistant
from assistant.modules import web
from langchain_openai import ChatOpenAI
from assistant.intent_router import detect_intent
from assistant.modules import crossing

# Boot Clark systems
webcam = WebcamStream()
model = ChatOpenAI(model="gpt-4o")
assistant = Assistant(model)


def audio_callback(recognizer, audio):
    intent = None #If user don't speak, Clark doesn't crash but skips..
    
    
    try:
        prompt = recognizer.recognize_whisper(audio, model="base", language="english")
        print("User:", prompt)
        
         # If user don't talk, skip, don't say anything
        if not prompt.strip():
            print("Clark: (empty input, skipping)")
            return
        
        # Understand user intent
        intent = detect_intent(prompt)
        print(f"[INTENT CLASSIFIED]: {intent}")


        # Clear image unless we need it
        image_b64 = None
        
        # If it's a vision/ocr request, capture image
        if intent in ["vision", "ocr", "crossing"]:
            if not webcam.running:
                webcam.start()
                time.sleep(1)

            raw_b64 = webcam.read(encode=True, for_ui=False)

            # If already str (e.g. if webcam.read is misused or overridden), skip decode
            if isinstance(raw_b64, str):
                image_b64 = raw_b64
            else:
                image_b64 = raw_b64.decode("utf-8")
    
            
        # Reset memory if user moves away from web context
        if detect_intent(prompt) not in ["web", "chat"]:
            if hasattr(assistant, "last_results"):
                del assistant.last_results
            if hasattr(assistant, "last_summary"):
                del assistant.last_summary



        # Avoid vision handling with no image
        if intent in ["vision", "ocr"] and not image_b64:
            tts("Sorry, I couldn't capture anything from the camera.")
            print("Clark: Skipped vision due to empty image.")
            return
        
        if intent in ["vision", "ocr"] and not image_b64:
            tts("Sorry, I couldn't capture anything from the camera.")
            print("Clark: Skipped vision due to empty image.")
            return
        
         # Final inference
        response = assistant.handle(prompt, image_b64)
        
        from assistant.utils.logger import log_text, save_image_b64
        
        # LOG & Save image only if image is present
        if image_b64:
            save_image_b64(image_b64, label=intent)
        # Log the whole interaction
        log_text(prompt, intent, response)
        
        print("Clark:", response)

        if response:
            tts(response)
        else:
            if intent == "chat":
                print("Clark: didn't understand")
                tts("Sorry, I didn't get that. Can you say it again?")
            else:
                print("Clark: couldn't analyze vision")
                tts("Sorry, I couldn't analyze the camera input.")

    except Exception as e:
        print("Error:", e)
        tts("Something went wrong. Please try again.")

    finally:
        if intent in ["vision", "ocr"] and webcam.running:
            webcam.stop()

# Activate Clark with a warm message
tts("Hey, what can I do for you?")

#Mic initialize
try:
    start_listening(audio_callback)
except OSError as e:
    print("Startup mic error:", e)
    tts("Could not access the microphone. Please check your audio device.")
    
try:
    while True:
        if webcam.running:
            frame = webcam.read()
            cv2.imshow("Clark Camera Feed", frame)
            if cv2.waitKey(1) in [27, ord("q")]:
                break
        else:
            time.sleep(0.1)
except KeyboardInterrupt:
    pass

if webcam.running:
    webcam.stop()
cv2.destroyAllWindows()