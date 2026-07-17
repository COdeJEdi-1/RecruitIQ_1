"""
Application configuration for the AI Recruitment Portal.
Centralizes paths, database settings, and upload constraints.

Phase 3: MySQL ('recruitiq') is the default runtime URI. Set USE_SQLITE=true
in .env to fall back to the local SQLite file.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _build_mysql_uri() -> str:
    host = os.environ.get("MYSQL_HOST", "127.0.0.1")
    port = os.environ.get("MYSQL_PORT", "3306")
    user = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    database = os.environ.get("MYSQL_DATABASE", "recruitiq")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


def _database_uri() -> str:
    """
    Prefer explicit DATABASE_URL.
    Phase 3: MySQL is the default backing store. Set USE_SQLITE=true to fall
    back to the local SQLite file (e.g. for offline development).
    """
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    use_sqlite = os.environ.get("USE_SQLITE", "false").lower() in ("1", "true", "yes")
    if use_sqlite:
        return f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"

    return _build_mysql_uri()


class Config:
    """Flask application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # MySQL settings (used unless USE_SQLITE=true)
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "recruitiq")

    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # Physical upload directories (existing runtime paths — unchanged in Phase 2)
    UPLOAD_FOLDER_JD = os.path.join(BASE_DIR, "static", "uploads", "jd")
    UPLOAD_FOLDER_CANDIDATE = os.path.join(BASE_DIR, "static", "uploads", "candidates")

    # Architecture target upload roots (Phase 3 may switch paths here)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    UPLOAD_FOLDER_RESUMES = os.path.join(BASE_DIR, "uploads", "resumes")

    # Maximum upload size (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Allowed file extensions (lowercase)
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt"}
    ALLOWED_EXTENSIONS_CANDIDATE = ALLOWED_EXTENSIONS | {"xls", "xlsx"}

    # Category constants for document library
    CATEGORY_JD = "jd"
    CATEGORY_CANDIDATE = "candidate"

    PORT = int(os.environ.get("PORT", "6002"))
