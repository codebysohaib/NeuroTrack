from flask import Flask
from flask_cors import CORS
from routes.chat import chat_bp
from routes.mood import mood_bp
from routes.suggestions import suggestions_bp
from routes.health import health_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register Blueprints
app.register_blueprint(health_bp, url_prefix="/api")
app.register_blueprint(chat_bp, url_prefix="/api")
app.register_blueprint(mood_bp, url_prefix="/api")
app.register_blueprint(suggestions_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
