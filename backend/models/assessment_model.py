import json
from datetime import datetime

from .db import get_connection


def save_assessment(profile: dict, result: dict, patient_name: str, user_id: int | None = None) -> None:
    risk_scores = result.get("risk_scores", {})
    symptoms = profile.get("Symptoms", [])
    if isinstance(symptoms, list):
        symptoms_text = ", ".join(str(x) for x in symptoms)
    else:
        symptoms_text = str(symptoms or "")

    avg_score = 0.0
    try:
        vals = [int(str(v).replace("%", "")) for v in risk_scores.values()]
        avg_score = round(sum(vals) / len(vals), 2) if vals else 0.0
    except Exception:
        avg_score = 0.0

    conn = get_connection()
    conn.execute(
        """
        INSERT INTO assessments (
            created_at, user_id, patient_name, age, gender, bmi, symptoms,
            thyroid_risk, diabetes_risk, pcos_risk, adrenal_risk, metabolic_risk,
            risk_score, profile_json, result_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.utcnow().isoformat(timespec="seconds") + "Z",
            user_id,
            patient_name,
            profile.get("Age"),
            profile.get("Gender"),
            profile.get("BMI"),
            symptoms_text,
            risk_scores.get("thyroid"),
            risk_scores.get("diabetes"),
            risk_scores.get("pcos"),
            risk_scores.get("adrenal"),
            risk_scores.get("metabolic"),
            avg_score,
            json.dumps(profile),
            json.dumps(result),
        ),
    )
    conn.commit()
    conn.close()


def get_dashboard_assessments(limit: int | None = None):
    conn = get_connection()
    query = (
        "SELECT id, created_at, user_id, patient_name, age, gender, bmi, symptoms, "
        "thyroid_risk, diabetes_risk, pcos_risk, adrenal_risk, metabolic_risk, "
        "risk_score, result_json FROM assessments ORDER BY id DESC"
    )
    if limit is not None:
        query += f" LIMIT {int(limit)}"
    rows = conn.execute(query).fetchall()
    conn.close()
    return rows


def get_all_assessments_json():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM assessments ORDER BY id DESC").fetchall()
    conn.close()

    out = []
    for row in rows:
        item = dict(row)
        for key in ["profile_json", "result_json"]:
            if item.get(key):
                item[key] = json.loads(item[key])
        out.append(item)
    return out


def get_all_assessment_rows():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, created_at, user_id, patient_name, age, gender, bmi, symptoms,
               thyroid_risk, diabetes_risk, pcos_risk, adrenal_risk, metabolic_risk, risk_score
        FROM assessments
        ORDER BY id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_assessments(user_id: int, limit: int = 50) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, created_at, patient_name, thyroid_risk, diabetes_risk, pcos_risk, adrenal_risk, metabolic_risk, risk_score
        FROM assessments
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, int(limit)),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
