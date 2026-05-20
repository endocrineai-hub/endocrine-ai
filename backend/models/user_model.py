import re
from uuid import uuid4

from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_connection


def create_user(name: str, email: str, password: str) -> tuple[bool, str]:
    if not name.strip() or not email.strip() or not password.strip():
        return False, "Name, email, and password are required"

    conn = get_connection()
    existing = conn.execute("SELECT id FROM users WHERE lower(email)=lower(?)", (email.strip(),)).fetchone()
    if existing:
        conn.close()
        return False, "Email already registered"

    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name.strip(), email.strip(), generate_password_hash(password.strip())),
    )
    conn.commit()
    conn.close()
    return True, "Account created"


def verify_user(email: str, password: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, name, email, password_hash FROM users WHERE lower(email)=lower(?)",
        (email.strip(),),
    ).fetchone()
    conn.close()

    if not row:
        return None
    if not check_password_hash(row["password_hash"], password.strip()):
        return None

    return {"id": row["id"], "name": row["name"], "email": row["email"]}


def get_all_users() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, email, created_at FROM users ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_users_with_stats() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                u.id,
                u.name,
                u.email,
                u.created_at,
                COALESCE(a.total_assessments, 0) AS total_assessments,
                a.latest_assessment_at,
                a.avg_risk_score
            FROM users u
            LEFT JOIN (
                SELECT
                    user_id,
                    COUNT(*) AS total_assessments,
                    MAX(created_at) AS latest_assessment_at,
                    ROUND(CAST(AVG(risk_score) AS numeric), 2) AS avg_risk_score
                FROM assessments
                WHERE user_id IS NOT NULL
                GROUP BY user_id
            ) a ON a.user_id = u.id
            ORDER BY u.id DESC
            """
        ).fetchall()
    except Exception:
        rows = conn.execute(
            """
            SELECT
                u.id,
                u.name,
                u.email,
                u.created_at,
                0 AS total_assessments,
                NULL AS latest_assessment_at,
                NULL AS avg_risk_score
            FROM users u
            ORDER BY u.id DESC
            """
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_with_stats(user_id: int) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT
                u.id,
                u.name,
                u.email,
                u.created_at,
                COALESCE(a.total_assessments, 0) AS total_assessments,
                a.latest_assessment_at,
                a.avg_risk_score
            FROM users u
            LEFT JOIN (
                SELECT
                    user_id,
                    COUNT(*) AS total_assessments,
                    MAX(created_at) AS latest_assessment_at,
                    ROUND(CAST(AVG(risk_score) AS numeric), 2) AS avg_risk_score
                FROM assessments
                WHERE user_id IS NOT NULL
                GROUP BY user_id
            ) a ON a.user_id = u.id
            WHERE u.id = ?
            """,
            (int(user_id),),
        ).fetchone()
    except Exception:
        row = conn.execute(
            """
            SELECT
                u.id,
                u.name,
                u.email,
                u.created_at,
                0 AS total_assessments,
                NULL AS latest_assessment_at,
                NULL AS avg_risk_score
            FROM users u
            WHERE u.id = ?
            """,
            (int(user_id),),
        ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_profile(user_id: int, name: str, email: str, password: str | None = None) -> tuple[bool, str]:
    cleaned_name = (name or "").strip()
    cleaned_email = (email or "").strip()
    cleaned_password = (password or "").strip()

    if not cleaned_name:
        return False, "Name is required"
    if not cleaned_email:
        return False, "Email is required"

    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM users WHERE lower(email)=lower(?) AND id != ?",
        (cleaned_email, int(user_id)),
    ).fetchone()
    if existing:
        conn.close()
        return False, "Email already used by another user"

    if cleaned_password:
        conn.execute(
            """
            UPDATE users
            SET name = ?, email = ?, password_hash = ?
            WHERE id = ?
            """,
            (cleaned_name, cleaned_email, generate_password_hash(cleaned_password), int(user_id)),
        )
    else:
        conn.execute(
            """
            UPDATE users
            SET name = ?, email = ?
            WHERE id = ?
            """,
            (cleaned_name, cleaned_email, int(user_id)),
        )
    conn.commit()
    conn.close()
    return True, "User updated successfully"


def _slugify_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", ".", (name or "").strip().lower()).strip(".")
    return slug or "user"


def import_users_from_patient_names(names: list[str]) -> int:
    if not names:
        return 0

    conn = get_connection()
    created = 0

    for raw_name in names:
        cleaned_name = (raw_name or "").strip()
        if not cleaned_name:
            continue

        by_name = conn.execute(
            "SELECT id FROM users WHERE lower(name)=lower(?)",
            (cleaned_name,),
        ).fetchone()
        if by_name:
            continue

        base_slug = _slugify_name(cleaned_name)
        email = f"{base_slug}@import.local"
        suffix = 1
        while conn.execute("SELECT id FROM users WHERE lower(email)=lower(?)", (email,)).fetchone():
            suffix += 1
            email = f"{base_slug}.{suffix}@import.local"

        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (cleaned_name, email, generate_password_hash(uuid4().hex)),
        )
        created += 1

    conn.commit()
    conn.close()
    return created
