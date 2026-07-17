"""
SQLAlchemy/MySQL data-access layer for the JD Generator.

Phase 3: replaces supabase_db.py. Same public function names/signatures/return
shapes as supabase_db.py so callers in app.py only need an import swap.

Every function is best-effort and swallows exceptions (matching the original
supabase_db.py contract) so a transient DB hiccup never breaks the
filesystem-based fallback that some app.py routes still use.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from database.db import db
from database.models import JdEditDiff, JdFeedback, KbVersion, UserJd, UserProfile


def _iso(dt) -> str:
    if dt is None:
        return ""
    return dt.isoformat()


def _jd_to_dict(row: UserJd) -> dict:
    return {
        "id": row.id,
        "generation_id": row.generation_id,
        "user_email": row.user_email,
        "role_title": row.role_title,
        "department": row.department,
        "division": row.division,
        "family": row.family,
        "yoe_band": row.yoe_band,
        "focus_areas": row.focus_areas,
        "original_text": row.original_text,
        "final_text": row.final_text,
        "status": row.status,
        "edit_ratio": row.edit_ratio,
        "jd_ref": row.jd_ref,
        "approved_at": _iso(row.approved_at),
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def _profile_to_dict(row: UserProfile) -> dict:
    return {
        "id": row.id,
        "email": row.email,
        "full_name": row.full_name,
        "role": row.role,
        "avatar_url": row.avatar_url,
        "jd_count": row.jd_count,
        "last_active": _iso(row.last_active),
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


# ── user_jds ─────────────────────────────────────────────────────────────────

def save_draft(
    generation_id: str,
    user_email: str,
    role_title: str,
    department: str,
    division: str,
    family: str,
    yoe_band: str,
    focus_areas: str,
    original_text: str,
) -> bool:
    """Insert or update a draft JD row (status='draft'). Returns True on success."""
    try:
        row = UserJd.query.filter_by(generation_id=generation_id).first()
        if row is None:
            row = UserJd(generation_id=generation_id)
            db.session.add(row)
        row.user_email = user_email
        row.role_title = role_title
        row.department = department
        row.division = division or ""
        row.family = family
        row.yoe_band = yoe_band
        row.focus_areas = focus_areas or ""
        row.original_text = original_text
        row.status = "draft"
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def approve_draft(generation_id: str, final_text: str, jd_ref: str, edit_ratio: float) -> bool:
    """Update a draft row to approved status with the final edited text."""
    try:
        row = UserJd.query.filter_by(generation_id=generation_id).first()
        if row is None:
            return False
        row.final_text = final_text
        row.jd_ref = jd_ref
        row.status = "approved"
        row.edit_ratio = edit_ratio
        row.approved_at = datetime.now(timezone.utc)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def get_user_jds(user_email: str, status: str | None = None) -> list[dict]:
    """Return all JDs for a user (optionally filtered by status)."""
    try:
        q = UserJd.query.filter_by(user_email=user_email)
        if status:
            q = q.filter_by(status=status)
        rows = q.order_by(UserJd.created_at.desc()).all()
        return [_jd_to_dict(r) for r in rows]
    except Exception:
        return []


def get_all_jds(limit: int = 200) -> list[dict]:
    """Return all JDs across all users (admin only). Ordered newest first."""
    try:
        rows = UserJd.query.order_by(UserJd.created_at.desc()).limit(limit).all()
        return [_jd_to_dict(r) for r in rows]
    except Exception:
        return []


def get_all_approved_jds(limit: int = 200) -> list[dict]:
    """Return all approved JDs across all users, newest first (for Sample JD Library)."""
    try:
        rows = (UserJd.query
                .filter_by(status="approved")
                .order_by(UserJd.approved_at.desc())
                .limit(limit)
                .all())
        return [_jd_to_dict(r) for r in rows]
    except Exception:
        return []


def get_jd_by_generation_id(generation_id: str) -> dict | None:
    """Fetch a single JD row by generation_id."""
    try:
        row = UserJd.query.filter_by(generation_id=generation_id).first()
        return _jd_to_dict(row) if row else None
    except Exception:
        return None


def archive_jd(generation_id: str, user_email: str) -> bool:
    try:
        row = UserJd.query.filter_by(generation_id=generation_id, user_email=user_email).first()
        if row is None:
            return False
        row.status = "archived"
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


# ── jd_feedback ───────────────────────────────────────────────────────────────

def save_feedback(
    jd_id: str,
    generation_id: str,
    user_email: str,
    department: str,
    family: str,
    yoe_band: str,
    role_title: str,
    overall_rating: int,
    section_ratings: dict,
    positive_tags: list,
    improvement_tags: list,
    free_text: str,
    better_than_manual: str,
) -> bool:
    try:
        row = JdFeedback(
            jd_id=jd_id,
            generation_id=generation_id or "",
            user_email=user_email,
            department=department,
            family=family,
            yoe_band=yoe_band,
            role_title=role_title,
            overall_rating=overall_rating,
            section_ratings=section_ratings or {},
            positive_tags=positive_tags or [],
            improvement_tags=improvement_tags or [],
            free_text=free_text or "",
            better_than_manual=better_than_manual or "about_the_same",
        )
        db.session.add(row)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def get_feedback_stats() -> dict:
    """Aggregate feedback stats for the admin dashboard."""
    try:
        rows = JdFeedback.query.with_entities(
            JdFeedback.overall_rating, JdFeedback.department
        ).all()

        if not rows:
            return {"avg_rating": None, "count": 0, "by_dept": {}}

        total = sum(r[0] for r in rows)
        count = len(rows)
        by_dept: dict = {}
        for rating, dept in rows:
            dept = dept or "Unknown"
            if dept not in by_dept:
                by_dept[dept] = {"sum": 0, "count": 0}
            by_dept[dept]["sum"] += rating
            by_dept[dept]["count"] += 1

        return {
            "avg_rating": round(total / count, 2),
            "count": count,
            "by_dept": {d: round(v["sum"] / v["count"], 2) for d, v in by_dept.items()},
        }
    except Exception:
        return {"avg_rating": None, "count": 0, "by_dept": {}}


# ── jd_edit_diffs ─────────────────────────────────────────────────────────────

def save_edit_diff(
    jd_id: str,
    generation_id: str,
    user_email: str,
    department: str,
    family: str,
    yoe_band: str,
    role_title: str,
    edit_ratio: float,
    original_text: str,
    final_text: str,
) -> bool:
    try:
        orig_len = len(original_text)
        final_len = len(final_text)
        added = max(0, final_len - orig_len)
        removed = max(0, orig_len - final_len)
        row = JdEditDiff(
            jd_id=jd_id,
            generation_id=generation_id or "",
            user_email=user_email,
            department=department,
            family=family,
            yoe_band=yoe_band,
            role_title=role_title,
            edit_ratio=edit_ratio,
            char_added=added,
            char_removed=removed,
            original_len=orig_len,
            final_len=final_len,
        )
        db.session.add(row)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


# ── user_profiles ─────────────────────────────────────────────────────────────

def upsert_user_profile(
    user_id: str,
    email: str,
    full_name: str,
    avatar_url: str = "",
    role: str = "employee",
) -> bool:
    try:
        row = UserProfile.query.get(user_id)
        if row is None:
            row = UserProfile(id=user_id, email=email)
            db.session.add(row)
        row.email = email
        row.full_name = full_name
        row.avatar_url = avatar_url
        row.role = role
        row.last_active = datetime.now(timezone.utc)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def bump_jd_count(user_email: str) -> bool:
    """Increment jd_count for a user profile row."""
    try:
        row = UserProfile.query.filter_by(email=user_email).first()
        if row is not None:
            row.jd_count = (row.jd_count or 0) + 1
            row.last_active = datetime.now(timezone.utc)
            db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def get_all_user_profiles() -> list[dict]:
    try:
        rows = UserProfile.query.order_by(UserProfile.jd_count.desc()).all()
        return [_profile_to_dict(r) for r in rows]
    except Exception:
        return []


# ── kb_versions ───────────────────────────────────────────────────────────────

def bump_kb_version(department: str, family: str, yoe_band: str) -> int:
    """Increment KB version for a dept/family/band; return new version number."""
    try:
        row = KbVersion.query.filter_by(
            department=department, family=family, yoe_band=yoe_band
        ).first()
        if row is not None:
            row.version = (row.version or 1) + 1
            new_ver = row.version
        else:
            new_ver = 1
            row = KbVersion(department=department, family=family, yoe_band=yoe_band, version=new_ver)
            db.session.add(row)
        db.session.commit()
        return new_ver
    except Exception:
        db.session.rollback()
        return 0


# ── Admin analytics ───────────────────────────────────────────────────────────

def get_admin_stats() -> dict | None:
    """
    Return dashboard metrics from MySQL. Returns None on DB failure so callers
    can fall back to the filesystem path.
    """
    try:
        now = datetime.now(timezone.utc)
        week_ago = (now - timedelta(days=7)).isoformat()
        two_weeks_ago = (now - timedelta(days=14)).isoformat()

        rows = (UserJd.query
                .order_by(UserJd.created_at.desc())
                .limit(500)
                .all())
        jds = [_jd_to_dict(r) for r in rows]

        fb_stats = get_feedback_stats()

        total = len(jds)
        this_week = sum(1 for j in jds if j.get("created_at", "") >= week_ago)
        last_week = sum(1 for j in jds if two_weeks_ago <= j.get("created_at", "") < week_ago)

        dept_counts: dict = {}
        user_stats: dict = {}
        recent_activity = []

        from collections import defaultdict
        daily_counts: dict = defaultdict(int)

        for j in jds:
            dept = j.get("department", "unknown")
            email = j.get("user_email", "—")
            ts = j.get("created_at", "")
            date = ts[:10] if ts else "—"

            dept_counts[dept] = dept_counts.get(dept, 0) + 1
            if date and date != "—":
                daily_counts[date] += 1

            if email not in user_stats:
                user_stats[email] = {"total": 0, "depts": {}}
            user_stats[email]["total"] += 1
            user_stats[email]["depts"][dept] = user_stats[email]["depts"].get(dept, 0) + 1

            recent_activity.append({
                "role": j.get("role_title", "—"),
                "dept": dept,
                "family": j.get("family", "—"),
                "date": date,
                "by": email,
                "status": j.get("status", "draft"),
            })

        if recent_activity:
            recent_activity[0]["is_newest"] = True

        all_days = sorted(daily_counts.keys())[-7:]
        daily_series = [{"date": d, "count": daily_counts[d]} for d in all_days]

        ai_score = (round(fb_stats["avg_rating"] / 5 * 100, 1)
                    if fb_stats.get("avg_rating") else None)

        return {
            "total_jds": total,
            "this_week": this_week,
            "last_week": last_week,
            "dept_counts": dept_counts,
            "recent_activity": recent_activity[:20],
            "user_stats": user_stats,
            "daily_series": daily_series,
            "ai_score": ai_score,
            "feedback_count": fb_stats["count"],
            "source": "supabase",
        }
    except Exception:
        return None
