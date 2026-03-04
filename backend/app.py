import json
import os
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from .risk_engine import calculate_risk, extract_markers

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "app.db"


def generate_chat_reply(message: str, assessment: dict) -> str:
    msg = (message or "").strip().lower()
    risk_scores = (assessment or {}).get("risk_scores", {})
    risk_level = (assessment or {}).get("risk_level", {})
    tests = (assessment or {}).get("suggested_tests", [])
    actions = (assessment or {}).get("recommended_actions", [])

    if not msg:
        return "Please ask a question about your endocrine health risk report."

    if any(token in msg for token in ["highest", "most risk", "top risk"]):
        if not risk_scores:
            return "Run an assessment first, then I can explain your highest-risk area."
        numeric = {}
        for key, val in risk_scores.items():
            try:
                numeric[key] = int(str(val).replace("%", ""))
            except ValueError:
                continue
        if not numeric:
            return "I could not read risk percentages from the report. Please run the analysis again."
        top = max(numeric, key=numeric.get)
        return f"Your highest estimated risk is {top} at {numeric[top]}% ({risk_level.get(top, 'N/A')})."

    if any(token in msg for token in ["thyroid", "diabetes", "pcos", "adrenal", "metabolic"]):
        if not risk_scores:
            return "Please run the assessment first so I can explain condition-specific risk."
        for key in ["thyroid", "diabetes", "pcos", "adrenal", "metabolic"]:
            if key in msg:
                return (
                    f"{key.capitalize()} risk is {risk_scores.get(key, 'N/A')} "
                    f"with level {risk_level.get(key, 'N/A')}. "
                    "I can also suggest next tests or lifestyle priorities for this risk."
                )

    if any(token in msg for token in ["test", "lab", "checkup"]):
        if not tests:
            return "No test suggestions are available yet. Run an assessment first."
        return "Suggested tests: " + "; ".join(tests[:6])

    if any(token in msg for token in ["action", "improve", "reduce", "what should i do", "next step"]):
        if not actions:
            return "No recommendations are available yet. Run an assessment first."
        return "Top actions: " + "; ".join(actions[:4])

    if any(token in msg for token in ["can you diagnose", "diagnose", "cure", "medicine", "prescription"]):
        return (
            "I cannot diagnose disease or prescribe medicine. "
            "I provide risk screening guidance only. Please consult a licensed clinician."
        )

    return (
        "I can help explain your risk scores, likely triggers, suggested tests, and priority lifestyle actions. "
        "Try: 'What is my highest risk?' or 'What tests should I do next?'"
    )


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")
    app.config["ADMIN_USERNAME"] = os.getenv("ADMIN_USERNAME", "admin")
    app.config["ADMIN_PASSWORD"] = os.getenv("ADMIN_PASSWORD", "admin123")

    init_db()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            if username == app.config["ADMIN_USERNAME"] and password == app.config["ADMIN_PASSWORD"]:
                session["is_admin"] = True
                return redirect(url_for("admin_dashboard"))
            return render_template("admin_login.html", error="Invalid credentials")
        return render_template("admin_login.html")

    @app.route("/admin/logout")
    def admin_logout():
        session.clear()
        return redirect(url_for("admin_login"))

    def admin_required(view_fn):
        @wraps(view_fn)
        def wrapped(*args, **kwargs):
            if not session.get("is_admin"):
                return redirect(url_for("admin_login"))
            return view_fn(*args, **kwargs)

        return wrapped

    @app.route("/admin")
    @admin_required
    def admin_dashboard():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, created_at, patient_name, age, gender, bmi,
                   thyroid_risk, diabetes_risk, pcos_risk, adrenal_risk, metabolic_risk
            FROM assessments
            ORDER BY id DESC
            """
        ).fetchall()
        conn.close()
        return render_template("admin_dashboard.html", assessments=rows)

    @app.route("/api/assess", methods=["POST"])
    def assess_profile():
        payload = request.get_json(force=True)
        profile = payload.get("profile", {})

        lab_text = payload.get("lab_report_text", "")
        extracted_markers = extract_markers(lab_text) if lab_text else {}

        explicit_labs = profile.get("Lab results (optional)", {}) or {}
        merged_markers = {**extracted_markers, **explicit_labs}
        result = calculate_risk(profile, merged_markers)

        save_assessment(profile, result, payload.get("patient_name", "Anonymous"))

        return jsonify(
            {
                "status": "success",
                "extracted_markers": extracted_markers,
                "assessment": result,
            }
        )

    @app.route("/api/extract-markers", methods=["POST"])
    def api_extract_markers():
        payload = request.get_json(force=True)
        text = payload.get("lab_report_text", "")
        return jsonify({"extracted_markers": extract_markers(text)})

    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        payload = request.get_json(force=True)
        message = payload.get("message", "")
        assessment = payload.get("assessment", {}) or {}
        reply = generate_chat_reply(message, assessment)
        return jsonify(
            {
                "reply": reply,
                "disclaimer": "This is preventive risk guidance, not a medical diagnosis.",
            }
        )

    @app.route("/api/admin/assessments")
    @admin_required
    def list_assessments():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM assessments ORDER BY id DESC").fetchall()
        conn.close()

        out = []
        for row in rows:
            item = dict(row)
            for key in ["profile_json", "result_json"]:
                if item.get(key):
                    item[key] = json.loads(item[key])
            out.append(item)
        return jsonify({"assessments": out})

    return app


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            patient_name TEXT,
            age INTEGER,
            gender TEXT,
            bmi REAL,
            thyroid_risk TEXT,
            diabetes_risk TEXT,
            pcos_risk TEXT,
            adrenal_risk TEXT,
            metabolic_risk TEXT,
            profile_json TEXT,
            result_json TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_assessment(profile: dict, result: dict, patient_name: str) -> None:
    risk_scores = result.get("risk_scores", {})

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO assessments (
            created_at, patient_name, age, gender, bmi,
            thyroid_risk, diabetes_risk, pcos_risk, adrenal_risk, metabolic_risk,
            profile_json, result_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.utcnow().isoformat(timespec="seconds") + "Z",
            patient_name,
            profile.get("Age"),
            profile.get("Gender"),
            profile.get("BMI"),
            risk_scores.get("thyroid"),
            risk_scores.get("diabetes"),
            risk_scores.get("pcos"),
            risk_scores.get("adrenal"),
            risk_scores.get("metabolic"),
            json.dumps(profile),
            json.dumps(result),
        ),
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
