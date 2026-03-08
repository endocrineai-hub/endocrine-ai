import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "app.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
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
