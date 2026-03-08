from functools import wraps
import json

from flask import Blueprint, Response, current_app, jsonify, redirect, render_template, request, session, url_for

from ..models.assessment_model import get_all_assessment_rows, get_all_assessments_json, get_dashboard_assessments
from ..services.analytics_service import build_dashboard_stats
from ..services.model_inference import model_available
from ..services.report_service import assessments_to_csv

admin_bp = Blueprint("admin", __name__)


def admin_required(view_fn):
    @wraps(view_fn)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin.admin_login"))
        return view_fn(*args, **kwargs)

    return wrapped


@admin_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        cfg_user = str(current_app.config["ADMIN_USERNAME"]).strip()
        cfg_pass = str(current_app.config["ADMIN_PASSWORD"]).strip()

        # Be user-friendly for demo usage.
        if username.lower() == cfg_user.lower() and password == cfg_pass:
            session["is_admin"] = True
            return redirect(url_for("admin.admin_dashboard"))
        return render_template("admin_login.html", error="Invalid credentials")
    return render_template("admin_login.html")


@admin_bp.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin.admin_login"))


@admin_bp.route("/admin")
@admin_required
def admin_dashboard():
    rows_raw = get_dashboard_assessments(limit=200)
    rows = []
    for r in rows_raw:
        item = dict(r)
        source = "rule_engine"
        if item.get("result_json"):
            try:
                source = json.loads(item["result_json"]).get("prediction_source", "rule_engine")
            except Exception:
                source = "rule_engine"
        item["prediction_source"] = source
        rows.append(item)
    stats = build_dashboard_stats(rows)
    return render_template(
        "admin_dashboard.html",
        assessments=rows,
        stats=stats,
        model_ready=model_available(),
    )


@admin_bp.route("/api/admin/assessments")
@admin_required
def list_assessments():
    return jsonify({"assessments": get_all_assessments_json()})


@admin_bp.route("/admin/export.csv")
@admin_required
def export_assessments_csv():
    rows = get_all_assessment_rows()
    csv_data = assessments_to_csv(rows)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=assessments_export.csv"},
    )
