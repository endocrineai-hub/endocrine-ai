from flask import Blueprint, redirect, render_template, url_for

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    return render_template("index.html")


@public_bp.route("/about")
def about():
    return redirect(url_for("public.index"))


@public_bp.route("/methodology")
def methodology():
    return redirect(url_for("public.index"))


@public_bp.route("/contact")
def contact():
    return redirect(url_for("public.index"))


@public_bp.route("/start-assessment")
def start_assessment():
    return render_template("public_assessment.html")


@public_bp.route("/services")
def services():
    return redirect(url_for("public.index"))
