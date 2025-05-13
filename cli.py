import time
import cv2
from audio.voice import start_listening, tts
from controllers.voice_loop import clark_audio_callback
from camera.webcam import WebcamStream

tts("Hey, what can I do for you?")

try:
    start_listening(clark_audio_callback)
except OSError as e:
    print("Mic error:", e)
    tts("Could not access the microphone.")

webcam = WebcamStream()

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
