"""Users, roles, permissions, password hashing."""
import hashlib
import secrets

from database.connection import get_connection


PERMISSIONS = {
    "owner": {"*"},
    "cashier": {
        "sell",
        "view_reports",
        "view_history",
        "soft_delete_sale",
    },
}


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    iterations = 200_000
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"),
        bytes.fromhex(salt), iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iter_s, salt, hash_hex = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"),
            bytes.fromhex(salt), int(iter_s),
        )
        return secrets.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False


def _create_user(conn, username, password, role, full_name=""):
    """Internal — used by migrations to seed the owner."""
    if role not in PERMISSIONS:
        raise ValueError(f"Unknown role: {role}")
    conn.execute(
        "INSERT INTO users (username, password_hash, full_name, role) "
        "VALUES (?, ?, ?, ?)",
        (username, hash_password(password), full_name, role),
    )


def create_user(username, password, role, full_name=""):
    conn = get_connection()
    try:
        _create_user(conn, username, password, role, full_name)
        conn.commit()
    finally:
        conn.close()


def authenticate(username: str, password: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password_hash, full_name, role, is_active "
            "FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        if not row:
            return None
        user_id, uname, pwd_hash, full_name, role, is_active = row
        if not is_active or not verify_password(password, pwd_hash):
            return None
        return {"id": user_id, "username": uname,
                "full_name": full_name, "role": role}
    finally:
        conn.close()


def list_users():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, full_name, role, is_active, created_at "
            "FROM users ORDER BY role, username"
        )
        return cur.fetchall()
    finally:
        conn.close()


def set_user_active(user_id, active: bool):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET is_active = ? WHERE id = ?",
                     (1 if active else 0, user_id))
        conn.commit()
    finally:
        conn.close()


def change_password(user_id, new_password: str):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                     (hash_password(new_password), user_id))
        conn.commit()
    finally:
        conn.close()


def rename_user(user_id, new_username: str):
    new_username = new_username.strip()
    if not new_username:
        raise ValueError("empty")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ? AND id != ?",
                    (new_username, user_id))
        if cur.fetchone():
            raise ValueError("taken")
        cur.execute("UPDATE users SET username = ? WHERE id = ?",
                    (new_username, user_id))
        conn.commit()
    finally:
        conn.close()


def delete_user(user_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()


def can(user, permission: str) -> bool:
    if not user:
        return False
    perms = PERMISSIONS.get(user.get("role"), set())
    return "*" in perms or permission in perms