"""
Database operations for Stock Manager.
"""

import os
import sqlite3
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'stock.db')


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ===========================================================================
# PRODUCTS
# ===========================================================================
def get_all_products():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT id, barcode, name, photo, buy_price, sell_price, unit, stock,
                   single_price, pieces_per_pack, product_type, single_cigarette_price
            FROM products
            ORDER BY name
        ''')
        return cur.fetchall()
    finally:
        conn.close()


def get_telecom_products():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT id, name, buy_price, sell_price, product_type
            FROM products
            WHERE product_type = 'telecom'
            ORDER BY name
        ''')
        return cur.fetchall()
    finally:
        conn.close()


def get_product_by_barcode(barcode):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
        return cur.fetchone()
    finally:
        conn.close()


def search_products_by_name(search_term):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT id, barcode, name, photo, buy_price, sell_price, unit, stock,
                   single_price, pieces_per_pack, product_type, single_cigarette_price
            FROM products
            WHERE name LIKE ?
            ORDER BY name
        ''', (f'%{search_term}%',))
        return cur.fetchall()
    finally:
        conn.close()


def add_product(barcode, name, photo, buy_price, sell_price, unit, stock,
                single_price=0, pieces_per_pack=20, product_type='normal',
                single_cigarette_price=0):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if barcode and barcode.strip():
            cur.execute("SELECT id FROM products WHERE barcode = ?", (barcode,))
            if cur.fetchone():
                raise Exception(f"Barcode '{barcode}' already exists")

        cur.execute('''
            INSERT INTO products
                (barcode, name, photo, buy_price, sell_price, unit, stock,
                 single_price, pieces_per_pack, product_type, single_cigarette_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (barcode, name, photo, buy_price, sell_price, unit, stock,
              single_price, pieces_per_pack, product_type, single_cigarette_price))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_product(id, barcode, name, photo, buy_price, sell_price, unit, stock,
                   single_price=0, pieces_per_pack=20, product_type='normal',
                   single_cigarette_price=0):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if barcode and barcode.strip():
            cur.execute(
                "SELECT id FROM products WHERE barcode = ? AND id != ?",
                (barcode, id)
            )
            if cur.fetchone():
                raise Exception(f"Barcode '{barcode}' already exists")

        cur.execute('''
            UPDATE products
            SET barcode = ?, name = ?, photo = ?, buy_price = ?, sell_price = ?,
                unit = ?, stock = ?, single_price = ?, pieces_per_pack = ?,
                product_type = ?, single_cigarette_price = ?
            WHERE id = ?
        ''', (barcode, name, photo, buy_price, sell_price, unit, stock,
              single_price, pieces_per_pack, product_type, single_cigarette_price, id))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_product(id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id = ?", (id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_stock(product_id, quantity_sold):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity_sold, product_id)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ===========================================================================
# SALES
# ===========================================================================
def add_sale(product_id, quantity, profit, total, date=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute('''
            INSERT INTO sales (product_id, quantity, profit, total, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, quantity, profit, total, date))
        sale_id = cur.lastrowid

        cur.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity, product_id)
        )
        conn.commit()
        return sale_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_sale(sale_id):
    """HARD delete of a single sale line. Owner only at the UI layer."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT product_id, quantity, deleted_at FROM sales WHERE id = ?",
            (sale_id,)
        )
        row = cur.fetchone()
        if not row:
            raise Exception("Sale not found")
        product_id, quantity, deleted_at = row

        if deleted_at is None:
            cur.execute(
                "UPDATE products SET stock = stock + ? WHERE id = ?",
                (quantity, product_id)
            )
        cur.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def soft_delete_sale(sale_id, user_id, reason=None):
    """Soft-delete one sale line. Restores stock only once."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT product_id, quantity, deleted_at FROM sales WHERE id = ?",
            (sale_id,)
        )
        row = cur.fetchone()
        if not row:
            raise Exception("Sale not found")

        product_id, quantity, deleted_at = row
        if deleted_at is not None:
            return True

        cur.execute(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            (quantity, product_id)
        )
        cur.execute('''
            UPDATE sales
            SET deleted_at = ?, deleted_by = ?, delete_reason = ?
            WHERE id = ?
        ''', (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id,
            reason,
            sale_id,
        ))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def soft_delete_sales_by_timestamp(timestamp, user_id, reason=None):
    """Soft-delete all active sale lines sharing a timestamp (one cart)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT id, product_id, quantity
            FROM sales
            WHERE date = ? AND deleted_at IS NULL
        ''', (timestamp,))
        rows = cur.fetchall()
        if not rows:
            raise Exception("No active sales found for this timestamp")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for sale_id, product_id, quantity in rows:
            cur.execute(
                "UPDATE products SET stock = stock + ? WHERE id = ?",
                (quantity, product_id)
            )
            cur.execute('''
                UPDATE sales
                SET deleted_at = ?, deleted_by = ?, delete_reason = ?
                WHERE id = ?
            ''', (now, user_id, reason, sale_id))
        conn.commit()
        return len(rows)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def hard_delete_sales_by_timestamp(timestamp):
    """Permanently delete all sale lines sharing a timestamp. Owner only."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT id, product_id, quantity, deleted_at
            FROM sales
            WHERE date = ?
        ''', (timestamp,))
        rows = cur.fetchall()
        if not rows:
            raise Exception("No sales found for this timestamp")

        for sale_id, product_id, quantity, deleted_at in rows:
            if deleted_at is None:
                cur.execute(
                    "UPDATE products SET stock = stock + ? WHERE id = ?",
                    (quantity, product_id)
                )
            cur.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        conn.commit()
        return len(rows)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_grouped_sales(start_datetime=None, end_datetime=None):
    """One row per cart (timestamp). Excludes soft-deleted sales."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = '''
            SELECT date, COUNT(*), SUM(total), SUM(profit)
            FROM sales
            WHERE deleted_at IS NULL
        '''
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
    """All active sale lines for a given cart timestamp."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT s.id, p.name, s.quantity, p.unit, s.total, s.profit
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.date = ? AND s.deleted_at IS NULL
        ''', (timestamp,))
        return cur.fetchall()
    finally:
        conn.close()


# ===========================================================================
# DELETED SALES (corbeille)
# ===========================================================================
def get_deleted_groups(start_dt=None, end_dt=None):
    """
    Group deleted sale lines by their *deletion* timestamp.
    Returns (deleted_at, count, total, profit, deleted_by_username).
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = '''
            SELECT s.deleted_at,
                   COUNT(*),
                   SUM(s.total),
                   SUM(s.profit),
                   COALESCE(MAX(u.username), '(inconnu)')
            FROM sales s
            LEFT JOIN users u ON s.deleted_by = u.id
            WHERE s.deleted_at IS NOT NULL
        '''
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
    """
    All deleted lines sharing one deletion timestamp.
    Returns (sale_id, original_date, product_name, quantity, unit,
             total, profit, deleted_by_username, delete_reason).
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT s.id, s.date, p.name, s.quantity, p.unit, s.total, s.profit,
                   COALESCE(u.username, '(inconnu)'), s.delete_reason
            FROM sales s
            JOIN products p ON s.product_id = p.id
            LEFT JOIN users u ON s.deleted_by = u.id
            WHERE s.deleted_at = ?
            ORDER BY s.id
        ''', (deleted_at,))
        return cur.fetchall()
    finally:
        conn.close()


def restore_sale(sale_id):
    """Undo a soft-delete: re-decrement stock and clear the delete markers."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT product_id, quantity, deleted_at
            FROM sales WHERE id = ?
        ''', (sale_id,))
        row = cur.fetchone()
        if not row:
            raise Exception("Vente introuvable")
        product_id, quantity, deleted_at = row
        if deleted_at is None:
            raise Exception("Cette vente n'est pas supprimée")

        cur.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
        r = cur.fetchone()
        if not r:
            raise Exception("Produit introuvable")
        if r[0] < quantity:
            raise Exception(
                f"Stock insuffisant pour restaurer (disponible: {r[0]}, "
                f"requis: {quantity})"
            )

        cur.execute("UPDATE products SET stock = stock - ? WHERE id = ?",
                    (quantity, product_id))
        cur.execute('''
            UPDATE sales
            SET deleted_at = NULL, deleted_by = NULL, delete_reason = NULL
            WHERE id = ?
        ''', (sale_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def restore_sales_by_deletion_timestamp(deleted_at):
    """Restore every line that shares this deletion timestamp."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT id, product_id, quantity FROM sales
            WHERE deleted_at = ?
        ''', (deleted_at,))
        rows = cur.fetchall()
        if not rows:
            raise Exception("Aucune vente supprimée pour ce timestamp")

        # Verify stock availability first (all-or-nothing).
        for _sale_id, product_id, quantity in rows:
            cur.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
            r = cur.fetchone()
            if not r:
                raise Exception(f"Produit {product_id} introuvable")
            if r[0] < quantity:
                raise Exception(
                    f"Stock insuffisant pour le produit {product_id} "
                    f"(disponible {r[0]}, requis {quantity})"
                )

        for sale_id, product_id, quantity in rows:
            cur.execute("UPDATE products SET stock = stock - ? WHERE id = ?",
                        (quantity, product_id))
            cur.execute('''
                UPDATE sales
                SET deleted_at = NULL, deleted_by = NULL, delete_reason = NULL
                WHERE id = ?
            ''', (sale_id,))

        conn.commit()
        return len(rows)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ===========================================================================
# REPORTS / AGGREGATES
# ===========================================================================
def get_period_summary_datetime(start_dt, end_dt):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT COALESCE(SUM(total), 0),
                   COALESCE(SUM(profit), 0),
                   COUNT(DISTINCT date)
            FROM sales
            WHERE date BETWEEN ? AND ? AND deleted_at IS NULL
        ''', (start_dt, end_dt))
        return cur.fetchone()
    finally:
        conn.close()


def get_top_products_datetime(limit=10, start_dt=None, end_dt=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = '''
            SELECT p.name, SUM(s.quantity), SUM(s.total), SUM(s.profit)
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.deleted_at IS NULL
        '''
        params = []
        if start_dt and end_dt:
            query += " AND s.date BETWEEN ? AND ?"
            params.extend([start_dt, end_dt])
        query += " GROUP BY p.id ORDER BY SUM(s.total) DESC LIMIT ?"
        params.append(limit)

        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()


def get_stock_status(threshold=10):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(SUM(buy_price * stock), 0) FROM products")
        total_value = cur.fetchone()[0]

        cur.execute('''
            SELECT name, stock, unit
            FROM products
            WHERE stock < ?
            ORDER BY stock ASC
        ''', (threshold,))
        low_stock = cur.fetchall()

        return total_value, low_stock
    finally:
        conn.close()


# ===========================================================================
# DEBUG
# ===========================================================================
def verify_sales_aggregates():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT COALESCE(SUM(total), 0), COALESCE(SUM(profit), 0) "
            "FROM sales WHERE deleted_at IS NULL"
        )
        all_total, all_profit = cur.fetchone()

        cur.execute(
            "SELECT date, SUM(total), SUM(profit) "
            "FROM sales WHERE deleted_at IS NULL GROUP BY date"
        )
        groups = cur.fetchall()
        grouped_total = sum(g[1] for g in groups)
        grouped_profit = sum(g[2] for g in groups)
    finally:
        conn.close()

    print(f"All sales:   total={all_total:.2f}, profit={all_profit:.2f}")
    print(f"Grouped sum: total={grouped_total:.2f}, profit={grouped_profit:.2f}")
    if abs(all_total - grouped_total) > 0.01:
        print("⚠️  MISMATCH DETECTED!")

    return all_total, all_profit, grouped_total, grouped_profit
