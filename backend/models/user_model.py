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
