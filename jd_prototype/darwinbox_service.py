"""
darwinbox_service.py — Mock Darwinbox / Job Board integration service.

All functions are structured for real-API swap-in:
  - publish_to_darwinbox()   → replace with real Darwinbox POST /jobs
  - publish_to_platform()    → replace with real LinkedIn / Naukri API call
  - fetch_darwinbox_jobs()   → replace with real Darwinbox GET /jobs
  - fetch_job_postings()     → replace with real platform API status fetch
  - fetch_candidates()       → replace with real Darwinbox GET /candidates

Phase 3: persistence backed by MySQL via SQLAlchemy (database/models.py) —
replaces the previous darwin_data/*.json flat-file storage.
"""

from datetime import datetime

from database.db import db
from database.models import ActivityLog, Candidate, DarwinboxJob, JobPosting


def _log_activity(user_id: str, action: str, entity_type: str, entity_id: str, metadata: dict = None):
    """Insert an entry into the activity log."""
    try:
        row = ActivityLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            log_metadata=metadata or {},
        )
        db.session.add(row)
        db.session.commit()
    except Exception:
        db.session.rollback()


# ── Dict mapping helpers ───────────────────────────────────────────────────────

def _darwinbox_job_to_dict(row: DarwinboxJob) -> dict:
    return {
        "darwinbox_job_id": row.darwinbox_job_id,
        "jd_id": row.jd_id,
        "role_title": row.role_title,
        "jd_text": row.jd_text,
        "version": row.version,
        "is_active": row.is_active,
        "status": row.status,
        "published_at": row.published_at.isoformat() if row.published_at else None,
        "created_by": row.created_by,
    }


def _posting_to_dict(row: JobPosting) -> dict:
    return {
        "posting_id": row.posting_id,
        "darwinbox_job_id": row.darwinbox_job_id,
        "platform": row.platform,
        "application_link": row.application_link,
        "status": row.status,
        "posted_at": row.posted_at.isoformat() if row.posted_at else None,
    }


def _candidate_to_dict(row: Candidate) -> dict:
    d = {
        "candidate_id": row.candidate_id,
        "darwinbox_job_id": row.darwinbox_job_id,
        "platform_source": row.platform_source,
        "name": row.name,
        "email": row.email,
        "phone": row.phone,
        "resume_file": row.resume_file,
        "applied_at": row.applied_at.isoformat() if row.applied_at else None,
        "consent_given": row.consent_given,
        "consent_timestamp": row.consent_timestamp.isoformat() if row.consent_timestamp else None,
        "consent_text": row.consent_text,
    }
    if row.resume_profile is not None:
        d["resume_profile"] = row.resume_profile
    if row.resume_profile_extracted_at is not None:
        d["resume_profile_extracted_at"] = row.resume_profile_extracted_at.isoformat()
    return d


# ── Darwinbox Jobs ────────────────────────────────────────────────────────────

def publish_to_darwinbox(jd_id: str, role_title: str, jd_text: str, created_by: str = None) -> dict:
    """
    Mock: push approved JD to Darwinbox.
    Returns the new darwinbox_job record.
    Handles versioning: deactivates previous active job for same role, bumps version.
    """
    try:
        # Find existing active job(s) for this role_title (case-insensitive)
        existing = DarwinboxJob.query.filter(
            db.func.lower(DarwinboxJob.role_title) == role_title.lower(),
            DarwinboxJob.is_active.is_(True),
        ).all()

        prev_version = 0
        for job in existing:
            job.is_active = False
            job.status = "deprecated"
            prev_version = job.version

        new_job = DarwinboxJob(
            jd_id=jd_id,
            role_title=role_title,
            jd_text=jd_text,
            version=prev_version + 1,
            is_active=True,
            status="published",
            published_at=datetime.now(),
            created_by=created_by,
        )
        db.session.add(new_job)
        db.session.commit()
        result = _darwinbox_job_to_dict(new_job)
    except Exception:
        db.session.rollback()
        raise

    _log_activity(created_by or "system", "jd_published", "darwinbox_job",
                  result["darwinbox_job_id"], {"role_title": role_title, "jd_id": jd_id})
    return result


def fetch_darwinbox_jobs(active_only: bool = True) -> list:
    """Return all Darwinbox jobs, optionally filtered to active only."""
    try:
        q = DarwinboxJob.query
        if active_only:
            q = q.filter_by(is_active=True)
        return [_darwinbox_job_to_dict(j) for j in q.all()]
    except Exception:
        return []


def get_darwinbox_job(darwinbox_job_id: str) -> dict | None:
    """Fetch a single Darwinbox job by ID."""
    try:
        row = DarwinboxJob.query.get(darwinbox_job_id)
        return _darwinbox_job_to_dict(row) if row else None
    except Exception:
        return None


# ── Job Postings (platform distribution) ─────────────────────────────────────

def publish_to_platform(darwinbox_job_id: str, platform: str, base_url: str) -> dict:
    """
    Mock: publish a Darwinbox job to LinkedIn or Naukri.
    Returns posting record with generated application_link.
    Idempotent: if already posted to this platform, returns existing posting.
    """
    try:
        existing = JobPosting.query.filter_by(
            darwinbox_job_id=darwinbox_job_id, platform=platform
        ).first()
        if existing is not None:
            return _posting_to_dict(existing)

        posting = JobPosting(
            darwinbox_job_id=darwinbox_job_id,
            platform=platform,
            application_link=f"{base_url}/apply/{platform}/{darwinbox_job_id}",
            status="active",
            posted_at=datetime.now(),
        )
        db.session.add(posting)
        db.session.commit()
        return _posting_to_dict(posting)
    except Exception:
        db.session.rollback()
        raise


def fetch_job_postings(darwinbox_job_id: str | None = None) -> list:
    """Return all postings, optionally filtered by darwinbox_job_id."""
    try:
        q = JobPosting.query
        if darwinbox_job_id:
            q = q.filter_by(darwinbox_job_id=darwinbox_job_id)
        return [_posting_to_dict(p) for p in q.all()]
    except Exception:
        return []


# ── Candidates ────────────────────────────────────────────────────────────────

# Consent copy shown on the public apply form — stored with each application for audit.
CONSENT_TEXT = (
    "I consent to Arvind Limited contacting me via phone, SMS, email, WhatsApp, and, where applicable, "
    "AI-assisted voice interactions for recruitment purposes, including application updates, interviews, "
    "candidate screening, assessments, and related hiring activities. "
    "Where AI-assisted interactions are used, I will be informed at the start. Where required, my consent "
    "will be obtained before any recorded interaction. I may withdraw my consent for future recruitment "
    "communications at any time by contacting Arvind Limited, subject to applicable legal and operational requirements."
)


def submit_candidate(
    darwinbox_job_id: str,
    platform_source: str,
    name: str,
    email: str,
    phone: str,
    resume_file: str,
    consent_given: bool = False,
    consent_timestamp: str | None = None,
) -> dict:
    """Store a candidate application submission."""
    now = datetime.now()

    consent_dt = None
    if consent_timestamp:
        try:
            consent_dt = datetime.fromisoformat(consent_timestamp)
        except ValueError:
            consent_dt = now
    elif consent_given:
        consent_dt = now

    try:
        candidate = Candidate(
            darwinbox_job_id=darwinbox_job_id,
            platform_source=platform_source,
            name=name,
            email=email,
            phone=phone,
            resume_file=resume_file,
            applied_at=now,
            consent_given=bool(consent_given),
            consent_timestamp=consent_dt,
            consent_text=CONSENT_TEXT if consent_given else None,
        )
        db.session.add(candidate)
        db.session.commit()
        return _candidate_to_dict(candidate)
    except Exception:
        db.session.rollback()
        raise


def fetch_candidates(darwinbox_job_id: str | None = None, platform_source: str | None = None) -> list:
    """Return candidates, filterable by job and/or platform."""
    try:
        q = Candidate.query
        if darwinbox_job_id:
            q = q.filter_by(darwinbox_job_id=darwinbox_job_id)
        if platform_source:
            q = q.filter_by(platform_source=platform_source)
        return [_candidate_to_dict(c) for c in q.all()]
    except Exception:
        return []
