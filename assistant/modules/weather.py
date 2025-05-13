import re
import requests
from config.config import OPENWEATHER_API_KEY, DEFAULT_CITY


def get_weather(prompt, default_city=DEFAULT_CITY):
    api_key = OPENWEATHER_API_KEY

    if "in" in prompt.lower():
        match = re.search(r"in ([a-zA-Z\s]+)", prompt.lower())
        city = match.group(1).strip() if match else default_city
    else:
        city = default_city or get_ip_location()

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        res = requests.get(url, timeout=5).json()
        temp = res["main"]["temp"]
        desc = res["weather"][0]["description"]
        return f"The weather in {city.title()} is {temp}°C with {desc}."
    except Exception as e:
        print("DEBUG: Weather fetch error ❌")
        print(f"City: {city}")
        print(f"API_KEY valid? {'Yes' if api_key else 'No'}")
        print(f"Raw response: {res}")
        print(f"Error: {e}")
        return "Sorry, I couldn't get the weather."


def get_ip_location():
    try:
        ip_data = requests.get("https://ipapi.co/json").json()
        return ip_data["city"]
    except:
        return "London"
