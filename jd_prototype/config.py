"""
Application configuration for the JD Generator backend.
MySQL via SQLAlchemy. Credentials loaded from environment / .env.
Phase 2 scaffold — not yet wired into app.py route logic.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def _build_mysql_uri() -> str:
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "recruitiq")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


class Config:
    """Flask / SQLAlchemy configuration."""

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-please-change-in-production")

    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "recruitiq")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or _build_mysql_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # Paths (architecture uploads/ — Phase 3 may switch runtime from static/uploads)
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    UPLOAD_FOLDER_RESUMES = str(BASE_DIR / "uploads" / "resumes")

    # Existing env keys preserved for Phase 3 wiring (unused by this Phase 2 scaffold)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    COMPANY_NAME = os.getenv("COMPANY_NAME", "Arvind GCC")
    ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "")
    DEV_MODE = os.getenv("DEV_MODE", "false").lower() in ("1", "true", "yes")
    PORT = int(os.getenv("PORT", "6001"))
