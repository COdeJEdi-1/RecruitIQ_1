"""
Feedback Learning Engine — Arvind JD Generator

Stores and retrieves two types of learning signals (single-variant generation
at temperature 0.9 — there is no variant selection signal):
  1. Edit diff          — what the user changed before approving
  2. Explicit feedback  — star rating, section scores, tags, free text

Builds a Feedback Digest per dept/role/yoe_band that is injected into
Layer 3 of future prompts for the same combination.

Phase 3: persists to MySQL via SQLAlchemy (`jd_edit_diffs`, `jd_feedback`,
`kb_family_stats` tables) instead of the old kb/{dept}/{family}/feedback/*.jsonl
+ version.yaml files. Every DB write is best-effort and swallows exceptions
(matching the original fire-and-forget JSONL/YAML append contract), following
the same try/except + db.session.rollback() style as services/jd_service.py.
"""

from database.db import db
from database.models import JdEditDiff, JdFeedback, KbFamilyStats

# ── helpers ──────────────────────────────────────────────────────────────────


def _get_or_create_family_stats(dept: str, family: str) -> KbFamilyStats:
    """Find-or-create the KbFamilyStats row for a dept/family pair.
    Caller is responsible for the surrounding try/except + commit."""
    row = KbFamilyStats.query.filter_by(department=dept, family=family).first()
    if row is None:
        row = KbFamilyStats(department=dept, family=family)
        db.session.add(row)
    return row


# ── Signal 2: Edit diff ───────────────────────────────────────────────────────

def compute_edit_ratio(original: str, final: str) -> float:
    """
    Simple character-level edit ratio.
    0.0 = no changes, 1.0 = completely rewritten.
    """
    if not original:
        return 1.0
    orig_len = len(original)
    final_len = len(final)
    # Levenshtein approximation via difflib
    import difflib
    matcher = difflib.SequenceMatcher(None, original, final)
    ratio = matcher.ratio()
    return round(1.0 - ratio, 3)


def summarise_diff(original: str, final: str) -> str:
    """
    Produce a human-readable summary of what changed.
    Uses simple line-diff — no LLM call to keep it fast.
    """
    import difflib
    orig_lines = original.splitlines()
    final_lines = final.splitlines()
    diff = list(difflib.unified_diff(orig_lines, final_lines, lineterm="", n=0))
    added = [l[1:].strip() for l in diff if l.startswith("+") and not l.startswith("+++")]
    removed = [l[1:].strip() for l in diff if l.startswith("-") and not l.startswith("---")]
    parts = []
    if added:
        parts.append(f"Added: {'; '.join(added[:3])}{'...' if len(added) > 3 else ''}")
    if removed:
        parts.append(f"Removed: {'; '.join(removed[:3])}{'...' if len(removed) > 3 else ''}")
    return " | ".join(parts) if parts else "No significant changes."


def store_edit_diff(
    dept: str,
    family: str,
    yoe_band: str,
    jd_id: str,
    generation_id: str,
    original_text: str,
    final_text: str,
    role_title: str,
    user_email: str = "",
) -> float:
    """Stores the edit diff and returns the edit_ratio."""
    ratio = compute_edit_ratio(original_text, final_text)
    summary = summarise_diff(original_text, final_text)

    try:
        row = JdEditDiff(
            jd_id=jd_id,
            generation_id=generation_id,
            user_email=user_email,
            department=dept,
            family=family,
            yoe_band=yoe_band,
            role_title=role_title,
            edit_ratio=ratio,
            diff_summary=summary,
        )
        db.session.add(row)
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        stats = _get_or_create_family_stats(dept, family)
        trend = list(stats.edit_ratio_trend or [])
        trend.append(round(ratio, 3))
        stats.edit_ratio_trend = trend[-20:]  # keep last 20
        stats.approved_jds_count = (stats.approved_jds_count or 0) + 1
        db.session.commit()
    except Exception:
        db.session.rollback()

    return ratio


# ── Signal 3: Explicit feedback ───────────────────────────────────────────────

def store_explicit_feedback(
    dept: str,
    family: str,
    yoe_band: str,
    jd_id: str,
    overall_rating: int,            # 1–5
    section_ratings: dict,          # {"role_summary": 4, "responsibilities": 5, ...}
    positive_tags: list[str],
    improvement_tags: list[str],
    free_text: str,
    better_than_manual: str,        # "yes" | "about_the_same" | "no"
    role_title: str,
    user_email: str = "",
) -> None:
    try:
        row = JdFeedback(
            jd_id=jd_id,
            user_email=user_email,
            department=dept,
            family=family,
            yoe_band=yoe_band,
            role_title=role_title,
            overall_rating=overall_rating,
            section_ratings=section_ratings,
            positive_tags=positive_tags,
            improvement_tags=improvement_tags,
            free_text=free_text,
            better_than_manual=better_than_manual,
        )
        db.session.add(row)
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        stats = _get_or_create_family_stats(dept, family)
        stats.feedback_submissions_count = (stats.feedback_submissions_count or 0) + 1
        # Rolling avg rating
        prev_avg = stats.avg_quality_rating or overall_rating
        count = stats.feedback_submissions_count
        stats.avg_quality_rating = round(
            (prev_avg * (count - 1) + overall_rating) / count, 2
        )
        db.session.commit()
    except Exception:
        db.session.rollback()


# ── Feedback Digest builder ───────────────────────────────────────────────────

def build_feedback_digest(dept: str, family: str, yoe_band: str) -> str:
    """
    Compiles both signal types into a plain-text digest for
    injection into the Layer 3 prompt context.
    Returns empty string if no feedback exists yet.
    """
    try:
        diffs = (
            JdEditDiff.query
            .filter_by(department=dept, family=family, yoe_band=yoe_band)
            .order_by(JdEditDiff.created_at.asc())
            .all()
        )
    except Exception:
        diffs = []

    # --- edit diffs ---
    avg_edit_ratio = (
        round(sum(r.edit_ratio for r in diffs) / len(diffs), 3) if diffs else None
    )
    diff_summaries = [r.diff_summary for r in diffs[-5:] if r.diff_summary]

    try:
        feedbacks = (
            JdFeedback.query
            .filter_by(department=dept, family=family, yoe_band=yoe_band)
            .order_by(JdFeedback.created_at.asc())
            .all()
        )
    except Exception:
        feedbacks = []

    # --- explicit feedback ---
    if not feedbacks and not diffs:
        return ""

    avg_rating = (
        round(sum(r.overall_rating for r in feedbacks) / len(feedbacks), 1)
        if feedbacks else None
    )
    all_pos_tags = [t for r in feedbacks for t in (r.positive_tags or [])]
    all_imp_tags = [t for r in feedbacks for t in (r.improvement_tags or [])]
    free_texts = [r.free_text for r in feedbacks[-3:] if (r.free_text or "").strip()]

    # Build digest string
    lines = [
        f"--- FEEDBACK SIGNALS ({dept}/{family} · {yoe_band} years) ---",
        f"Based on {len(feedbacks)} explicit feedback submission(s) and {len(diffs)} approved JD(s).",
    ]

    if avg_rating is not None:
        lines.append(f"Average quality rating: {avg_rating}/5 — target 4.5+")
    if avg_edit_ratio is not None:
        lines.append(f"Average edit ratio: {avg_edit_ratio} (0=no edits, 1=fully rewritten). Target <0.10.")

    if all_pos_tags:
        from collections import Counter
        top_pos = [t for t, _ in Counter(all_pos_tags).most_common(5)]
        lines.append(f"What users approved: {', '.join(top_pos)}")

    if all_imp_tags:
        from collections import Counter
        top_imp = [t for t, _ in Counter(all_imp_tags).most_common(5)]
        lines.append(f"What users changed: {', '.join(top_imp)}")

    if diff_summaries:
        lines.append("Recent edit patterns:")
        for s in diff_summaries[:3]:
            lines.append(f"  · {s}")

    if free_texts:
        lines.append("Direct user instructions for next generation:")
        for t in free_texts:
            lines.append(f"  · {t}")

    return "\n".join(lines)


# ── Admin analytics helpers ───────────────────────────────────────────────────

def get_analytics_summary() -> list[dict]:
    """
    Returns a list of per role-family summary dicts for the admin analytics page.
    """
    try:
        rows = (
            KbFamilyStats.query
            .order_by(KbFamilyStats.department.asc(), KbFamilyStats.family.asc())
            .all()
        )
    except Exception:
        return []

    summaries = []
    for row in rows:
        summaries.append({
            "dept": row.department,
            "family": row.family,
            "version": row.current_version or "v1.0",
            "approved_jds": row.approved_jds_count or 0,
            "feedback_count": row.feedback_submissions_count or 0,
            "avg_rating": row.avg_quality_rating,
            "edit_ratio_trend": row.edit_ratio_trend or [],
            "last_updated": row.last_updated.strftime("%Y-%m-%d") if row.last_updated else "",
        })
    return summaries
