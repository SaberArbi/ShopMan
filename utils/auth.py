# utils/auth.py
import hashlib
import secrets
import sqlite3
from datetime import datetime

from database.db_operations import DB_PATH


# ---------------------------------------------------------------------------
# Roles / permissions
# ---------------------------------------------------------------------------
PERMISSIONS = {
    "owner": {"*"},
    "cashier": {
        "sell",
        "view_reports",
        "view_history",
        "soft_delete_sale",
    },
}

SCREEN_PERMISSIONS = {
    "sales":    "sell",
    "reports":  "view_reports",
    "history":  "view_history",
    "products": "manage_products",
    "users":    "manage_users",
    "deleted":  "view_deleted_sales",
}


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


# ---------------------------------------------------------------------------
# Schema / migration
# ---------------------------------------------------------------------------
def ensure_auth_schema():
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT NOT NULL DEFAULT 'cashier',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        for col, ddl in [
            ("deleted_at",    "TEXT DEFAULT NULL"),
            ("deleted_by",    "INTEGER DEFAULT NULL"),
            ("delete_reason", "TEXT DEFAULT NULL"),
        ]:
            if not _column_exists(cur, "sales", col):
                cur.execute(f"ALTER TABLE sales ADD COLUMN {col} {ddl}")

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_date_active
            ON sales(date, deleted_at)
        """)

        conn.commit()

        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            _create_user(conn, "owner", "owner123", "owner", "Owner")
            conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    iterations = 200_000
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iter_s, salt, hash_hex = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(iter_s),
        )
        return secrets.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
def _create_user(conn, username, password, role, full_name=""):
    if role not in PERMISSIONS:
        raise ValueError(f"Unknown role: {role}")
    conn.execute(
        """
        INSERT INTO users (username, password_hash, full_name, role)
        VALUES (?, ?, ?, ?)
        """,
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
        cur.execute("""
            SELECT id, username, password_hash, full_name, role, is_active
            FROM users
            WHERE username = ?
        """, (username,))
        row = cur.fetchone()
        if not row:
            return None

        user_id, uname, pwd_hash, full_name, role, is_active = row
        if not is_active:
            return None
        if not verify_password(password, pwd_hash):
            return None

        return {
            "id": user_id,
            "username": uname,
            "full_name": full_name,
            "role": role,
        }
    finally:
        conn.close()


def list_users():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, username, full_name, role, is_active, created_at
            FROM users
            ORDER BY role, username
        """)
        return cur.fetchall()
    finally:
        conn.close()


def set_user_active(user_id, active: bool):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET is_active = ? WHERE id = ?",
            (1 if active else 0, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def change_password(user_id, new_password: str):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_password(new_password), user_id),
        )
        conn.commit()
    finally:
        conn.close()


def rename_user(user_id, new_username: str):
    """Change a user's login name. Raises ValueError on empty/duplicate."""
    new_username = new_username.strip()
    if not new_username:
        raise ValueError("Le nom d'utilisateur ne peut pas être vide")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM users WHERE username = ? AND id != ?",
            (new_username, user_id),
        )
        if cur.fetchone():
            raise ValueError(f"Le nom '{new_username}' est déjà utilisé")

        cur.execute(
            "UPDATE users SET username = ? WHERE id = ?",
            (new_username, user_id),
        )
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


# ---------------------------------------------------------------------------
# Permission checks
# ---------------------------------------------------------------------------
def can(user, permission: str) -> bool:
    if not user:
        return False
    perms = PERMISSIONS.get(user.get("role"), set())
    return "*" in perms or permission in perms
