"""
Platform preview pages — LinkedIn and Naukri job posting views.
"""

import sys
from pathlib import Path

from flask import Blueprint, render_template, request

from database.models import DarwinboxJob

platforms_bp = Blueprint("platforms", __name__)

_JD_PROTOTYPE_DIR = Path(__file__).parent.parent.parent / "jd_prototype"

if str(_JD_PROTOTYPE_DIR) not in sys.path:
    # Appended (not prepended) so this app's own same-named packages
    # (utils, database, config, ...) keep resolving to themselves
    # elsewhere in this process; jd_prototype is only a fallback for
    # names unique to it, like `jd_constants`.
    sys.path.append(str(_JD_PROTOTYPE_DIR))

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


def _get_job(job_id):
    job = DarwinboxJob.query.get(job_id)
    return job.to_dict() if job else None


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
