"""
SQLAlchemy models for the JD Generator (MySQL).

Schema originally mirrored the Supabase/Postgres tables it replaced; these
models are now the live runtime schema, queried via services/jd_service.py
and services/kb_service.py.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship

from database.db import db


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(db.Model, UserMixin):
    """Application user — authenticated via Flask-Login (Werkzeug password hashes)."""

    __tablename__ = "users"

    id = db.Column(String(36), primary_key=True, default=_uuid)
    username = db.Column(String(255), unique=True, nullable=True)
    email = db.Column(String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(String(255), nullable=True)
    full_name = db.Column(String(255), nullable=True)
    avatar_url = db.Column(String(512), nullable=True)
    role = db.Column(String(32), nullable=False, default="employee")
    auth_provider = db.Column(String(32), nullable=False, default="local")
    magic_token = db.Column(String(128), nullable=True)
    magic_token_expires = db.Column(DateTime, nullable=True)
    created_at = db.Column(DateTime, nullable=False, default=_utcnow)
    updated_at = db.Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False)

    # ── Template-facing display aliases (no schema impact — computed only) ──
    @property
    def name(self) -> str:
        return self.full_name or self.email.split("@")[0]

    @property
    def picture(self) -> str:
        return self.avatar_url or ""

    @property
    def initials(self) -> str:
        parts = self.name.split()
        return "".join(p[0].upper() for p in parts[:2]) if parts else "U"


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    email = db.Column(String(255), unique=True, nullable=False, index=True)
    full_name = db.Column(String(255), nullable=True)
    role = db.Column(String(32), nullable=False, default="employee")
    avatar_url = db.Column(String(512), nullable=True)
    jd_count = db.Column(Integer, nullable=False, default=0)
    last_active = db.Column(DateTime, nullable=True)
    created_at = db.Column(DateTime, nullable=False, default=_utcnow)
    updated_at = db.Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)

    user = relationship("User", back_populates="profile")


class UserJd(db.Model):
    __tablename__ = "user_jds"

    id = db.Column(String(36), primary_key=True, default=_uuid)
    generation_id = db.Column(String(64), unique=True, nullable=False, index=True)
    user_email = db.Column(String(255), nullable=False, index=True)
    role_title = db.Column(String(255), nullable=False)
    department = db.Column(String(128), nullable=False, index=True)
    division = db.Column(String(128), nullable=True)
    family = db.Column(String(128), nullable=False)
    yoe_band = db.Column(String(32), nullable=False)
    focus_areas = db.Column(Text, nullable=True)
    original_text = db.Column(Text, nullable=False)
    final_text = db.Column(Text, nullable=True)
    status = db.Column(String(32), nullable=False, default="draft", index=True)
    edit_ratio = db.Column(Float, nullable=True)
    jd_ref = db.Column(String(32), nullable=True)
    approved_at = db.Column(DateTime, nullable=True)
    created_at = db.Column(DateTime, nullable=False, default=_utcnow, index=True)
    updated_at = db.Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


class JdFeedback(db.Model):
    __tablename__ = "jd_feedback"

    id = db.Column(String(36), primary_key=True, default=_uuid)
    jd_id = db.Column(String(64), nullable=False, index=True)
    generation_id = db.Column(String(64), nullable=True)
    user_email = db.Column(String(255), nullable=False)
    department = db.Column(String(128), nullable=True, index=True)
    family = db.Column(String(128), nullable=True)
    yoe_band = db.Column(String(32), nullable=True)
    role_title = db.Column(String(255), nullable=True)
    overall_rating = db.Column(Integer, nullable=False)
    section_ratings = db.Column(JSON, nullable=True)
    positive_tags = db.Column(JSON, nullable=True)
    improvement_tags = db.Column(JSON, nullable=True)
    free_text = db.Column(Text, nullable=True)
    better_than_manual = db.Column(String(64), nullable=True, default="about_the_same")
    created_at = db.Column(DateTime, nullable=False, default=_utcnow)


class JdEditDiff(db.Model):
    __tablename__ = "jd_edit_diffs"

    id = db.Column(String(36), primary_key=True, default=_uuid)
    jd_id = db.Column(String(64), nullable=False, index=True)
    generation_id = db.Column(String(64), nullable=True)
    user_email = db.Column(String(255), nullable=False)
    department = db.Column(String(128), nullable=True)
    family = db.Column(String(128), nullable=True)
    yoe_band = db.Column(String(32), nullable=True)
    role_title = db.Column(String(255), nullable=True)
    edit_ratio = db.Column(Float, nullable=True)
    char_added = db.Column(Integer, nullable=True)
    char_removed = db.Column(Integer, nullable=True)
    original_len = db.Column(Integer, nullable=True)
    final_len = db.Column(Integer, nullable=True)
    diff_summary = db.Column(Text, nullable=True)
    created_at = db.Column(DateTime, nullable=False, default=_utcnow)


class RoleTaxonomy(db.Model):
    __tablename__ = "role_taxonomy"
    __table_args__ = (
        UniqueConstraint(
            "department", "role_family", "yoe_band",
            name="uq_role_taxonomy_dept_family_yoe",
        ),
    )

    id = db.Column(String(36), primary_key=True, default=_uuid)
    department = db.Column(String(128), nullable=False, index=True)
    division = db.Column(String(128), nullable=False)
    role_family = db.Column(String(128), nullable=False)
    yoe_band = db.Column(String(32), nullable=False)
    seniority_label = db.Column(String(64), nullable=True)
    created_at = db.Column(DateTime, nullable=False, default=_utcnow)

    samples = relationship("SampleJd", back_populates="taxonomy", cascade="all, delete-orphan")


class SampleJd(db.Model):
    __tablename__ = "sample_jds"

    id = db.Column(String(36), primary_key=True, default=_uuid)
    taxonomy_id = db.Column(
        String(36),
        ForeignKey("role_taxonomy.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    jd_text = db.Column(Text, nullable=False)
    sample_metadata = db.Column("metadata", JSON, nullable=True)
    added_by = db.Column(String(255), nullable=True)
    created_at = db.Column(DateTime, nullable=False, default=_utcnow)

    taxonomy = relationship("RoleTaxonomy", back_populates="samples")


class KbVersion(db.Model):
    __tablename__ = "kb_versions"
    __table_args__ = (
        UniqueConstraint(
            "department", "family", "yoe_band",
            name="uq_kb_versions_dept_family_yoe",
        ),
    )

    id = db.Column(String(36), primary_key=True, default=_uuid)
    department = db.Column(String(128), nullable=False)
    family = db.Column(String(128), nullable=False)
    yoe_band = db.Column(String(32), nullable=False)
    version = db.Column(Integer, nullable=False, default=1)
    updated_at = db.Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


class ShareToken(db.Model):
    __tablename__ = "share_tokens"

    id = db.Column(String(36), primary_key=True, default=_uuid)
    token = db.Column(String(128), unique=True, nullable=False, index=True)
    jd_id = db.Column(String(64), nullable=False)
    user_email = db.Column(String(255), nullable=False)
    expires_at = db.Column(DateTime, nullable=True)
    created_at = db.Column(DateTime, nullable=False, default=_utcnow)


# ── Darwinbox mock integration (replaces darwin_data/*.json — Phase 3) ────────

class DarwinboxJob(db.Model):
    """Replacement for darwin_data/darwinbox_jobs.json rows."""

    __tablename__ = "darwinbox_jobs"

    darwinbox_job_id = db.Column(String(36), primary_key=True, default=_uuid)
    jd_id = db.Column(String(64), nullable=True, index=True)
    role_title = db.Column(String(255), nullable=False)
    jd_text = db.Column(Text, nullable=False)
    version = db.Column(Integer, nullable=False, default=1)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    status = db.Column(String(32), nullable=False, default="published")
    published_at = db.Column(DateTime, nullable=False, default=_utcnow)
    created_by = db.Column(String(255), nullable=True)
    position_level = db.Column(String(32), nullable=False, default="junior")
    shortlist_threshold = db.Column(Integer, nullable=True)
    jd_requirements = db.Column(JSON, nullable=True)
    jd_requirements_extracted_at = db.Column(DateTime, nullable=True)


class JobPosting(db.Model):
    """Replacement for darwin_data/job_postings.json rows."""

    __tablename__ = "job_postings"

    posting_id = db.Column(String(36), primary_key=True, default=_uuid)
    darwinbox_job_id = db.Column(String(36), nullable=False, index=True)
    platform = db.Column(String(32), nullable=False)
    application_link = db.Column(String(512), nullable=True)
    status = db.Column(String(32), nullable=False, default="active")
    posted_at = db.Column(DateTime, nullable=False, default=_utcnow)


class Candidate(db.Model):
    """Replacement for darwin_data/candidates.json rows."""

    __tablename__ = "candidates"

    candidate_id = db.Column(String(36), primary_key=True, default=_uuid)
    darwinbox_job_id = db.Column(String(36), nullable=False, index=True)
    platform_source = db.Column(String(32), nullable=True)
    name = db.Column(String(255), nullable=False)
    email = db.Column(String(255), nullable=True)
    phone = db.Column(String(32), nullable=True)
    resume_file = db.Column(String(512), nullable=True)
    applied_at = db.Column(DateTime, nullable=False, default=_utcnow)
    consent_given = db.Column(db.Boolean, nullable=False, default=False)
    consent_timestamp = db.Column(DateTime, nullable=True)
    consent_text = db.Column(Text, nullable=True)
    resume_profile = db.Column(JSON, nullable=True)
    resume_profile_extracted_at = db.Column(DateTime, nullable=True)
    manual_call_triggered_at = db.Column(DateTime, nullable=True)


class CandidateScore(db.Model):
    """Replacement for darwin_data/candidate_scores.json rows."""

    __tablename__ = "candidate_scores"

    score_id = db.Column(String(36), primary_key=True, default=_uuid)
    candidate_id = db.Column(String(36), nullable=False, index=True)
    darwinbox_job_id = db.Column(String(36), nullable=False, index=True)
    overall_score = db.Column(Float, nullable=False)
    skills_score = db.Column(Float, nullable=True)
    experience_score = db.Column(Float, nullable=True)
    education_score = db.Column(Float, nullable=True)
    title_relevance_score = db.Column(Float, nullable=True)
    domain_score = db.Column(Float, nullable=True)
    score_breakdown = db.Column(JSON, nullable=True)
    scored_at = db.Column(DateTime, nullable=False, default=_utcnow)


class ActivityLog(db.Model):
    """Replacement for darwin_data/activity_log.json rows."""

    __tablename__ = "activity_log"

    log_id = db.Column(String(36), primary_key=True, default=_uuid)
    user_id = db.Column(String(255), nullable=True, index=True)
    action = db.Column(String(64), nullable=False)
    entity_type = db.Column(String(64), nullable=True)
    entity_id = db.Column(String(64), nullable=True)
    log_metadata = db.Column("metadata", JSON, nullable=True)
    created_at = db.Column(DateTime, nullable=False, default=_utcnow, index=True)


class VoiceAgentPush(db.Model):
    """Replacement for darwin_data/voice_agent_pushes.json (dedup list)."""

    __tablename__ = "voice_agent_pushes"

    candidate_id = db.Column(String(36), primary_key=True)
    pushed_at = db.Column(DateTime, nullable=False, default=_utcnow)


class DownloadRequest(db.Model):
    """Replacement for darwin_data/download_requests.json rows (owned/written by DummyDarwin-main)."""

    __tablename__ = "download_requests"

    request_id = db.Column(String(36), primary_key=True, default=_uuid)
    requester_id = db.Column(String(255), nullable=False, index=True)
    requester_name = db.Column(String(255), nullable=True)
    filters = db.Column(JSON, nullable=True)
    match_count = db.Column(Integer, nullable=False, default=0)
    status = db.Column(String(32), nullable=False, default="pending", index=True)
    created_at = db.Column(DateTime, nullable=False, default=_utcnow)
    reviewed_at = db.Column(DateTime, nullable=True)
    reviewed_by = db.Column(String(255), nullable=True)
    reviewer_name = db.Column(String(255), nullable=True)
    reject_reason = db.Column(Text, nullable=True)


# ── Pending JD generations (replaces darwin_data/pending_generations.json) ────

class PendingGeneration(db.Model):
    __tablename__ = "pending_generations"

    generation_id = db.Column(String(64), primary_key=True)
    payload = db.Column(JSON, nullable=False)
    created_at = db.Column(DateTime, nullable=False, default=_utcnow)
    updated_at = db.Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


# ── KB family stats (replaces kb/{dept}/{family}/version.yaml) ────────────────
# Distinct from KbVersion (per dept/family/yoe_band Supabase mirror, simple
# int counter) — this tracks feedback_engine.py's richer per dept/family
# analytics (no yoe_band dimension in version.yaml).

class KbFamilyStats(db.Model):
    __tablename__ = "kb_family_stats"
    __table_args__ = (
        UniqueConstraint("department", "family", name="uq_kb_family_stats_dept_family"),
    )

    id = db.Column(String(36), primary_key=True, default=_uuid)
    department = db.Column(String(128), nullable=False, index=True)
    family = db.Column(String(128), nullable=False, index=True)
    current_version = db.Column(String(16), nullable=False, default="v1.0")
    approved_jds_count = db.Column(Integer, nullable=False, default=0)
    feedback_submissions_count = db.Column(Integer, nullable=False, default=0)
    avg_quality_rating = db.Column(Float, nullable=True)
    edit_ratio_trend = db.Column(JSON, nullable=True)
    last_updated = db.Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


# ── Community skills (replaces kb/{dept}/{family}/feedback/custom_skills.jsonl) ─

class CommunitySkill(db.Model):
    __tablename__ = "community_skills"

    id = db.Column(String(36), primary_key=True, default=_uuid)
    department = db.Column(String(128), nullable=False, index=True)
    family = db.Column(String(128), nullable=False, index=True)
    skill_raw = db.Column(String(255), nullable=False)
    skill_key = db.Column(String(255), nullable=False, index=True)
    user_email = db.Column(String(255), nullable=False)
    jd_id = db.Column(String(64), nullable=True)
    role_title = db.Column(String(255), nullable=True)
    created_at = db.Column(DateTime, nullable=False, default=_utcnow)
