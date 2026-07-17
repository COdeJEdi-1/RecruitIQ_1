"""
SQLAlchemy database handle for the JD Generator. Wired into app.py at
startup and used throughout services/, routes, and database/models.py.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_engine(app):
    """Bind Flask-SQLAlchemy to the Flask app."""
    db.init_app(app)
    return db
