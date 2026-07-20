"""
SQLAlchemy models for the Darwinbox portal (MySQL-ready).

Phase 3: this is the sole runtime models module. `Document` is owned by this
module. The remaining classes below are read/write mirrors of tables owned by
the sibling `jd_prototype` module (same MySQL database, same __tablename__ —
each Flask process defines its own model classes bound to its own `db`
instance, but both point at the identical physical tables). `download_requests`
is the only table owned by this module among the mirrors.
"""

import uuid
from datetime import datetime, timezone

from database.db import db


def _uuid():
    return str(uuid.uuid4())


def _utcnow():
    return datetime.now(timezone.utc)


def _iso(value):
    """Render a datetime as an ISO-8601 string, matching the shape the old
    JSON files stored (so templates/routes that slice/compare strings keep
    working unchanged)."""
    return value.isoformat() if value else None


class Document(db.Model):
    """Represents an uploaded document in the JD or Candidate library."""

    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    filepath = db.Column(db.String(512), nullable=False)

    def formatted_date(self):
        """Return a human-readable upload date for templates."""
        if self.upload_date:
            return self.upload_date.strftime("%b %d, %Y · %I:%M %p")
        return "Unknown"

    def __repr__(self):
        return f"<Document {self.id}: {self.original_filename} ({self.category})>"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    username = db.Column(db.String(255), unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    full_name = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(512), nullable=True)
    role = db.Column(db.String(32), nullable=False, default="employee")
    auth_provider = db.Column(db.String(32), nullable=False, default="local")
    magic_token = db.Column(db.String(128), nullable=True)
    magic_token_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)

    def to_dict(self):
        """Key names match the legacy users.json shape (`id` -> `user_id`)."""
        return {
            "user_id": self.id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "role": self.role,
            "auth_provider": self.auth_provider,
            "created_at": _iso(self.created_at),
            "updated_at": _iso(self.updated_at),
        }


class DarwinboxJob(db.Model):
    __tablename__ = "darwinbox_jobs"

    darwinbox_job_id = db.Column(db.String(36), primary_key=True, default=_uuid)
    jd_id = db.Column(db.String(64), nullable=True, index=True)
    role_title = db.Column(db.String(255), nullable=False)
    jd_text = db.Column(db.Text, nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    status = db.Column(db.String(32), nullable=False, default="published")
    published_at = db.Column(db.DateTime, nullable=False, default=_utcnow)
    created_by = db.Column(db.String(255), nullable=True)
    position_level = db.Column(db.String(32), nullable=False, default="junior")
    shortlist_threshold = db.Column(db.Integer, nullable=True)
    # Owned by jd_prototype; read here for the linkedin.html/naukri.html previews.
    jd_requirements = db.Column(db.JSON, nullable=True)
    jd_requirements_extracted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "darwinbox_job_id": self.darwinbox_job_id,
            "jd_id": self.jd_id,
            "role_title": self.role_title,
            "jd_text": self.jd_text,
            "version": self.version,
            "is_active": self.is_active,
            "status": self.status,
            "published_at": _iso(self.published_at),
            "created_by": self.created_by,
            "position_level": self.position_level,
            "shortlist_threshold": self.shortlist_threshold,
            "jd_requirements": self.jd_requirements,
        }


class Candidate(db.Model):
    __tablename__ = "candidates"

    candidate_id = db.Column(db.String(36), primary_key=True, default=_uuid)
    darwinbox_job_id = db.Column(db.String(36), nullable=False, index=True)
    platform_source = db.Column(db.String(32), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(32), nullable=True)
    resume_file = db.Column(db.String(512), nullable=True)
    applied_at = db.Column(db.DateTime, nullable=False, default=_utcnow)
    consent_given = db.Column(db.Boolean, nullable=False, default=False)
    consent_timestamp = db.Column(db.DateTime, nullable=True)
    consent_text = db.Column(db.Text, nullable=True)
    # Owned by jd_prototype (scoring_service.py); declared here only so this
    # model's schema matches exactly, making table creation order-independent.
    resume_profile = db.Column(db.JSON, nullable=True)
    resume_profile_extracted_at = db.Column(db.DateTime, nullable=True)
    # Set the moment a recruiter clicks the manual-call button (single or bulk)
    # -- independent of whether the call has actually connected/completed yet,
    # so the UI can show "Call Triggered" immediately instead of waiting for
    # the OmniDimension sheet to sync a result.
    manual_call_triggered_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "candidate_id": self.candidate_id,
            "darwinbox_job_id": self.darwinbox_job_id,
            "platform_source": self.platform_source,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "resume_file": self.resume_file,
            "applied_at": _iso(self.applied_at) or "",
            "consent_given": self.consent_given,
            "consent_timestamp": _iso(self.consent_timestamp),
            "consent_text": self.consent_text,
            "manual_call_triggered_at": _iso(self.manual_call_triggered_at),
        }


class CandidateScore(db.Model):
    __tablename__ = "candidate_scores"

    score_id = db.Column(db.String(36), primary_key=True, default=_uuid)
    candidate_id = db.Column(db.String(36), nullable=False, index=True)
    darwinbox_job_id = db.Column(db.String(36), nullable=False, index=True)
    overall_score = db.Column(db.Float, nullable=False)
    skills_score = db.Column(db.Float, nullable=True)
    experience_score = db.Column(db.Float, nullable=True)
    education_score = db.Column(db.Float, nullable=True)
    title_relevance_score = db.Column(db.Float, nullable=True)
    domain_score = db.Column(db.Float, nullable=True)
    score_breakdown = db.Column(db.JSON, nullable=True)
    scored_at = db.Column(db.DateTime, nullable=False, default=_utcnow)

    def to_dict(self):
        return {
            "score_id": self.score_id,
            "candidate_id": self.candidate_id,
            "darwinbox_job_id": self.darwinbox_job_id,
            "overall_score": self.overall_score,
            "skills_score": self.skills_score,
            "experience_score": self.experience_score,
            "education_score": self.education_score,
            "title_relevance_score": self.title_relevance_score,
            "domain_score": self.domain_score,
            "score_breakdown": self.score_breakdown,
            "scored_at": _iso(self.scored_at),
        }


class ActivityLog(db.Model):
    __tablename__ = "activity_log"

    log_id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(db.String(255), nullable=True, index=True)
    action = db.Column(db.String(64), nullable=False)
    entity_type = db.Column(db.String(64), nullable=True)
    entity_id = db.Column(db.String(64), nullable=True)
    log_metadata = db.Column("metadata", db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow, index=True)

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "metadata": self.log_metadata,
            "created_at": _iso(self.created_at),
        }


class DownloadRequest(db.Model):
    __tablename__ = "download_requests"

    request_id = db.Column(db.String(36), primary_key=True, default=_uuid)
    requester_id = db.Column(db.String(255), nullable=False, index=True)
    requester_name = db.Column(db.String(255), nullable=True)
    filters = db.Column(db.JSON, nullable=True)
    match_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(32), nullable=False, default="pending", index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.String(255), nullable=True)
    reviewer_name = db.Column(db.String(255), nullable=True)
    reject_reason = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "requester_id": self.requester_id,
            "requester_name": self.requester_name,
            "filters": self.filters,
            "match_count": self.match_count,
            "status": self.status,
            "created_at": _iso(self.created_at),
            "reviewed_at": _iso(self.reviewed_at),
            "reviewed_by": self.reviewed_by,
            "reviewer_name": self.reviewer_name,
            "reject_reason": self.reject_reason,
        }
