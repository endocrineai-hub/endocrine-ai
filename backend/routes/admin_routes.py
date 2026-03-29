from functools import wraps
import json

from flask import Blueprint, Response, jsonify, redirect, render_template, request, session, url_for

from ..models.admin_model import verify_admin_credentials
from ..models.assessment_model import (
    get_all_assessment_rows,
    get_all_assessments_json,
    get_dashboard_assessments,
    get_distinct_orphan_patient_names,
    get_user_recent_assessments_for_admin,
)
from ..models.user_model import (
    get_all_users_with_stats,
    get_user_with_stats,
    import_users_from_patient_names,
    update_user_profile,
)
from ..services.analytics_service import build_dashboard_stats
from ..services.model_inference import model_available
from ..services.openai_service import openai_available
from ..services.report_service import assessments_to_csv, assessments_to_pdf_bytes

admin_bp = Blueprint("admin", __name__)


def admin_required(view_fn):
    @wraps(view_fn)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin.admin_login"))
        return view_fn(*args, **kwargs)

    return wrapped


def _load_admin_dashboard_data():
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
    return rows, stats


@admin_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if verify_admin_credentials(username, password):
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
    _, stats = _load_admin_dashboard_data()
    return render_template(
        "admin_dashboard.html",
        stats=stats,
        model_ready=model_available(),
        openai_ready=openai_available(),
    )


@admin_bp.route("/admin/insights")
@admin_required
def admin_insights():
    _, stats = _load_admin_dashboard_data()
    return render_template(
        "admin_insights.html",
        stats=stats,
        model_ready=model_available(),
        openai_ready=openai_available(),
    )


@admin_bp.route("/admin/assessments")
@admin_required
def admin_assessments():
    rows, stats = _load_admin_dashboard_data()
    return render_template(
        "admin_assessments.html",
        assessments=rows,
        stats=stats,
        model_ready=model_available(),
        openai_ready=openai_available(),
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


@admin_bp.route("/admin/export.pdf")
@admin_required
def export_assessments_pdf():
    rows = get_all_assessment_rows()
    pdf_data = assessments_to_pdf_bytes(rows)
    return Response(
        pdf_data,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=assessments_export.pdf"},
    )


@admin_bp.route("/admin/users", methods=["GET", "POST"])
@admin_required
def admin_users():
    error = None
    success = None

    if request.method == "POST":
        action = request.form.get("action", "update_user")

        if action == "import_from_assessments":
            names = get_distinct_orphan_patient_names(limit=500)
            created_count = import_users_from_patient_names(names)
            if created_count > 0:
                success = f"Imported {created_count} user profile(s) from assessment records."
            else:
                error = "No importable patient records found. Create users from Register page first."
        else:
            user_id = request.form.get("user_id", type=int)
            name = request.form.get("name", "")
            email = request.form.get("email", "")
            password = request.form.get("password", "")

            if not user_id:
                error = "Invalid user selection"
            else:
                ok, msg = update_user_profile(user_id, name, email, password)
                if ok:
                    success = msg
                else:
                    error = msg

    users = get_all_users_with_stats()
    selected_id = request.args.get("user_id", type=int)
    if request.method == "POST":
        selected_id = request.form.get("user_id", type=int) or selected_id
    if not selected_id and users:
        selected_id = users[0]["id"]

    selected_user = get_user_with_stats(selected_id) if selected_id else None
    recent_assessments = (
        get_user_recent_assessments_for_admin(selected_id, limit=8) if selected_id else []
    )

    return render_template(
        "admin_users.html",
        users=users,
        selected_user=selected_user,
        recent_assessments=recent_assessments,
        error=error,
        success=success,
        model_ready=model_available(),
        openai_ready=openai_available(),
    )
