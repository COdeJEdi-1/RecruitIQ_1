"""
Dashboard blueprint — main portal view with statistics and document lists.
"""

from flask import Blueprint, render_template

from config import Config
from models.models import Document

dashboard_bp = Blueprint("dashboard", __name__)


def _get_library_stats():
    """Calculate document counts for the statistics section."""
    jd_count = Document.query.filter_by(category=Config.CATEGORY_JD).count()
    candidate_count = Document.query.filter_by(
        category=Config.CATEGORY_CANDIDATE
    ).count()
    total_count = Document.query.count()

    return {
        "jd_count": jd_count,
        "candidate_count": candidate_count,
        "total_count": total_count,
    }


@dashboard_bp.route("/")
def index():
    """Render the Document Library dashboard."""
    stats = _get_library_stats()

    jd_documents = (
        Document.query.filter_by(category=Config.CATEGORY_JD)
        .order_by(Document.upload_date.desc())
        .all()
    )

    candidate_documents = (
        Document.query.filter_by(category=Config.CATEGORY_CANDIDATE)
        .order_by(Document.upload_date.desc())
        .all()
    )

    return render_template(
        "dashboard.html",
        stats=stats,
        jd_documents=jd_documents,
        candidate_documents=candidate_documents,
    )
