"""
AI Recruitment Portal — Application entry point.

Modular Flask application designed as middleware for multiple
AI recruitment modules. This module implements the Document Library.
"""

import os

from flask import Flask

from config import Config
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.downloads import downloads_bp
from routes.interview_ready import interview_ready_bp
from routes.platforms import platforms_bp
from routes.upload import upload_bp
from utils.db import init_db


def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload directories exist on startup
    os.makedirs(Config.UPLOAD_FOLDER_JD, exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER_CANDIDATE, exist_ok=True)

    # Initialize database and create tables if needed
    init_db(app)

    # Register modular blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(downloads_bp)
    app.register_blueprint(interview_ready_bp)
    app.register_blueprint(platforms_bp)
    app.register_blueprint(upload_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002, use_reloader=False)
