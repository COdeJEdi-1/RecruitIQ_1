"""
Multi-user authentication blueprint for DarwinBox.
Reads credentials from the shared MySQL `users` table (mirrored via
database.models.User — same table jd_prototype's users.json migration writes to).
Roles: 'admin' sees all data; 'user' sees only their own.
"""

from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import db
from database.models import User

auth_bp = Blueprint("auth", __name__)


def _find_user(email: str) -> dict | None:
    user = User.query.filter(db.func.lower(User.email) == email.lower()).first()
    return user.to_dict() if user else None


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
