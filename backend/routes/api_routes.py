from flask import Blueprint, jsonify, request

from ..models.assessment_model import save_assessment
from ..services.chat_service import generate_chat_reply
from ..services.model_inference import model_available, predict_with_models
from ..services.risk_engine import calculate_risk, extract_markers

api_bp = Blueprint("api", __name__)


def validate_profile(profile: dict) -> list[str]:
    errors = []
    required = [
        "Age",
        "Gender",
        "BMI",
        "Sleep quality",
        "Stress level",
        "Exercise frequency",
        "Diet type",
    ]
    for field in required:
        if profile.get(field) in [None, ""]:
            errors.append(f"Missing required field: {field}")

    try:
        age = int(profile.get("Age", 0))
        if age < 1 or age > 120:
            errors.append("Age must be between 1 and 120")
    except (TypeError, ValueError):
        errors.append("Age must be a valid number")

    try:
        bmi = float(profile.get("BMI", 0))
        if bmi < 10 or bmi > 80:
            errors.append("BMI must be between 10 and 80")
    except (TypeError, ValueError):
        errors.append("BMI must be a valid number")

    return errors


@api_bp.route("/api/assess", methods=["POST"])
def assess_profile():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"status": "error", "message": "Invalid JSON payload"}), 400

    profile = payload.get("profile", {})
    if not isinstance(profile, dict):
        return jsonify({"status": "error", "message": "profile must be an object"}), 400

    errors = validate_profile(profile)
    if errors:
        return jsonify({"status": "error", "message": "Validation failed", "errors": errors}), 400

    lab_text = payload.get("lab_report_text", "")
    extracted_markers = extract_markers(lab_text) if lab_text else {}

    explicit_labs = profile.get("Lab results (optional)", {}) or {}
    merged_markers = {**extracted_markers, **explicit_labs}
    result = calculate_risk(profile, merged_markers)

    # Use trained ML models when available, with safe fallback to rule engine.
    ml_result = predict_with_models(profile, merged_markers)
    if ml_result:
        result["risk_scores"] = ml_result["risk_scores"]
        result["risk_level"] = ml_result["risk_level"]
        result["prediction_source"] = ml_result["prediction_source"]
        result["explanation"] = (
            result.get("explanation", "") + " " + ml_result.get("explanation", "")
        ).strip()
    else:
        result["prediction_source"] = "rule_engine"

    save_assessment(profile, result, payload.get("patient_name", "Anonymous"))

    return jsonify(
        {
            "status": "success",
            "extracted_markers": extracted_markers,
            "assessment": result,
        }
    )


@api_bp.route("/api/extract-markers", methods=["POST"])
def api_extract_markers():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"status": "error", "message": "Invalid JSON payload"}), 400

    text = payload.get("lab_report_text", "")
    if not isinstance(text, str):
        return jsonify({"status": "error", "message": "lab_report_text must be a string"}), 400

    return jsonify({"status": "success", "extracted_markers": extract_markers(text)})


@api_bp.route("/api/chat", methods=["POST"])
def api_chat():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"status": "error", "message": "Invalid JSON payload"}), 400

    message = payload.get("message", "")
    assessment = payload.get("assessment", {}) or {}

    if not isinstance(message, str) or not message.strip():
        return jsonify({"status": "error", "message": "message is required"}), 400

    if not isinstance(assessment, dict):
        return jsonify({"status": "error", "message": "assessment must be an object"}), 400

    reply = generate_chat_reply(message, assessment)
    return jsonify(
        {
            "status": "success",
            "reply": reply,
            "disclaimer": "This is preventive risk guidance, not a medical diagnosis.",
        }
    )


@api_bp.route("/api/model-status", methods=["GET"])
def api_model_status():
    return jsonify({"status": "success", "model_available": model_available()})
