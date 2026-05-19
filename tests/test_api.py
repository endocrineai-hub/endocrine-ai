from pathlib import Path

from backend.app import create_app
from backend.models.db import get_connection


def test_home_route():
    app = create_app()
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200


def test_assess_validation_error():
    app = create_app()
    client = app.test_client()
    resp = client.post('/api/assess', json={'profile': {'Age': 21}})
    assert resp.status_code == 400
    assert resp.get_json()['status'] == 'error'


def test_public_assessment_is_saved_with_contact_fields(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "test_app.db"
    monkeypatch.setenv("SQLITE_DB_PATH", str(db_path))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    monkeypatch.delenv("POSTGRES_PRISMA_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL_NON_POOLING", raising=False)
    monkeypatch.delenv("NEON_DATABASE_URL", raising=False)

    app = create_app()
    client = app.test_client()

    payload = {
        "patient_name": "Test Patient",
        "patient_email": "patient@example.com",
        "patient_mobile": "9999999999",
        "profile": {
            "Age": 28,
            "Gender": "Female",
            "BMI": 24.2,
            "Sleep quality": "Average",
            "Stress level": "Moderate",
            "Exercise frequency": "3 days/week",
            "Diet type": "Balanced",
            "Symptoms": ["Fatigue"],
        },
        "lab_report_text": "TSH: 2.7, HbA1c: 5.4",
        "use_ml": False,
    }

    resp = client.post("/api/assess", json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "success"

    conn = get_connection()
    row = conn.execute(
        "SELECT patient_name, patient_email, patient_mobile FROM assessments ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()

    assert row is not None
    assert row["patient_name"] == "Test Patient"
    assert row["patient_email"] == "patient@example.com"
    assert row["patient_mobile"] == "9999999999"
