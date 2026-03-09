from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_connection


def verify_admin_credentials(username: str, password: str) -> bool:
    if not username or not password:
        return False
    conn = get_connection()
    row = conn.execute(
        "SELECT password_hash FROM admin_users WHERE lower(username)=lower(?)",
        (username.strip(),),
    ).fetchone()
    conn.close()
    if not row:
        return False
    return check_password_hash(row["password_hash"], password)


def upsert_admin_user(username: str, password: str) -> None:
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM admin_users WHERE lower(username)=lower(?)",
        (username.strip(),),
    ).fetchone()
    password_hash = generate_password_hash(password)
    if existing:
        conn.execute(
            "UPDATE admin_users SET password_hash=? WHERE id=?",
            (password_hash, existing["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            (username.strip(), password_hash),
        )
    conn.commit()
    conn.close()
