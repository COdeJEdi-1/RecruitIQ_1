"""
SQLAlchemy models for the AI Recruitment Portal.
"""

from datetime import datetime, timezone

from utils.db import db


class Document(db.Model):
    """Represents an uploaded document in the JD or Candidate library."""

    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    filepath = db.Column(db.String(512), nullable=False)

    def formatted_date(self):
        """Return a human-readable upload date for templates."""
        if self.upload_date:
            return self.upload_date.strftime("%b %d, %Y · %I:%M %p")
        return "Unknown"

    def __repr__(self):
        return f"<Document {self.id}: {self.original_filename} ({self.category})>"
