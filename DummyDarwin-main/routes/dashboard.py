"""
Dashboard blueprint — main portal view with statistics and document lists.
Data is scoped by role: admin sees all; user sees only their own (created_by).
"""

import json
import os
import sys

from flask import Blueprint, render_template, session, redirect, url_for

from config import Config
from models.models import Document
from routes.auth import login_required, is_admin, current_user_id

dashboard_bp = Blueprint("dashboard", __name__)

_JD_PROTOTYPE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "jd_prototype")
DARWIN_DATA = os.path.join(_JD_PROTOTYPE_DIR, "darwin_data")
DARWIN_JOBS_FILE       = os.path.join(DARWIN_DATA, "darwinbox_jobs.json")
DARWIN_CANDIDATES_FILE = os.path.join(DARWIN_DATA, "candidates.json")
DARWIN_SCORES_FILE     = os.path.join(DARWIN_DATA, "candidate_scores.json")
DARWIN_ACTIVITY_FILE   = os.path.join(DARWIN_DATA, "activity_log.json")

if _JD_PROTOTYPE_DIR not in sys.path:
    sys.path.insert(0, _JD_PROTOTYPE_DIR)

from scoring_service import AUTO_CALL_SCORE_THRESHOLD, MANUAL_CALL_SCORE_THRESHOLD  # noqa: E402

# Score is 0-100 internally, shown to users as /10. Tier boundaries below are
# in the internal 0-100 scale (90 -> 9.0/10, 70 -> 7.0/10).
SCORE_THRESHOLDS = {"green": AUTO_CALL_SCORE_THRESHOLD, "yellow": MANUAL_CALL_SCORE_THRESHOLD}


def _load_file(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def _load_candidates():
    try:
        with open(DARWIN_CANDIDATES_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def _load_shared_context():
    admin = is_admin()
    uid   = current_user_id()

    all_jds     = [j for j in _load_file(DARWIN_JOBS_FILE) if j.get("is_active")]
    all_cands   = _load_candidates()
    scores_raw  = _load_file(DARWIN_SCORES_FILE)

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
    threshold_map = {j["darwinbox_job_id"]: j.get("shortlist_threshold", 70) for j in all_jds}

    # User map for admin "created by" display
    user_map = {}
    try:
        import json as _j
        from pathlib import Path
        uf = Path(DARWIN_DATA) / "users.json"
        for u in _j.loads(uf.read_text()):
            user_map[u["user_id"]] = u.get("full_name") or u.get("username", u["user_id"])
    except Exception:
        pass

    # Activity log — admin only
    activity_log = []
    if admin:
        activity_log = list(reversed(_load_file(DARWIN_ACTIVITY_FILE)))[:50]

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
    import json as _json
    from pathlib import Path as _Path
    pending_download_count = 0
    try:
        reqs_file = _Path(DARWIN_DATA) / "download_requests.json"
        reqs = _json.loads(reqs_file.read_text()) if reqs_file.exists() else []
        pending_download_count = sum(1 for r in reqs if r.get("status") == "pending")
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
