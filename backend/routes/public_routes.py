from flask import Blueprint, render_template

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    return render_template("index.html")


@public_bp.route("/about")
def about():
    return render_template("about.html")


@public_bp.route("/methodology")
def methodology():
    return render_template("methodology.html")


@public_bp.route("/contact")
def contact():
    return render_template("contact.html")
