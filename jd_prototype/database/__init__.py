"""Database package — MySQL infrastructure via SQLAlchemy (Phase 2 scaffold)."""

from database.db import db, init_engine
from database.init_db import init_db

__all__ = ["db", "init_engine", "init_db"]
