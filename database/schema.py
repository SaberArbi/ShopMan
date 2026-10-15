"""Schema creation. Only called on first run or when the DB is empty."""
import sqlite3

from .connection import DB_PATH


def create_tables() -> None:
    """Create products + sales tables and seed telecom products."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fresh-install path only — main.py guards this.
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS sales")

    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            name TEXT NOT NULL,
            photo TEXT,
            buy_price REAL NOT NULL DEFAULT 0,
            sell_price REAL NOT NULL DEFAULT 0,
            unit TEXT NOT NULL DEFAULT 'piece',
            stock REAL DEFAULT 0,
            single_price REAL DEFAULT 0,
            pieces_per_pack INTEGER DEFAULT 20,
            product_type TEXT DEFAULT 'normal',
            single_cigarette_price REAL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity REAL NOT NULL,
            profit REAL NOT NULL,
            total REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)

    telecom = [
        ("TELECOM 1.3 DT", "telecom_1.3", 0.8, 1.3, "piece", 0, "telecom"),
        ("TELECOM 5.9 DT", "telecom_5.9", 4.5, 5.9, "piece", 0, "telecom"),
        ("ORANGE 1.3 DT",  "orange_1.3",  0.8, 1.3, "piece", 0, "telecom"),
        ("ORANGE 5.9 DT",  "orange_5.9",  4.5, 5.9, "piece", 0, "telecom"),
        ("OOREDOO 1.3 DT", "ooredoo_1.3", 0.8, 1.3, "piece", 0, "telecom"),
        ("OOREDOO 5.9 DT", "ooredoo_5.9", 4.5, 5.9, "piece", 0, "telecom"),
    ]
    for name, barcode, buy, sell, unit, stock, ptype in telecom:
        cursor.execute(
            "INSERT INTO products "
            "(name, barcode, buy_price, sell_price, unit, stock, product_type) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, barcode, buy, sell, unit, stock, ptype),
        )

    conn.commit()
    conn.close()