"""Sales operations: checkout, soft/hard delete, trash, restore."""
from datetime import datetime

from .connection import get_connection
from .errors import (
    SaleNotFound, SaleAlreadyDeleted, SaleNotDeleted,
    NoActiveSales, NoSales, NoDeletedSales, InsufficientStock,
)

__all__ = [
    "add_sale", "delete_sale", "soft_delete_sale",
    "soft_delete_sales_by_timestamp", "hard_delete_sales_by_timestamp",
    "get_grouped_sales", "get_sales_by_timestamp",
    "get_deleted_groups", "get_deleted_sales_by_deletion_timestamp",
    "restore_sale", "restore_sales_by_deletion_timestamp",
]


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------
def add_sale(product_id, quantity, profit, total, date=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        date = date or _now()
        cur.execute(
            "INSERT INTO sales (product_id, quantity, profit, total, date) "
            "VALUES (?, ?, ?, ?, ?)",
            (product_id, quantity, profit, total, date),
        )
        sale_id = cur.lastrowid
        cur.execute("UPDATE products SET stock = stock - ? WHERE id = ?",
                    (quantity, product_id))
        conn.commit()
        return sale_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Delete — single line
# ---------------------------------------------------------------------------
def delete_sale(sale_id):
    """HARD delete of one line. Owner only at the UI layer."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT product_id, quantity, deleted_at FROM sales WHERE id = ?",
                    (sale_id,))
        row = cur.fetchone()
        if not row:
            raise SaleNotFound()
        product_id, quantity, deleted_at = row
        if deleted_at is None:
            cur.execute("UPDATE products SET stock = stock + ? WHERE id = ?",
                        (quantity, product_id))
        cur.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def soft_delete_sale(sale_id, user_id, reason=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT product_id, quantity, deleted_at FROM sales WHERE id = ?",
                    (sale_id,))
        row = cur.fetchone()
        if not row:
            raise SaleNotFound()
        product_id, quantity, deleted_at = row
        if deleted_at is not None:
            return True   # already deleted → idempotent

        cur.execute("UPDATE products SET stock = stock + ? WHERE id = ?",
                    (quantity, product_id))
        cur.execute("""
            UPDATE sales
            SET deleted_at = ?, deleted_by = ?, delete_reason = ?
            WHERE id = ?
        """, (_now(), user_id, reason, sale_id))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Delete — by cart timestamp
# ---------------------------------------------------------------------------
def soft_delete_sales_by_timestamp(timestamp, user_id, reason=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, product_id, quantity FROM sales
            WHERE date = ? AND deleted_at IS NULL
        """, (timestamp,))
        rows = cur.fetchall()
        if not rows:
            raise NoActiveSales()

        now = _now()
        for sale_id, product_id, quantity in rows:
            cur.execute("UPDATE products SET stock = stock + ? WHERE id = ?",
                        (quantity, product_id))
            cur.execute("""
                UPDATE sales
                SET deleted_at = ?, deleted_by = ?, delete_reason = ?
                WHERE id = ?
            """, (now, user_id, reason, sale_id))
        conn.commit()
        return len(rows)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def hard_delete_sales_by_timestamp(timestamp):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, product_id, quantity, deleted_at FROM sales
            WHERE date = ?
        """, (timestamp,))
        rows = cur.fetchall()
        if not rows:
            raise NoSales()

        for sale_id, product_id, quantity, deleted_at in rows:
            if deleted_at is None:
                cur.execute("UPDATE products SET stock = stock + ? WHERE id = ?",
                            (quantity, product_id))
            cur.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        conn.commit()
        return len(rows)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Read — active
# ---------------------------------------------------------------------------
def get_grouped_sales(start_datetime=None, end_datetime=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = ("SELECT date, COUNT(*), SUM(total), SUM(profit) "
                 "FROM sales WHERE deleted_at IS NULL")
        params = []
        if start_datetime:
            query += " AND date >= ?"
            params.append(start_datetime)
        if end_datetime:
            query += " AND date <= ?"
            params.append(end_datetime)
        query += " GROUP BY date ORDER BY date DESC"
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()


def get_sales_by_timestamp(timestamp):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id, p.name, s.quantity, p.unit, s.total, s.profit
            FROM sales s JOIN products p ON s.product_id = p.id
            WHERE s.date = ? AND s.deleted_at IS NULL
        """, (timestamp,))
        return cur.fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Read — trash
# ---------------------------------------------------------------------------
def get_deleted_groups(start_dt=None, end_dt=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
            SELECT s.deleted_at, COUNT(*), SUM(s.total), SUM(s.profit),
                   COALESCE(MAX(u.username), '(inconnu)')
            FROM sales s
            LEFT JOIN users u ON s.deleted_by = u.id
            WHERE s.deleted_at IS NOT NULL
        """
        params = []
        if start_dt:
            query += " AND s.deleted_at >= ?"
            params.append(start_dt)
        if end_dt:
            query += " AND s.deleted_at <= ?"
            params.append(end_dt)
        query += " GROUP BY s.deleted_at ORDER BY s.deleted_at DESC"
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()


def get_deleted_sales_by_deletion_timestamp(deleted_at):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id, s.date, p.name, s.quantity, p.unit, s.total, s.profit,
                   COALESCE(u.username, '(inconnu)'), s.delete_reason
            FROM sales s
            JOIN products p ON s.product_id = p.id
            LEFT JOIN users u ON s.deleted_by = u.id
            WHERE s.deleted_at = ?
            ORDER BY s.id
        """, (deleted_at,))
        return cur.fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------
def _assert_restorable(cur, rows):
    """All-or-nothing stock check before restoring a batch."""
    for _sale_id, product_id, quantity in rows:
        cur.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
        r = cur.fetchone()
        if not r:
            raise SaleNotFound()  # product gone
        if r[0] < quantity:
            raise InsufficientStock(available=r[0], required=quantity)


def restore_sale(sale_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT product_id, quantity, deleted_at FROM sales WHERE id = ?",
                    (sale_id,))
        row = cur.fetchone()
        if not row:
            raise SaleNotFound()
        product_id, quantity, deleted_at = row
        if deleted_at is None:
            raise SaleNotDeleted()

        cur.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
        r = cur.fetchone()
        if not r:
            raise SaleNotFound()
        if r[0] < quantity:
            raise InsufficientStock(available=r[0], required=quantity)

        cur.execute("UPDATE products SET stock = stock - ? WHERE id = ?",
                    (quantity, product_id))
        cur.execute("""
            UPDATE sales
            SET deleted_at = NULL, deleted_by = NULL, delete_reason = NULL
            WHERE id = ?
        """, (sale_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def restore_sales_by_deletion_timestamp(deleted_at):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, product_id, quantity FROM sales WHERE deleted_at = ?",
                    (deleted_at,))
        rows = cur.fetchall()
        if not rows:
            raise NoDeletedSales()

        _assert_restorable(cur, rows)

        for sale_id, product_id, quantity in rows:
            cur.execute("UPDATE products SET stock = stock - ? WHERE id = ?",
                        (quantity, product_id))
            cur.execute("""
                UPDATE sales
                SET deleted_at = NULL, deleted_by = NULL, delete_reason = NULL
                WHERE id = ?
            """, (sale_id,))
        conn.commit()
        return len(rows)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()