"""
Dashboard blueprint — main portal view with statistics and document lists.
Data is scoped by role: admin sees all; user sees only their own (created_by).
"""

import os
import sys

from flask import Blueprint, render_template, session, redirect, url_for

from config import Config
from database.models import (
    ActivityLog,
    Candidate,
    CandidateScore,
    DarwinboxJob,
    Document,
    DownloadRequest,
    User,
)
from routes.auth import login_required, is_admin, current_user_id
from utils.helpers import import_isolated

dashboard_bp = Blueprint("dashboard", __name__)

_JD_PROTOTYPE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "jd_prototype")

# Appended (not prepended) so this app's own same-named packages
# (utils, database, config, ...) keep resolving to themselves everywhere
# else in this process; jd_prototype is only a fallback for names unique
# to it, like `scoring_service`/`jd_constants`.
if _JD_PROTOTYPE_DIR not in sys.path:
    sys.path.append(_JD_PROTOTYPE_DIR)

# scoring_service.py (jd_prototype) transitively imports its OWN
# `database.models` (bound to its own SQLAlchemy instance). Isolated so it
# doesn't collide with this file's `database.models` import above — see
# import_isolated()'s docstring for why a plain `from scoring_service
# import ...` here would otherwise break.
AUTO_CALL_SCORE_THRESHOLD, MANUAL_CALL_SCORE_THRESHOLD = import_isolated(
    "scoring_service",
    ("AUTO_CALL_SCORE_THRESHOLD", "MANUAL_CALL_SCORE_THRESHOLD"),
    _JD_PROTOTYPE_DIR,
)

# Score is 0-100 internally, shown to users as /10. Tier boundaries below are
# in the internal 0-100 scale (90 -> 9.0/10, 70 -> 7.0/10).
SCORE_THRESHOLDS = {"green": AUTO_CALL_SCORE_THRESHOLD, "yellow": MANUAL_CALL_SCORE_THRESHOLD}


def _load_shared_context():
    admin = is_admin()
    uid   = current_user_id()

    all_jds    = [j.to_dict() for j in DarwinboxJob.query.filter_by(is_active=True).all()]
    all_cands  = [c.to_dict() for c in Candidate.query.all()]
    scores_raw = [s.to_dict() for s in CandidateScore.query.all()]

    # Scope data for non-admin: only rows they created
    if admin:
        ai_jds     = all_jds
        candidates = all_cands
    else:
        ai_jds     = [j for j in all_jds if j.get("created_by") == uid]
        # Candidates: only those who applied to jobs this user owns
        owned_job_ids = {j["darwinbox_job_id"] for j in ai_jds}
        candidates    = [c for c in all_cands if c.get("darwinbox_job_id") in owned_job_ids]

    score_map     = {s["candidate_id"]: s for s in scores_raw}
    job_map       = {j["darwinbox_job_id"]: j["role_title"] for j in all_jds}
    threshold_map = {
        j["darwinbox_job_id"]: j.get("shortlist_threshold")
        if j.get("shortlist_threshold") is not None else 70
        for j in all_jds
    }

    # User map for admin "created by" display
    user_map = {}
    try:
        for u in User.query.all():
            ud = u.to_dict()
            user_map[ud["user_id"]] = ud.get("full_name") or ud.get("username", ud["user_id"])
    except Exception:
        pass

    # Activity log — admin only
    activity_log = []
    if admin:
        rows = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(50).all()
        activity_log = [a.to_dict() for a in rows]

    return {
        "admin": admin,
        "uid": uid,
        "ai_jds": ai_jds,
        "candidates": candidates,
        "score_map": score_map,
        "job_map": job_map,
        "threshold_map": threshold_map,
        "user_map": user_map,
        "activity_log": activity_log,
    }


@dashboard_bp.route("/")
def index():
    ctx = _load_shared_context()
    ai_jds     = ctx["ai_jds"]
    candidates = ctx["candidates"]

    stats = {
        "jd_count":        len(ai_jds),
        "candidate_count": len(candidates),
        "total_count":     len(ai_jds) + len(candidates),
    }

    # Download request counts for admin badge
    pending_download_count = 0
    try:
        pending_download_count = DownloadRequest.query.filter_by(status="pending").count()
    except Exception:
        pass

    return render_template(
        "dashboard.html",
        stats=stats,
        ai_jds=ai_jds,
        candidates=candidates,
        job_map=ctx["job_map"],
        score_map=ctx["score_map"],
        threshold_map=ctx["threshold_map"],
        score_thresholds=SCORE_THRESHOLDS,
        is_admin=ctx["admin"],
        user_map=ctx["user_map"],
        pending_download_count=pending_download_count,
    )


@dashboard_bp.route("/shortlisted")
def shortlisted():
    ctx = _load_shared_context()
    return render_template(
        "shortlisted.html",
        candidates=ctx["candidates"],
        score_map=ctx["score_map"],
        job_map=ctx["job_map"],
        is_admin=ctx["admin"],
        user_map=ctx["user_map"],
        activity_log=ctx["activity_log"],
        score_thresholds=SCORE_THRESHOLDS,
    )
