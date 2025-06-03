from flask import Flask, render_template
from extensions.socket import socketio

from routes.voice_routes import voice_bp
from routes.webcam_routes import webcam_bp
from routes.assistant_routes import assistant_bp
from routes.intent_routes import intent_bp
from routes.logger_routes import logger_bp
from routes.web_routes import web_bp
from routes.weather_routes import weather_bp
from routes.train_routes import train_bp
from routes.time_routes import time_bp
from routes.ocr_routes import ocr_bp
from routes.crossing_routes import crossing_bp
from routes.calendar_routes import calendar_bp

app = Flask(__name__)

socketio.init_app(app, cors_allowed_origins="*")

######### BLUEPRINTS #########

app.register_blueprint(intent_bp) # INTENT 
app.register_blueprint(assistant_bp, url_prefix="/assistant") # CLARK BRAIN


app.register_blueprint(voice_bp) # VOICE
app.register_blueprint(webcam_bp) # WEBCAM 
app.register_blueprint(logger_bp) # LOGGER

######### MODULES FEATURES #########
app.register_blueprint(web_bp, url_prefix="/web") # BROWSING
app.register_blueprint(train_bp, url_prefix="/train") # TRAIN TICKETS BROWSE
app.register_blueprint(weather_bp, url_prefix="/weather") # WEATHER
app.register_blueprint(time_bp, url_prefix="/time") # TIME
app.register_blueprint(ocr_bp, url_prefix="/ocr") # OCR 
app.register_blueprint(crossing_bp, url_prefix="/crossing") # CROSSING STREET


######### CALENDAR REMINDER- NOTIFICATION #########
app.register_blueprint(calendar_bp, url_prefix="/calendar")


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, debug=True)
