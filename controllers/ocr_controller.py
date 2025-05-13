from assistant.modules import ocr

def extract_text_from_image(image_b64: str) -> str:
    try:
        return ocr.read_text_from_image(image_b64)
    except Exception as e:
        print("[OCR Controller Error]:", e)
        return "Clark couldn't read the image."
