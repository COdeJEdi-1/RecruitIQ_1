"""
Supabase data-access layer for the JD Generator.

Uses the service_role key (bypasses RLS) for all writes.
All public-facing reads can also use the service key server-side — RLS
enforcement happens on the client (browser) if it ever calls Supabase directly.

Every function is best-effort: a Supabase outage must never break the
filesystem-based fallback that the app still uses as primary storage.
"""

import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL              = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY         = os.getenv("SUPABASE_ANON_KEY")

DB_ENABLED = bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)

_svc_client = None


def svc() :
    """Return a lazily-created service-role Supabase client. None if not configured."""
    global _svc_client
    if not DB_ENABLED:
        return None
    if _svc_client is None:
        from supabase import create_client
        _svc_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _svc_client


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
    """Insert a new draft JD row (status='draft'). Returns True on success."""
    client = svc()
    if client is None:
        return False
    try:
        client.table("user_jds").upsert({
            "generation_id": generation_id,
            "user_email":    user_email,
            "role_title":    role_title,
            "department":    department,
            "division":      division or "",
            "family":        family,
            "yoe_band":      yoe_band,
            "focus_areas":   focus_areas or "",
            "original_text": original_text,
            "status":        "draft",
        }, on_conflict="generation_id").execute()
        return True
    except Exception:
        return False


def approve_draft(
    generation_id: str,
    final_text: str,
    jd_ref: str,
    edit_ratio: float,
) -> bool:
    """Update a draft row to approved status with the final edited text."""
    client = svc()
    if client is None:
        return False
    try:
        client.table("user_jds").update({
            "final_text":   final_text,
            "jd_ref":       jd_ref,
            "status":       "approved",
            "edit_ratio":   edit_ratio,
            "approved_at":  datetime.now(timezone.utc).isoformat(),
        }).eq("generation_id", generation_id).execute()
        return True
    except Exception:
        return False


def get_user_jds(user_email: str, status: str | None = None) -> list[dict]:
    """Return all JDs for a user (optionally filtered by status)."""
    client = svc()
    if client is None:
        return []
    try:
        q = (client.table("user_jds")
             .select("*")
             .eq("user_email", user_email)
             .order("created_at", desc=True))
        if status:
            q = q.eq("status", status)
        return q.execute().data or []
    except Exception:
        return []


def get_all_jds(limit: int = 200) -> list[dict]:
    """Return all JDs across all users (admin only). Ordered newest first."""
    client = svc()
    if client is None:
        return []
    try:
        return (client.table("user_jds")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute().data or [])
    except Exception:
        return []


def get_all_approved_jds(limit: int = 200) -> list[dict]:
    """Return all approved JDs across all users, newest first (for Sample JD Library)."""
    client = svc()
    if client is None:
        return []
    try:
        return (client.table("user_jds")
                .select("*")
                .eq("status", "approved")
                .order("approved_at", desc=True)
                .limit(limit)
                .execute().data or [])
    except Exception:
        return []


def get_jd_by_generation_id(generation_id: str) -> dict | None:
    """Fetch a single JD row by generation_id."""
    client = svc()
    if client is None:
        return None
    try:
        rows = (client.table("user_jds")
                .select("*")
                .eq("generation_id", generation_id)
                .limit(1)
                .execute().data or [])
        return rows[0] if rows else None
    except Exception:
        return None


def archive_jd(generation_id: str, user_email: str) -> bool:
    client = svc()
    if client is None:
        return False
    try:
        client.table("user_jds").update({"status": "archived"}) \
            .eq("generation_id", generation_id) \
            .eq("user_email", user_email) \
            .execute()
        return True
    except Exception:
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
    client = svc()
    if client is None:
        return False
    try:
        client.table("jd_feedback").insert({
            "jd_id":              jd_id,
            "generation_id":      generation_id or "",
            "user_email":         user_email,
            "department":         department,
            "family":             family,
            "yoe_band":           yoe_band,
            "role_title":         role_title,
            "overall_rating":     overall_rating,
            "section_ratings":    section_ratings or {},
            "positive_tags":      positive_tags or [],
            "improvement_tags":   improvement_tags or [],
            "free_text":          free_text or "",
            "better_than_manual": better_than_manual or "about_the_same",
        }).execute()
        return True
    except Exception:
        return False


def get_feedback_stats() -> dict:
    """Aggregate feedback stats for the admin dashboard."""
    client = svc()
    if client is None:
        return {"avg_rating": None, "count": 0, "by_dept": {}}
    try:
        rows = client.table("jd_feedback").select(
            "overall_rating, department"
        ).execute().data or []

        if not rows:
            return {"avg_rating": None, "count": 0, "by_dept": {}}

        total  = sum(r["overall_rating"] for r in rows)
        count  = len(rows)
        by_dept: dict = {}
        for r in rows:
            d = r.get("department", "Unknown")
            if d not in by_dept:
                by_dept[d] = {"sum": 0, "count": 0}
            by_dept[d]["sum"]   += r["overall_rating"]
            by_dept[d]["count"] += 1

        return {
            "avg_rating": round(total / count, 2),
            "count":      count,
            "by_dept":    {d: round(v["sum"] / v["count"], 2) for d, v in by_dept.items()},
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
    client = svc()
    if client is None:
        return False
    try:
        orig_len  = len(original_text)
        final_len = len(final_text)
        # Simple char-level diff approximation
        added    = max(0, final_len - orig_len)
        removed  = max(0, orig_len  - final_len)
        client.table("jd_edit_diffs").insert({
            "jd_id":        jd_id,
            "generation_id": generation_id or "",
            "user_email":   user_email,
            "department":   department,
            "family":       family,
            "yoe_band":     yoe_band,
            "role_title":   role_title,
            "edit_ratio":   edit_ratio,
            "char_added":   added,
            "char_removed": removed,
            "original_len": orig_len,
            "final_len":    final_len,
        }).execute()
        return True
    except Exception:
        return False


# ── user_profiles ─────────────────────────────────────────────────────────────

def upsert_user_profile(
    user_id: str,
    email: str,
    full_name: str,
    avatar_url: str = "",
    role: str = "employee",
) -> bool:
    client = svc()
    if client is None:
        return False
    try:
        client.table("user_profiles").upsert({
            "id":         user_id,
            "email":      email,
            "full_name":  full_name,
            "avatar_url": avatar_url,
            "role":       role,
            "last_active": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="id").execute()
        return True
    except Exception:
        return False


def bump_jd_count(user_email: str) -> bool:
    """Increment jd_count for a user profile row."""
    client = svc()
    if client is None:
        return False
    try:
        # Supabase doesn't support increment natively; use rpc if available
        # Fallback: read then write (acceptable for low-concurrency demo)
        rows = client.table("user_profiles").select("jd_count").eq("email", user_email).execute().data
        if rows:
            new_count = (rows[0].get("jd_count") or 0) + 1
            client.table("user_profiles").update({
                "jd_count":    new_count,
                "last_active": datetime.now(timezone.utc).isoformat(),
            }).eq("email", user_email).execute()
        return True
    except Exception:
        return False


def get_all_user_profiles() -> list[dict]:
    client = svc()
    if client is None:
        return []
    try:
        return client.table("user_profiles").select("*").order("jd_count", desc=True).execute().data or []
    except Exception:
        return []


# ── kb_versions ───────────────────────────────────────────────────────────────

def bump_kb_version(department: str, family: str, yoe_band: str) -> int:
    """Increment KB version for a dept/family/band; return new version number."""
    client = svc()
    if client is None:
        return 0
    try:
        rows = (client.table("kb_versions")
                .select("version")
                .eq("department", department)
                .eq("family", family)
                .eq("yoe_band", yoe_band)
                .execute().data)
        if rows:
            new_ver = (rows[0].get("version") or 1) + 1
            client.table("kb_versions").update({
                "version":    new_ver,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("department", department).eq("family", family).eq("yoe_band", yoe_band).execute()
        else:
            new_ver = 1
            client.table("kb_versions").insert({
                "department": department,
                "family":     family,
                "yoe_band":   yoe_band,
                "version":    new_ver,
            }).execute()
        return new_ver
    except Exception:
        return 0


# ── Admin analytics ───────────────────────────────────────────────────────────

def get_admin_stats() -> dict | None:
    """
    Return dashboard metrics from Supabase. Returns None when DB is unavailable
    so callers can fall back to the filesystem path.
    """
    client = svc()
    if client is None:
        return None
    try:
        from datetime import timedelta
        now      = datetime.now(timezone.utc)
        week_ago = (now - timedelta(days=7)).isoformat()
        two_weeks_ago = (now - timedelta(days=14)).isoformat()

        jds = (client.table("user_jds")
               .select("user_email, department, role_title, status, created_at, approved_at, jd_ref, family")
               .order("created_at", desc=True)
               .limit(500)
               .execute().data or [])

        fb_stats = get_feedback_stats()

        total     = len(jds)
        this_week = sum(1 for j in jds if j.get("created_at", "") >= week_ago)
        last_week = sum(1 for j in jds if two_weeks_ago <= j.get("created_at", "") < week_ago)

        dept_counts: dict = {}
        user_stats:  dict = {}
        recent_activity   = []

        from collections import defaultdict
        daily_counts: dict = defaultdict(int)

        for j in jds:
            dept  = j.get("department", "unknown")
            email = j.get("user_email", "—")
            ts    = j.get("created_at", "")
            date  = ts[:10] if ts else "—"

            dept_counts[dept] = dept_counts.get(dept, 0) + 1
            if date and date != "—":
                daily_counts[date] += 1

            if email not in user_stats:
                user_stats[email] = {"total": 0, "depts": {}}
            user_stats[email]["total"] += 1
            user_stats[email]["depts"][dept] = user_stats[email]["depts"].get(dept, 0) + 1

            recent_activity.append({
                "role":   j.get("role_title", "—"),
                "dept":   dept,
                "family": j.get("family", "—"),
                "date":   date,
                "by":     email,
                "status": j.get("status", "draft"),
            })

        if recent_activity:
            recent_activity[0]["is_newest"] = True

        all_days     = sorted(daily_counts.keys())[-7:]
        daily_series = [{"date": d, "count": daily_counts[d]} for d in all_days]

        ai_score = (round(fb_stats["avg_rating"] / 5 * 100, 1)
                    if fb_stats.get("avg_rating") else None)

        return {
            "total_jds":       total,
            "this_week":       this_week,
            "last_week":       last_week,
            "dept_counts":     dept_counts,
            "recent_activity": recent_activity[:20],
            "user_stats":      user_stats,
            "daily_series":    daily_series,
            "ai_score":        ai_score,
            "feedback_count":  fb_stats["count"],
            "source":          "supabase",
        }
    except Exception:
        return None
