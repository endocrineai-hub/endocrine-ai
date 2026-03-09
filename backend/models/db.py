import sqlite3
from pathlib import Path
import os
from werkzeug.security import generate_password_hash

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
            user_id INTEGER,
            patient_name TEXT,
            age INTEGER,
            gender TEXT,
            bmi REAL,
            symptoms TEXT,
            thyroid_risk TEXT,
            diabetes_risk TEXT,
            pcos_risk TEXT,
            adrenal_risk TEXT,
            metabolic_risk TEXT,
            risk_score REAL,
            profile_json TEXT,
            result_json TEXT
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )

    # Backward-compatible migrations for older local DB files.
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(assessments)").fetchall()}
    if "user_id" not in columns:
        conn.execute("ALTER TABLE assessments ADD COLUMN user_id INTEGER")
    if "symptoms" not in columns:
        conn.execute("ALTER TABLE assessments ADD COLUMN symptoms TEXT")
    if "risk_score" not in columns:
        conn.execute("ALTER TABLE assessments ADD COLUMN risk_score REAL")

    default_user = os.getenv("ADMIN_USERNAME", "admin").strip()
    default_pass = os.getenv("ADMIN_PASSWORD", "admin123").strip()
    row = conn.execute("SELECT id FROM admin_users WHERE lower(username)=lower(?)", (default_user,)).fetchone()
    if not row:
        conn.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            (default_user, generate_password_hash(default_pass)),
        )

    conn.commit()
    conn.close()
