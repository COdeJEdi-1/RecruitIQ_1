"""
Application configuration for the AI Recruitment Portal.
Centralizes paths, database settings, and upload constraints.
"""

import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Flask application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # SQLite database
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Physical upload directories
    UPLOAD_FOLDER_JD = os.path.join(BASE_DIR, "static", "uploads", "jd")
    UPLOAD_FOLDER_CANDIDATE = os.path.join(BASE_DIR, "static", "uploads", "candidates")

    # Maximum upload size (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Allowed file extensions (lowercase)
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt"}
    ALLOWED_EXTENSIONS_CANDIDATE = ALLOWED_EXTENSIONS | {"xls", "xlsx"}

    # Category constants for document library
    CATEGORY_JD = "jd"
    CATEGORY_CANDIDATE = "candidate"
