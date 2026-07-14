"""
Multi-user authentication blueprint for DarwinBox.
Reads credentials from shared darwin_data/users.json.
Roles: 'admin' sees all data; 'user' sees only their own.
"""

import json
import os
from functools import wraps
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__)

_USERS_FILE = Path(__file__).parent.parent.parent / "jd_prototype" / "darwin_data" / "users.json"


def _load_users() -> list:
    try:
        return json.loads(_USERS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _find_user(email: str) -> dict | None:
    for u in _load_users():
        if u.get("email", "").lower() == email.lower():
            return u
    return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login", next=request.url))
        if session.get("role") != "admin":
            flash("Admin access required.", "error")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated


def is_admin() -> bool:
    return session.get("role") == "admin"


def current_user_id() -> str | None:
    return session.get("user_id")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))

    error = None
    if request.method == "POST":
        email = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = _find_user(email)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            session["is_admin"] = (user["role"] == "admin")
            next_url = request.form.get("next") or url_for("dashboard.index")
            return redirect(next_url)
        else:
            error = "Invalid email or password."

    return render_template("login.html", error=error, next=request.args.get("next", ""))


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
