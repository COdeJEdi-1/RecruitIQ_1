"""
Dashboard blueprint — main portal view with statistics and document lists.
Data is scoped by role: admin sees all; user sees only their own (created_by).
"""

import os
import sys
from datetime import datetime

from flask import Blueprint, jsonify, render_template, session, redirect, url_for

from config import Config
from database.db import db
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
from utils.voice_screening import fetch_call_results_by_phone, _phone_last10

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


def _name_match_tier(sheet_name, candidate_name):
    """0 = no match, 1 = one name is a case-insensitive prefix of the other
    ('Kashish' vs 'Kashish Bhagat'), 2 = exact (case-insensitive). Exact
    ranks above prefix because this sheet's test phone numbers are
    sometimes shared between two of OUR OWN distinct candidates (e.g. both
    'Chahat' and 'Chahat Dholakia' are real, different candidates on the
    same number) — an exact name hit disambiguates that case; a bare prefix
    match can't. A blank/placeholder sheet name never counts as a match."""
    a = (sheet_name or "").strip().lower()
    b = (candidate_name or "").strip().lower()
    if not a or not b:
        return 0
    if a == b:
        return 2
    if a.startswith(b) or b.startswith(a):
        return 1
    return 0


def _call_info_for_candidate(call_results, candidate):
    """Phone-match a candidate against the call-results sheet.

    Test/demo phone numbers in this sheet are reused across many different
    named candidates (confirmed against real data: one number alone logged
    calls under half a dozen different names over several weeks). Naively
    taking "the most recent call to this number" would silently attribute a
    completely different person's call to this candidate — so among the
    calls to this phone, we prefer the most recent one whose OWN
    candidate_name matches this candidate's name (exact match preferred
    over a loose prefix match — see _name_match_tier()), and only fall back
    to "most recent regardless of name" when the sheet never captured a
    matching name for this phone at all. Each per-phone list from
    fetch_call_results_by_phone() is already sorted most-recent-first.

    A genuine name match is trusted completely over the applied_at
    date-guard: real data showed a candidate's own true, well-scored call
    can predate our internal (test) applied_at timestamp, which would
    otherwise reject a correct match. Within a matched name-tier we instead
    prefer their most recent call that actually completed (a real verdict)
    over their most recent call period, since that may just be a short
    retry. The date-guard remains the sole protection when there's no name
    match at all (pure phone-only fallback, where a stale reused-number
    match is a real risk).

    Logs both failure modes (no phone match at all / every unnamed call on
    this phone rejected by the date-guard) so a "why isn't this candidate
    showing up as called?" question is answerable from the server log
    instead of requiring a one-off debugging script."""
    if not call_results:
        return None
    last10 = _phone_last10(candidate.get("phone"))
    if not last10:
        return None
    calls = call_results.get(last10)
    if not calls:
        print(
            f"[call-match] no match for {candidate.get('name')!r} "
            f"(phone={candidate.get('phone')!r} -> last10={last10!r}); "
            f"{len(call_results)} phone(s) in sheet: {sorted(call_results.keys())}",
            flush=True,
        )
        return None

    applied_at_str = candidate.get("applied_at")
    applied_dt = None
    if applied_at_str:
        try:
            applied_dt = datetime.fromisoformat(applied_at_str)
        except ValueError:
            pass  # unparseable timestamp — don't let a bad date silently hide a real match

    def date_ok(call):
        if not applied_dt:
            return True
        try:
            return datetime.fromisoformat(call.get("call_date") or "") >= applied_dt
        except ValueError:
            return True  # unparseable call_date — don't let it silently hide a real match

    tiers = {}
    for call in calls:
        tiers.setdefault(_name_match_tier(call.get("name"), candidate.get("name")), []).append(call)

    for tier in (2, 1):
        if tier not in tiers:
            continue
        # A name match already confirms identity, so the applied_at
        # date-guard adds nothing here — apply it and real data showed it
        # rejecting a candidate's own genuine, well-scored call in favor of
        # a same-person short retry that merely happened to land after
        # their (test) applied_at. Prefer their most recent call that
        # actually completed (a real verdict) over their most recent call
        # period, which may just be a short retry; only fall back to "most
        # recent regardless" if every one of their own calls was Incomplete.
        this_tier = tiers[tier]
        real_verdicts = [c for c in this_tier if c.get("verdict") != "Incomplete"]
        return (real_verdicts or this_tier)[0]

    # No sheet call ever captured a matching name for this phone — pure
    # phone-only fallback, where the date-guard is the only protection
    # against a stale reused-number match.
    eligible = [c for c in tiers.get(0, []) if date_ok(c)]
    if not eligible:
        print(
            f"[call-match] rejected for {candidate.get('name')!r}: "
            f"every one of {len(calls)} call(s) on this phone predates their applied_at "
            f"(and none matched by name)",
            flush=True,
        )
        return None
    return eligible[0]


def _group_rows_by_role(rows, job_map):
    """Groups already-sorted (score, candidate, ...) row tuples by their
    darwinbox_job_id into per-role tables, ranked within each role group
    (rank #1 = best score in that specific role's own applicant pool, not a
    global rank across every role).

    `rows` must already be sorted the way the caller wants candidates ordered
    overall — group membership never reorders that, it just buckets by role
    while preserving relative order, so each group naturally comes out
    sorted too. Tuple shape is (score, candidate, *rest) — `rest` may be
    empty (ranking), or (sc,) / (sc, call_info) depending on the caller — each
    element is copied into the row dict under the given key. Shared by
    ranking(), pre_calling(), and post_calling() so the role/rowspan grouping
    exists in exactly one place instead of three near-identical Jinja
    namespace/rowspan blocks."""
    grouped = {}
    order = []
    for row in rows:
        c = row[1]
        jid = c["darwinbox_job_id"]
        if jid not in grouped:
            grouped[jid] = []
            order.append(jid)
        grouped[jid].append(row)

    groups = []
    for jid in order:
        ranked = []
        for i, row in enumerate(grouped[jid], start=1):
            score, c, *rest = row
            entry = {"rank": i, "score": score, "candidate": c}
            if len(rest) >= 1:
                entry["sc"] = rest[0]
            if len(rest) >= 2:
                entry["call_info"] = rest[1]
            ranked.append(entry)
        groups.append({"role": job_map.get(jid, "Unknown"), "job_id": jid, "rows": ranked})
    return groups


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
    req_id_map    = {j["darwinbox_job_id"]: j.get("jd_id") for j in all_jds}
    threshold_map = {
        j["darwinbox_job_id"]: j.get("shortlist_threshold")
        if j.get("shortlist_threshold") is not None else 70
        for j in all_jds
    }
    position_level_map = {
        j["darwinbox_job_id"]: j.get("position_level", "junior") for j in all_jds
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
        "logged_in": uid is not None,
        "ai_jds": ai_jds,
        "candidates": candidates,
        "score_map": score_map,
        "job_map": job_map,
        "req_id_map": req_id_map,
        "threshold_map": threshold_map,
        "position_level_map": position_level_map,
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
        "library.html",
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
        activity_log=ctx["activity_log"],
    )


@dashboard_bp.route("/darwin-resumes")
def darwin_resumes():
    """Read-only feed of every (access-scoped) candidate — the eventual landing
    spot for resumes pushed directly from Darwin's own webhook. For now every
    row in `candidates` is shown here, since Darwin isn't wired up yet and
    everything currently arrives via LinkedIn/Naukri."""
    ctx = _load_shared_context()
    candidates = sorted(ctx["candidates"], key=lambda c: c.get("applied_at") or "", reverse=True)
    return render_template(
        "darwin_resumes.html",
        candidates=candidates,
        job_map=ctx["job_map"],
        logged_in=ctx["logged_in"],
    )


@dashboard_bp.route("/ranking")
def ranking():
    ctx = _load_shared_context()
    candidates = ctx["candidates"]
    score_map = ctx["score_map"]
    job_map = ctx["job_map"]

    rows = []
    for c in candidates:
        sc = score_map.get(c["candidate_id"])
        overall = sc["overall_score"] if (sc and sc.get("overall_score") is not None) else None
        rows.append((overall, c, sc))
    rows.sort(key=lambda row: (row[0] is None, -(row[0] or 0)))

    groups = _group_rows_by_role(rows, job_map)

    return render_template(
        "ranking.html",
        groups=groups,
        job_map=job_map,
        threshold_map=ctx["threshold_map"],
        score_thresholds=SCORE_THRESHOLDS,
        is_admin=ctx["admin"],
        logged_in=ctx["logged_in"],
        user_map=ctx["user_map"],
    )


@dashboard_bp.route("/pre-calling")
def pre_calling():
    """The calling queue — every scored candidate, tagged with whether they've
    been called yet (and if so, whether that call was auto- or manually-
    triggered, and whether it was actually answered), phone-matched via
    fetch_call_results_by_phone()."""
    ctx = _load_shared_context()
    candidates = ctx["candidates"]
    score_map = ctx["score_map"]

    call_results, call_error = fetch_call_results_by_phone()

    rows = []
    for c in candidates:
        sc = score_map.get(c["candidate_id"])
        if not sc or sc.get("overall_score") is None:
            continue
        call_info = _call_info_for_candidate(call_results, c)
        rows.append((sc["overall_score"], c, sc, call_info))
    rows.sort(key=lambda row: row[0], reverse=True)

    groups = _group_rows_by_role(rows, ctx["job_map"])

    return render_template(
        "pre_calling.html",
        groups=groups,
        job_map=ctx["job_map"],
        position_level_map=ctx["position_level_map"],
        score_thresholds=SCORE_THRESHOLDS,
        is_admin=ctx["admin"],
        logged_in=ctx["logged_in"],
        call_error=call_error,
    )


@dashboard_bp.route("/post-calling")
def post_calling():
    """Candidates who have already been called — phone-matched against the
    OmniDimension call-results sheet via the same fetch_call_results_by_phone()
    join used by pre_calling()'s exclusion check. Flat, sorted by JD-match
    score (not grouped by role) — role/REQ ID is shown as subtext under the
    candidate's name instead, matching the Interview Ready table design."""
    ctx = _load_shared_context()
    candidates = ctx["candidates"]
    score_map = ctx["score_map"]
    job_map = ctx["job_map"]
    req_id_map = ctx["req_id_map"]

    call_results, call_error = fetch_call_results_by_phone()

    rows = []
    for c in candidates:
        call_info = _call_info_for_candidate(call_results, c)
        if not call_info:
            continue
        sc = score_map.get(c["candidate_id"])
        overall = sc["overall_score"] if (sc and sc.get("overall_score") is not None) else None
        job_id = c.get("darwinbox_job_id")
        rows.append({
            "candidate": c,
            "sc": sc,
            "score": overall,
            "call_info": call_info,
            "role": job_map.get(job_id, "Unknown Role"),
            "req_id": req_id_map.get(job_id),
        })
    rows.sort(key=lambda row: (row["score"] is None, -(row["score"] or 0)))

    answered_count = sum(1 for row in rows if row["call_info"]["verdict"] != "Incomplete")
    call_counts = {
        "total": len(rows),
        "answered": answered_count,
        "no_answer": len(rows) - answered_count,
    }

    verdict_counts = {}
    scores_for_avg = []
    for row in rows:
        verdict = row["call_info"]["verdict"]
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        if row["call_info"].get("score") is not None:
            scores_for_avg.append(row["call_info"]["score"])
    analytics = {
        "verdict_counts": verdict_counts,
        "avg_score": round(sum(scores_for_avg) / len(scores_for_avg), 1) if scores_for_avg else None,
        "analysed_count": len(scores_for_avg),
    }

    roles = sorted({row["role"] for row in rows if row["role"]})

    return render_template(
        "post_calling.html",
        rows=rows,
        roles=roles,
        call_counts=call_counts,
        analytics=analytics,
        score_thresholds=SCORE_THRESHOLDS,
        is_admin=ctx["admin"],
        logged_in=ctx["logged_in"],
        call_error=call_error,
    )


@dashboard_bp.route("/api/candidates/<candidate_id>/mark-called", methods=["POST"])
def mark_candidate_called(candidate_id):
    """Records that a manual call was just triggered for this candidate —
    independent of whether the call has actually connected/completed yet, so
    Pre-Calling can show "Call Triggered" immediately instead of waiting for
    the OmniDimension sheet to sync a result. Idempotent: safe to call again
    (e.g. a retried dispatch) — just refreshes the timestamp."""
    candidate = Candidate.query.get(candidate_id)
    if candidate is None:
        return jsonify({"error": "Candidate not found"}), 404
    candidate.manual_call_triggered_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"success": True, "candidate_id": candidate_id})
