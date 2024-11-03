# Initializes the Flask app
from flask import Flask
from .routes import main as main_blueprint
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register the main blueprint for routes
    app.register_blueprint(main_blueprint)

    return app
