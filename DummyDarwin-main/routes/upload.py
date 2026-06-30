"""
Upload blueprint — handles file upload, view, download, and delete operations.
"""

import os

from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    send_file,
    url_for,
)

from config import Config
from models.models import Document
from utils.db import db
from utils.helpers import delete_file_from_disk, save_uploaded_file

upload_bp = Blueprint("upload", __name__)


def _handle_upload(category, success_message):
    """
    Shared upload handler for JD and Candidate libraries.
    Validates the file, saves to disk, and records metadata in SQLite.
    """
    if "file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("dashboard.index"))

    file = request.files["file"]

    try:
        stored_filename, original_filename, full_filepath = save_uploaded_file(
            file, category
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("dashboard.index"))

    document = Document(
        filename=stored_filename,
        original_filename=original_filename,
        category=category,
        filepath=full_filepath,
    )

    db.session.add(document)
    db.session.commit()

    flash(success_message, "success")
    return redirect(url_for("dashboard.index"))


@upload_bp.route("/upload/jd", methods=["POST"])
def upload_jd():
    """Upload a Job Description document."""
    return _handle_upload(
        Config.CATEGORY_JD,
        "Job Description uploaded successfully.",
    )


@upload_bp.route("/upload/candidate", methods=["POST"])
def upload_candidate():
    """Upload a Candidate resume document."""
    return _handle_upload(
        Config.CATEGORY_CANDIDATE,
        "Candidate document uploaded successfully.",
    )


def _get_document_or_redirect(document_id):
    """Fetch a document by ID or redirect to dashboard if not found."""
    document = Document.query.get(document_id)
    if not document:
        flash("Document not found.", "error")
        return None
    if not os.path.isfile(document.filepath):
        flash("File no longer exists on disk.", "error")
        return None
    return document


@upload_bp.route("/view/<int:document_id>")
def view_document(document_id):
    """Open a document inline in the browser."""
    document = _get_document_or_redirect(document_id)
    if not document:
        return redirect(url_for("dashboard.index"))

    return send_file(
        document.filepath,
        mimetype=_guess_mimetype(document.original_filename),
        as_attachment=False,
        download_name=document.original_filename,
    )


@upload_bp.route("/download/<int:document_id>")
def download_document(document_id):
    """Download a document as an attachment."""
    document = _get_document_or_redirect(document_id)
    if not document:
        return redirect(url_for("dashboard.index"))

    return send_file(
        document.filepath,
        as_attachment=True,
        download_name=document.original_filename,
    )


@upload_bp.route("/delete/<int:document_id>", methods=["POST"])
def delete_document(document_id):
    """Delete a document from storage and the database."""
    document = Document.query.get(document_id)

    if not document:
        flash("Document not found.", "error")
        return redirect(url_for("dashboard.index"))

    delete_file_from_disk(document.filepath)

    db.session.delete(document)
    db.session.commit()

    flash("Document deleted successfully.", "success")
    return redirect(url_for("dashboard.index"))


def _guess_mimetype(filename):
    """Return a best-guess MIME type for inline browser viewing."""
    extension = filename.rsplit(".", 1)[-1].lower() if filename else ""
    mime_map = {
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": (
            "application/vnd.openxmlformats-officedocument"
            ".wordprocessingml.document"
        ),
        "txt": "text/plain",
        "xls": "application/vnd.ms-excel",
        "xlsx": (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    }
    return mime_map.get(extension, "application/octet-stream")
