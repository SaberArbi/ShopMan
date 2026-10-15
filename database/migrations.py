"""Idempotent migrations run at every startup."""
from utils import auth as _auth   # hashed here, but keeps the table local
from .connection import get_connection


def _column_exists(cur, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def ensure_auth_schema() -> None:
    """Create users table if missing, add soft-delete columns to sales,
    create the covering index, seed the default owner on a fresh DB."""
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
        for col, ddl in (
            ("deleted_at",    "TEXT DEFAULT NULL"),
            ("deleted_by",    "INTEGER DEFAULT NULL"),
            ("delete_reason", "TEXT DEFAULT NULL"),
        ):
            if not _column_exists(cur, "sales", col):
                cur.execute(f"ALTER TABLE sales ADD COLUMN {col} {ddl}")

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_date_active
            ON sales(date, deleted_at)
        """)
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            _auth._create_user(conn, "owner", "owner123", "owner", "Owner")
            conn.commit()
    finally:
        conn.close()