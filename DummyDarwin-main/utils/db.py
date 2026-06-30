"""
Database initialization and SQLAlchemy instance.
Keeps the db object separate so models and routes can import it cleanly.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """
    Bind SQLAlchemy to the Flask app and create tables if they do not exist.
    Models must be imported before calling create_all().
    """
    db.init_app(app)

    with app.app_context():
        # Import models so SQLAlchemy registers the Document table
        import models.models  # noqa: F401

        db.create_all()
