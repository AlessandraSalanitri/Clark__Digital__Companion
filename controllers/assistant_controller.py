from assistant.core import Assistant
from assistant.intent_router import detect_intent
from langchain_openai import ChatOpenAI
from controllers.webcam_controller import start_camera, stop_camera, save_preview_to_file
from controllers.web_controller import confirm_checkout
from assistant.utils.logger import log_text, save_image_b64
import base64
import os

model = ChatOpenAI(model="gpt-4o")
assistant = Assistant(model)

def read_image_as_base64(path: str) -> str:
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None


def handle_user_prompt(prompt: str):
    try:
        intent = detect_intent(prompt)
        image_b64 = None

        # Handle camera-based intents
        if intent in ["vision", "ocr", "crossing"]:
            start_camera()
            save_preview_to_file()
            stop_camera()
            image_b64 = read_image_as_base64("static/preview.jpg")

        if intent == "train-confirm":
            return {"response": confirm_checkout(), "image_preview_b64": None}

        result = assistant.handle(prompt, image_b64=image_b64)
        
         # --- Log interaction ---
        log_text(prompt, intent, result)
        if image_b64:
            save_image_b64(image_b64, label=intent)


        # Normalize the response for TTS — always return a string
        if isinstance(result, dict) and "text" in result:
            response_text = result["text"]
        else:
            response_text = result if isinstance(result, str) else str(result)

        return {
            "response": response_text,
            "image_preview_b64": image_b64 if intent in ["vision", "ocr"] else None
        }

    except Exception as e:
        print("[Assistant Controller Error]:", e)
        return {
            "response": "Clark encountered an error.",
            "image_preview_b64": None
        }


# def handle_user_prompt(prompt: str):
#     try:
#         intent = detect_intent(prompt)
#         image_b64 = None

#         # Handle camera-based intents
#         if intent in ["vision", "ocr", "crossing"]:
#             start_camera()
#             save_preview_to_file()
#             stop_camera()

#             image_b64 = read_image_as_base64("static/preview.jpg")

#         if intent == "train-confirm":
#             return confirm_checkout()

#         response = assistant.handle(prompt, image_b64=image_b64)
#         return response
    

#     except Exception as e:
#         print("[Assistant Controller Error]:", e)
#         return {"text": "Clark encountered an error."}


# def handle_user_prompt(prompt: str):
#     try:
#         intent = detect_intent(prompt)
#         image_b64 = None

#         if intent in ["vision", "ocr", "crossing"]:
#             start_camera()
#             save_preview_to_file()
#             stop_camera()
#             image_b64 = read_image_as_base64("static/preview.jpg")

#         if intent == "train-confirm":
#             return confirm_checkout()

#         response = assistant.handle(prompt, image_b64=image_b64)

#         # return response and image preview
#         return {
#             "response": response,
#             "image_preview_b64": image_b64 if intent in ["vision", "ocr"] else None
#         }

#     except Exception as e:
#         print("[Assistant Controller Error]:", e)
#         return {"response": "Clark encountered an error."}
