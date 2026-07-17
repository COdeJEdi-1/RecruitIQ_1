"""
Initialize MySQL schema for the JD Generator.

Usage:
  python -m database.init_db

Phase 2: creates tables from models. Does not migrate data or touch Supabase.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure package root is on path when run as `python -m database.init_db`
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def init_db(app=None):
    """
    Bind SQLAlchemy and create all tables.

    If app is None, builds a minimal Flask app from Config.
    """
    from flask import Flask

    from config import Config
    from database.db import db, init_engine

    owns_app = app is None
    if owns_app:
        app = Flask(__name__)
        app.config.from_object(Config)

    init_engine(app)

    # Import models so metadata is registered
    import database.models  # noqa: F401

    with app.app_context():
        db.create_all()
        print(f"[init_db] Tables ensured for URI host={app.config.get('MYSQL_HOST')} "
              f"db={app.config.get('MYSQL_DATABASE')}")

    return app


def main():
    from dotenv import load_dotenv

    load_dotenv()
    try:
        init_db()
        print("[init_db] Success.")
    except Exception as exc:
        print(f"[init_db] Failed (MySQL must be reachable when running this script): {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
