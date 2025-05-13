from assistant.modules import weather

def fetch_weather(prompt: str) -> str:
    try:
        return weather.get_weather(prompt)
    except Exception as e:
        print("[Weather Controller Error]:", e)
        return "Sorry, I couldn't retrieve the weather."
