from threading import Thread, Lock
import cv2
import base64
import time


class WebcamStream:
    def __init__(self):
        self.stream = None
        self.lock = Lock()
        self.frame = None
        self.running = False

    def start(self):
        if self.running:
            return self
        self.stream = cv2.VideoCapture(0)
        _, self.frame = self.stream.read()
        self.running = True
        Thread(target=self.update).start()
        return self

    def update(self):
        while self.running:
            _, frame = self.stream.read()
            with self.lock:
                self.frame = frame


    def read(self, encode=False, for_ui=False):
        with self.lock:
            if self.frame is None:
                return None
            frame = self.frame.copy()

        # Encode frame as JPEG
        ret, buffer = cv2.imencode(".jpeg", frame)
        if not ret:
            return None

        # Return base64
        if encode:
            b64_bytes = base64.b64encode(buffer)  # always bytes
            return b64_bytes.decode("utf-8") if for_ui else b64_bytes

        # Raw image bytes (e.g., for display or OpenCV)
        return buffer.tobytes()

    
    
    # def read(self, encode=False):
    #     with self.lock:
    #         if self.frame is None:
    #             return None
    #         frame = self.frame.copy()

    #     if encode:
    #         _, buffer = cv2.imencode(".jpeg", frame)
    #         return base64.b64encode(buffer)

    #     return frame

    def stop(self):
        self.running = False
        time.sleep(0.2)  # exit gracefully

        if self.stream is not None:
            self.stream.release()
            self.stream = None
            
        self.frame = None
