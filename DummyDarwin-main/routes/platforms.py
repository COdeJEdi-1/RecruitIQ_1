"""
Platform preview pages — LinkedIn and Naukri job posting views.
"""

import json
import sys
from pathlib import Path

from flask import Blueprint, render_template, request

platforms_bp = Blueprint("platforms", __name__)

_JD_PROTOTYPE_DIR = Path(__file__).parent.parent.parent / "jd_prototype"
_DARWIN_DATA = _JD_PROTOTYPE_DIR / "darwin_data"

if str(_JD_PROTOTYPE_DIR) not in sys.path:
    sys.path.insert(0, str(_JD_PROTOTYPE_DIR))

from jd_constants import (  # noqa: E402
    JD_FOOTER_HEADING,
    JD_FOOTER_TEXT,
    JD_FOOTER_BRAND_LABEL,
    JD_FOOTER_BRAND_NAME,
)

_FOOTER_CTX = {
    "jd_footer_heading": JD_FOOTER_HEADING,
    "jd_footer_text": JD_FOOTER_TEXT,
    "jd_footer_brand_label": JD_FOOTER_BRAND_LABEL,
    "jd_footer_brand_name": JD_FOOTER_BRAND_NAME,
}


def _load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _get_job(job_id):
    for j in _load(_DARWIN_DATA / "darwinbox_jobs.json"):
        if j.get("darwinbox_job_id") == job_id:
            return j
    return None


@platforms_bp.route("/linkedin")
def linkedin():
    job_id = request.args.get("job_id", "")
    job = _get_job(job_id) if job_id else None
    return render_template("linkedin.html", job=job, **_FOOTER_CTX)


@platforms_bp.route("/naukri")
def naukri():
    job_id = request.args.get("job_id", "")
    job = _get_job(job_id) if job_id else None
    return render_template("naukri.html", job=job, **_FOOTER_CTX)
