🤖 Clark - Your Digital Assistant
Clark is a voice-enabled virtual assistant designed to help visually impaired users. It supports natural conversations, camera-based perception (OCR, scene analysis, crossing detection), and real-time visual feedback, for demo purposes enhanced with animated mouth movements synced to speech.

📦 Features:

🎙️ Voice recognition via browser mic (Web Speech API)

🧠 Natural language understanding (OpenAI / LangChain)

🧾 OCR + object recognition via webcam

📷 Real-time camera feedback

🛒 Smart follow-ups for web, Amazon, and calendar

👄 Lip-synced animated avatar (viseme-driven)

💬 Text-to-speech response with synchronized mouth movements


# 1 . clone the repository
    git clone https://github.com/AlessandraSalanitri/Clark_DigitalCompanion.git

# 2. Create virtual environment
python -m venv .venv

# 3. Activate (Windows PowerShell)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt
pip install selenium webdriver-manager beautifulsoup4

# 5. Just for run the program easily, I have left the .env file for you with:
OPENWEATHER_API_KEY =my key
DEFAULT_CITY= London
and fake credentials for amazon accounts
# Please Add:
`OPENAI_API_KEY=your-key-here

# 6. Run the app
python app.py
