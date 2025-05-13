import openai
from pyaudio import PyAudio, paInt16
from io import BytesIO
from speech_recognition import Recognizer, Microphone
from config.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def tts(response):
    player = PyAudio().open(format=paInt16, channels=1, rate=24000, output=True)
    with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=response,
        response_format="pcm"
    ) as stream:
        for chunk in stream.iter_bytes(chunk_size=1024):
            player.write(chunk)

def start_listening(callback):
    recognizer = Recognizer()
    mic = Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
    return recognizer.listen_in_background(mic, callback)

def tts_to_wav(text):
    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="wav"  
        )
        return BytesIO(response.content) 
    except Exception as e:
        print("[TTS Error]:", e)
        return None
