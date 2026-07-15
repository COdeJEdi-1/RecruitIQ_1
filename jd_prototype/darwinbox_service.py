"""
darwinbox_service.py — Mock Darwinbox / Job Board integration service.

All functions are structured for real-API swap-in:
  - publish_to_darwinbox()   → replace with real Darwinbox POST /jobs
  - publish_to_platform()    → replace with real LinkedIn / Naukri API call
  - fetch_darwinbox_jobs()   → replace with real Darwinbox GET /jobs
  - fetch_job_postings()     → replace with real platform API status fetch
  - fetch_candidates()       → replace with real Darwinbox GET /candidates
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

# ── Storage paths (filesystem fallback when Supabase is not configured) ───────
_DATA_DIR = Path(__file__).parent / "darwin_data"
_DARWIN_JOBS_FILE = _DATA_DIR / "darwinbox_jobs.json"
_JOB_POSTINGS_FILE = _DATA_DIR / "job_postings.json"
_CANDIDATES_FILE = _DATA_DIR / "candidates.json"
_ACTIVITY_FILE = _DATA_DIR / "activity_log.json"


def _ensure_store():
    _DATA_DIR.mkdir(exist_ok=True)
    for f in [_DARWIN_JOBS_FILE, _JOB_POSTINGS_FILE, _CANDIDATES_FILE, _ACTIVITY_FILE]:
        if not f.exists():
            f.write_text("[]", encoding="utf-8")


def _log_activity(user_id: str, action: str, entity_type: str, entity_id: str, metadata: dict = None):
    """Append an entry to the activity log."""
    try:
        log = _load(_ACTIVITY_FILE)
        log.append({
            "log_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
        })
        _save(_ACTIVITY_FILE, log)
    except Exception:
        pass


def _load(path: Path) -> list:
    _ensure_store()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save(path: Path, data: list):
    _ensure_store()
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


# ── Darwinbox Jobs ────────────────────────────────────────────────────────────

def publish_to_darwinbox(jd_id: str, role_title: str, jd_text: str, created_by: str = None) -> dict:
    """
    Mock: push approved JD to Darwinbox.
    Returns the new darwinbox_job record.
    Handles versioning: deactivates previous active job for same role, bumps version.
    """
    jobs = _load(_DARWIN_JOBS_FILE)

    # Find existing active job for this role_title
    prev_version = 0
    for job in jobs:
        if job["role_title"].lower() == role_title.lower() and job["is_active"]:
            job["is_active"] = False
            job["status"] = "deprecated"
            prev_version = job["version"]

    new_job = {
        "darwinbox_job_id": str(uuid.uuid4()),
        "jd_id": jd_id,
        "role_title": role_title,
        "jd_text": jd_text,
        "version": prev_version + 1,
        "is_active": True,
        "status": "published",
        "published_at": datetime.now().isoformat(),
        "created_by": created_by,
    }
    jobs.append(new_job)
    _save(_DARWIN_JOBS_FILE, jobs)
    _log_activity(created_by or "system", "jd_published", "darwinbox_job",
                  new_job["darwinbox_job_id"], {"role_title": role_title, "jd_id": jd_id})
    return new_job


def fetch_darwinbox_jobs(active_only: bool = True) -> list:
    """Return all Darwinbox jobs, optionally filtered to active only."""
    jobs = _load(_DARWIN_JOBS_FILE)
    if active_only:
        return [j for j in jobs if j["is_active"]]
    return jobs


def get_darwinbox_job(darwinbox_job_id: str) -> dict | None:
    """Fetch a single Darwinbox job by ID."""
    for job in _load(_DARWIN_JOBS_FILE):
        if job["darwinbox_job_id"] == darwinbox_job_id:
            return job
    return None


# ── Job Postings (platform distribution) ─────────────────────────────────────

def publish_to_platform(darwinbox_job_id: str, platform: str, base_url: str) -> dict:
    """
    Mock: publish a Darwinbox job to LinkedIn or Naukri.
    Returns posting record with generated application_link.
    Idempotent: if already posted to this platform, returns existing posting.
    """
    postings = _load(_JOB_POSTINGS_FILE)

    # Idempotent — return existing if already posted
    for p in postings:
        if p["darwinbox_job_id"] == darwinbox_job_id and p["platform"] == platform:
            return p

    posting = {
        "posting_id": str(uuid.uuid4()),
        "darwinbox_job_id": darwinbox_job_id,
        "platform": platform,
        "application_link": f"{base_url}/apply/{platform}/{darwinbox_job_id}",
        "status": "active",
        "posted_at": datetime.now().isoformat(),
    }
    postings.append(posting)
    _save(_JOB_POSTINGS_FILE, postings)
    return posting


def fetch_job_postings(darwinbox_job_id: str | None = None) -> list:
    """Return all postings, optionally filtered by darwinbox_job_id."""
    postings = _load(_JOB_POSTINGS_FILE)
    if darwinbox_job_id:
        return [p for p in postings if p["darwinbox_job_id"] == darwinbox_job_id]
    return postings


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
    candidates = _load(_CANDIDATES_FILE)
    now = datetime.now().isoformat()
    candidate = {
        "candidate_id": str(uuid.uuid4()),
        "darwinbox_job_id": darwinbox_job_id,
        "platform_source": platform_source,
        "name": name,
        "email": email,
        "phone": phone,
        "resume_file": resume_file,
        "applied_at": now,
        "consent_given": bool(consent_given),
        "consent_timestamp": consent_timestamp or (now if consent_given else None),
        "consent_text": CONSENT_TEXT if consent_given else None,
    }
    candidates.append(candidate)
    _save(_CANDIDATES_FILE, candidates)
    return candidate


def fetch_candidates(darwinbox_job_id: str | None = None, platform_source: str | None = None) -> list:
    """Return candidates, filterable by job and/or platform."""
    candidates = _load(_CANDIDATES_FILE)
    if darwinbox_job_id:
        candidates = [c for c in candidates if c["darwinbox_job_id"] == darwinbox_job_id]
    if platform_source:
        candidates = [c for c in candidates if c["platform_source"] == platform_source]
    return candidates
