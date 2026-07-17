"""
SQLAlchemy database handle for the Darwinbox portal.

Phase 3: this is the sole runtime database module (utils/db.py was removed).
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_engine(app):
    """Bind Flask-SQLAlchemy to the Flask app."""
    db.init_app(app)
    return db
