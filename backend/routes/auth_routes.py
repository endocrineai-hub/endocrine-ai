from functools import wraps

from flask import Blueprint, redirect, render_template, request, session, url_for

from ..models.assessment_model import get_user_assessments
from ..models.user_model import create_user, verify_user

auth_bp = Blueprint("auth", __name__)


def user_required(view_fn):
    @wraps(view_fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.user_login"))
        return view_fn(*args, **kwargs)

    return wrapped


@auth_bp.route("/signup", methods=["GET", "POST"])
def user_signup():
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        ok, msg = create_user(name, email, password)
        if ok:
            return redirect(url_for("auth.user_login"))
        return render_template("user_signup.html", error=msg)
    return render_template("user_signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        user = verify_user(email, password)
        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            return redirect(url_for("auth.user_dashboard"))
        return render_template("user_login.html", error="Invalid email or password")
    return render_template("user_login.html")


@auth_bp.route("/logout")
def user_logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("user_email", None)
    return redirect(url_for("public.index"))


@auth_bp.route("/dashboard")
@user_required
def user_dashboard():
    assessments = get_user_assessments(session["user_id"])
    return render_template("user_dashboard.html", assessments=assessments)
