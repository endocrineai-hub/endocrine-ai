import json
from datetime import datetime

from .db import get_connection


def save_assessment(profile: dict, result: dict, patient_name: str) -> None:
    risk_scores = result.get("risk_scores", {})
    conn = get_connection()
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


def get_dashboard_assessments(limit: int | None = None):
    conn = get_connection()
    query = (
        "SELECT id, created_at, patient_name, age, gender, bmi, "
        "thyroid_risk, diabetes_risk, pcos_risk, adrenal_risk, metabolic_risk, "
        "result_json "
        "FROM assessments ORDER BY id DESC"
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
        SELECT id, created_at, patient_name, age, gender, bmi,
               thyroid_risk, diabetes_risk, pcos_risk, adrenal_risk, metabolic_risk
        FROM assessments
        ORDER BY id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
