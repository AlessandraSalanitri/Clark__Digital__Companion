import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Default city for get the weather
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "London")

# Demo Amazon credentials
DEMO_AMAZON_EMAIL = os.getenv("DEMO_AMAZON_EMAIL")
DEMO_AMAZON_PASSWORD = os.getenv("DEMO_AMAZON_PASSWORD")


# Check for missing keys
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env")
if not OPENWEATHER_API_KEY:
    raise ValueError("Missing OPENWEATHER_API_KEY in .env")
if not DEMO_AMAZON_EMAIL:
    raise ValueError("Missing Amazon Email in .env")
if not DEMO_AMAZON_PASSWORD:
    raise ValueError("Missing FakePassword in .env")