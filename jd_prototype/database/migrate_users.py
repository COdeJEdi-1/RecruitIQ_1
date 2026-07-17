"""
One-time migration: import darwin_data/users.json records into the MySQL
`users` table (User model).

Usage:
  python -m database.migrate_users

Idempotent — safe to re-run; existing rows (matched by id/user_id) are updated
in place rather than duplicated.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_USERS_FILE = _ROOT / "darwin_data" / "users.json"


def _load_users_json() -> list:
    try:
        return json.loads(_USERS_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[migrate_users] Could not read {_USERS_FILE}: {exc}")
        return []


def migrate(app=None) -> dict:
    from flask import Flask

    from config import Config
    from database.db import db, init_engine
    from database.models import User

    owns_app = app is None
    if owns_app:
        app = Flask(__name__)
        app.config.from_object(Config)
    init_engine(app)

    imported, updated, skipped = 0, 0, 0

    with app.app_context():
        db.create_all()

        users = _load_users_json()
        for u in users:
            email = (u.get("email") or "").strip().lower()
            if not email:
                skipped += 1
                continue

            row = User.query.get(u.get("user_id")) or User.query.filter_by(email=email).first()
            if row is None:
                row = User(id=u.get("user_id"), email=email)
                db.session.add(row)
                imported += 1
            else:
                updated += 1

            row.username = u.get("username")
            row.email = email
            row.password_hash = u.get("password_hash")
            row.full_name = u.get("full_name")
            row.role = u.get("role", "user")
            row.auth_provider = "local"

        db.session.commit()

    print(f"[migrate_users] imported={imported} updated={updated} skipped={skipped} "
          f"(source: {_USERS_FILE})")
    return {"imported": imported, "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    migrate()
