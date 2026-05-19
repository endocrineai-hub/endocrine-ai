import os
import sqlite3
from pathlib import Path

try:
    import psycopg
    from psycopg.rows import dict_row
except ModuleNotFoundError:
    psycopg = None
    dict_row = None
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parents[1]


def _database_url() -> str:
    return os.getenv("DATABASE_URL", "").strip()


def _is_postgres() -> bool:
    url = _database_url()
    return url.startswith("postgres://") or url.startswith("postgresql://")


def _sqlite_db_path() -> Path:
    explicit_path = os.getenv("SQLITE_DB_PATH", "").strip()
    if explicit_path:
        return Path(explicit_path)

    # Vercel has a read-only source filesystem. Use /tmp when no external DB is configured.
    if os.getenv("VERCEL") and not _database_url():
        return Path("/tmp/endocrine_app.db")

    return BASE_DIR / "data" / "app.db"


def _translate_params(query: str) -> str:
    # Existing codebase uses sqlite-style '?' placeholders; postgres needs '%s'.
    return query.replace("?", "%s")


class DBConnection:
    def __init__(self, conn, is_postgres: bool):
        self._conn = conn
        self._is_postgres = is_postgres

    def execute(self, query: str, params: tuple | list | None = None):
        final_query = _translate_params(query) if self._is_postgres else query
        cursor = self._conn.cursor()
        if params is None:
            params = ()
        cursor.execute(final_query, params)
        return cursor

    def commit(self) -> None:
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


def get_connection() -> DBConnection:
    if _is_postgres():
        if psycopg is None or dict_row is None:
            raise RuntimeError("psycopg is required when DATABASE_URL points to PostgreSQL")
        conn = psycopg.connect(_database_url(), row_factory=dict_row)
        return DBConnection(conn, is_postgres=True)

    sqlite_path = _sqlite_db_path()
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    return DBConnection(conn, is_postgres=False)


def _init_sqlite_db(conn: DBConnection) -> None:
    sqlite_path = _sqlite_db_path()
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            user_id INTEGER,
            patient_name TEXT,
            patient_email TEXT,
            patient_mobile TEXT,
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
    if "patient_email" not in columns:
        conn.execute("ALTER TABLE assessments ADD COLUMN patient_email TEXT")
    if "patient_mobile" not in columns:
        conn.execute("ALTER TABLE assessments ADD COLUMN patient_mobile TEXT")


def _init_postgres_db(conn: DBConnection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS assessments (
            id BIGSERIAL PRIMARY KEY,
            created_at TEXT NOT NULL,
            user_id BIGINT,
            patient_name TEXT,
            patient_email TEXT,
            patient_mobile TEXT,
            age INTEGER,
            gender TEXT,
            bmi DOUBLE PRECISION,
            symptoms TEXT,
            thyroid_risk TEXT,
            diabetes_risk TEXT,
            pcos_risk TEXT,
            adrenal_risk TEXT,
            metabolic_risk TEXT,
            risk_score DOUBLE PRECISION,
            profile_json TEXT,
            result_json TEXT
        )
        """
    )
    conn.execute("ALTER TABLE assessments ADD COLUMN IF NOT EXISTS patient_email TEXT")
    conn.execute("ALTER TABLE assessments ADD COLUMN IF NOT EXISTS patient_mobile TEXT")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id BIGSERIAL PRIMARY KEY,
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
            id BIGSERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )


def init_db() -> None:
    conn = get_connection()
    if _is_postgres():
        _init_postgres_db(conn)
    else:
        _init_sqlite_db(conn)

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
