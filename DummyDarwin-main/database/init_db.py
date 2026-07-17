"""
Initialize database schema for the Darwinbox portal.

Usage:
  python -m database.init_db

Creates tables from database.models. MySQL is the default runtime store;
set USE_SQLITE=true in .env to fall back to the local SQLite file instead.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _redact_uri(uri: str) -> str:
    """Mask the password in a DB URI for safe logging (behavior is unaffected —
    the real URI is still what's passed to SQLAlchemy; this only touches what
    gets printed)."""
    return re.sub(r"(://[^:/@]+:)[^@]*(@)", r"\1***\2", uri or "")


def init_db(app=None):
    """Bind SQLAlchemy and create all tables for the architecture database package."""
    from flask import Flask

    from config import Config
    from database.db import db, init_engine

    if app is None:
        app = Flask(__name__)
        app.config.from_object(Config)

    init_engine(app)

    import database.models  # noqa: F401

    with app.app_context():
        db.create_all()
        safe_uri = _redact_uri(app.config.get("SQLALCHEMY_DATABASE_URI", ""))
        print(f"[init_db] Tables ensured for: {safe_uri[:64]}...")

    return app


def main():
    try:
        init_db()
        print("[init_db] Success.")
    except Exception as exc:
        print(f"[init_db] Failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
