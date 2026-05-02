import os # Import lazmi karen warna port wala code crash ho jayega
from flask import Flask
from flask_cors import CORS
from routes.chat import chat_bp
from routes.mood import mood_bp
from routes.suggestions import suggestions_bp
from routes.health import health_bp

app = Flask(__name__)

CORS(app)

# Register Blueprints
app.register_blueprint(health_bp, url_prefix="/api")
app.register_blueprint(chat_bp, url_prefix="/api")
app.register_blueprint(mood_bp, url_prefix="/api")
app.register_blueprint(suggestions_bp, url_prefix="/api")

@app.route('/')
def home():
    return "Backend is Running!"

if __name__ == "__main__":
    # Render assignment ke liye dynamic port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)