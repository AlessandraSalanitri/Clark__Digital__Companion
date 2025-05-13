import base64
import re
import cv2
import numpy as np
import pytesseract
from typing import Optional

# Configure Tesseract path only if running locally
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class ExpiryDateExtractor:
    OCR_CONFIGS = [
        '--oem 3 --psm 6 -c tessedit_char_whitelist="0123456789./-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"',
        '--oem 3 --psm 11 -c tessedit_char_whitelist="0123456789./-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"',
        '--oem 3 --psm 7 -c tessedit_char_whitelist="0123456789./-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"',
        '--oem 3 --psm 4 -c tessedit_char_whitelist="0123456789./-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"',
        '--oem 3 --psm 12 -c tessedit_char_whitelist="0123456789./-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"',

    ]

    EXPIRY_PATTERNS = [
        r"\b(?:exp|expiry|scad)[\.: ]{0,2}(0[1-9]|1[0-2])[.\-/ ]?(20\d{2})\b",
        r"\b20\d{2}[.\-/ ]{1,2}(0[1-9]|1[0-2])\b",
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[., ]{0,2}(20\d{2})\b",
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4}\b",  # new: AUG 2025
        r"\b\d{4}\b",  # new: fallback on year-only if needed
    ]


    @staticmethod
    def decode_image(image_b64: str) -> Optional[np.ndarray]:
        try:
            img_bytes = base64.b64decode(image_b64)
            img_array = np.frombuffer(img_bytes, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Decoded image is None.")
            return image
        except Exception as e:
            print(f"[Decode Error] {e}")
            return None

    @staticmethod
    def preprocess_image(image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Contrast stretching
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Morphological closing
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        closed = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)

        # Thresholding
        _, thresh = cv2.threshold(closed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Upscale
        upscaled = cv2.resize(thresh, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)

        # Apply sharpening after resize
        sharpening_kernel = np.array([[0, -1, 0],
                                    [-1, 5, -1],
                                    [0, -1, 0]])
        sharpened = cv2.filter2D(upscaled, -1, sharpening_kernel)

        return sharpened

    @classmethod
    def extract_text(cls, image: np.ndarray) -> Optional[str]:
        for config in cls.OCR_CONFIGS:
            text = pytesseract.image_to_string(image, config=config)
            if text.strip():
                return text
        return None

    @classmethod
    def find_expiry_date(cls, text: str) -> Optional[str]:
        for pattern in cls.EXPIRY_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def read_expiry_from_base64(self, image_b64: str) -> str:
        image = self.decode_image(image_b64)
        if image is None:
            return "Invalid image data."

        processed = self.preprocess_image(image)
        text = self.extract_text(processed)

        if not text:
            return "OCR failed to detect any text."

        expiry = self.find_expiry_date(text)
        if expiry:
            print("\n[RAW OCR TEXT]:")
            print(repr(text))
            return f"Expiration date detected: {expiry}"

        print("\n[RAW OCR TEXT]:")
        print(repr(text))
        return f"I see text, but no clear expiry date:\n{text.strip()}"

extractor = ExpiryDateExtractor()

def read_text_from_image(image_b64: str) -> str:
    return extractor.read_expiry_from_base64(image_b64)


# Example usage:
# extractor = ExpiryDateExtractor()
# result = extractor.read_expiry_from_base64(image_b64)
