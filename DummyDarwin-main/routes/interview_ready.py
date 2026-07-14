"""
Interview Ready — AI voice-screening review page.
Reads call answers from the OmniDimension-linked Google Sheet and shows
recruiters who's ready for interview scheduling, per utils/voice_screening.py.
"""

from flask import Blueprint, render_template

from utils.voice_screening import fetch_and_score

interview_ready_bp = Blueprint("interview_ready", __name__)


@interview_ready_bp.route("/interview-ready")
def index():
    candidates, error = fetch_and_score()

    counts = {"Ready for Interview": 0, "Manual Review": 0, "Not Suitable": 0, "Incomplete": 0}
    for c in candidates:
        counts[c["verdict"]] = counts.get(c["verdict"], 0) + 1

    return render_template(
        "interview_ready.html",
        candidates=candidates,
        counts=counts,
        error=error,
    )
