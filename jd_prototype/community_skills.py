"""
Community Skill Consolidation — Arvind JD Generator

Tracks custom (user-typed, non-suggested) skills added per department/family
when a JD is approved. When the same normalized skill has been added by
PROMOTION_THRESHOLD or more distinct users for a role, it is promoted into
the suggested-skills list surfaced for future JDs on that role.

Phase 3: persists to MySQL via SQLAlchemy (`community_skills` table, model
CommunitySkill in database/models.py) instead of the old
kb/{dept}/{family}/feedback/custom_skills.jsonl file. Writes are best-effort
and swallow exceptions, matching the original fire-and-forget JSONL append
contract, following the same try/except + db.session.rollback() style as
services/jd_service.py.
"""

import re
from collections import Counter

from database.db import db
from database.models import CommunitySkill

PROMOTION_THRESHOLD = 5


def _normalize_skill(raw: str) -> str:
    """Lowercase, trim, collapse whitespace. Keeps +, #, . so 'C++', 'C#',
    'Node.js' stay distinguishable from unrelated words."""
    s = raw.strip().lower()
    s = re.sub(r"[^a-z0-9+#.]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def record_custom_skill(
    dept: str,
    family: str,
    skill_raw: str,
    user_email: str,
    jd_id: str = "",
    role_title: str = "",
) -> None:
    """Log that `user_email` added `skill_raw` as a custom skill for this
    role. No-op if this exact (skill, user) pair was already logged for
    this role — the same user re-adding a skill doesn't count twice."""
    skill_raw = (skill_raw or "").strip()
    if not skill_raw:
        return
    skill_key = _normalize_skill(skill_raw)
    if not skill_key:
        return

    try:
        existing = CommunitySkill.query.filter_by(
            department=dept,
            family=family,
            skill_key=skill_key,
            user_email=user_email,
        ).first()
        if existing is not None:
            return

        row = CommunitySkill(
            department=dept,
            family=family,
            skill_raw=skill_raw,
            skill_key=skill_key,
            user_email=user_email,
            jd_id=jd_id,
            role_title=role_title,
        )
        db.session.add(row)
        db.session.commit()
    except Exception:
        db.session.rollback()


def get_promoted_skills(dept: str, family: str, threshold: int = PROMOTION_THRESHOLD) -> list[str]:
    """Return skill labels that at least `threshold` distinct users have
    added for this role, most-agreed-on first."""
    try:
        records = CommunitySkill.query.filter_by(department=dept, family=family).all()
    except Exception:
        return []

    if not records:
        return []

    by_key: dict[str, list] = {}
    for r in records:
        key = r.skill_key
        if not key:
            continue
        by_key.setdefault(key, []).append(r)

    promoted = []
    for key, recs in by_key.items():
        distinct_users = {r.user_email for r in recs if r.user_email}
        if len(distinct_users) >= threshold:
            label = Counter(r.skill_raw for r in recs).most_common(1)[0][0]
            promoted.append((label, len(distinct_users)))

    promoted.sort(key=lambda x: -x[1])
    return [label for label, _ in promoted]
