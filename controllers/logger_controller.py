from assistant.utils import logger

def log_interaction(prompt: str, intent: str, result: str):
    try:
        logger.log_text(prompt, intent, result)
        return {"status": "logged"}
    except Exception as e:
        return {"error": str(e)}

def save_image_from_b64(image_b64: str, label="frame"):
    try:
        path = logger.save_image_b64(image_b64, label)
        return {"status": "saved", "path": path}
    except Exception as e:
        return {"error": str(e)}
