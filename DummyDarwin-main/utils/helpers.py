"""
Shared helper functions for file validation, naming, and storage paths.
"""

import os
import uuid

from werkzeug.utils import secure_filename

from config import Config


def get_allowed_extensions(category):
    """Return the allowed extensions for a given document category."""
    if category == Config.CATEGORY_CANDIDATE:
        return Config.ALLOWED_EXTENSIONS_CANDIDATE
    return Config.ALLOWED_EXTENSIONS


def format_allowed_extensions(category):
    """Return a human-readable list of allowed formats for error messages."""
    extensions = sorted(get_allowed_extensions(category))
    return ", ".join(ext.upper() for ext in extensions)


def allowed_file(filename, category):
    """Return True if the file extension is allowed for the given category."""
    if not filename or "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in get_allowed_extensions(category)


def generate_unique_filename(original_filename):
    """
    Sanitize the original filename and prepend a UUID to prevent collisions.
    Returns a tuple of (stored_filename, original_filename).
    """
    safe_name = secure_filename(original_filename)
    if not safe_name:
        safe_name = "document"

    unique_prefix = uuid.uuid4().hex[:12]
    stored_filename = f"{unique_prefix}_{safe_name}"
    return stored_filename, original_filename


def get_upload_folder(category):
    """Return the physical upload directory for a given document category."""
    if category == Config.CATEGORY_JD:
        return Config.UPLOAD_FOLDER_JD
    if category == Config.CATEGORY_CANDIDATE:
        return Config.UPLOAD_FOLDER_CANDIDATE
    raise ValueError(f"Unknown category: {category}")


def save_uploaded_file(file_storage, category):
    """
    Validate and persist an uploaded file to disk.
    Returns (stored_filename, original_filename, full_filepath) on success.
    Raises ValueError for invalid files.
    """
    if not file_storage or not file_storage.filename:
        raise ValueError("No file selected.")

    original_filename = file_storage.filename

    if not allowed_file(original_filename, category):
        raise ValueError(
            f"Invalid file type. Allowed formats: {format_allowed_extensions(category)}."
        )

    stored_filename, original_filename = generate_unique_filename(original_filename)
    upload_folder = get_upload_folder(category)
    full_filepath = os.path.join(upload_folder, stored_filename)

    file_storage.save(full_filepath)

    return stored_filename, original_filename, full_filepath


def delete_file_from_disk(filepath):
    """Remove a file from disk if it exists. Returns True if deleted."""
    if filepath and os.path.isfile(filepath):
        os.remove(filepath)
        return True
    return False
