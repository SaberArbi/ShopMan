"""Aggregates and reporting queries."""
from .connection import get_connection

__all__ = [
    "get_period_summary_datetime", "get_top_products_datetime",
    "get_stock_status", "verify_sales_aggregates",
]


def get_period_summary_datetime(start_dt, end_dt):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(total), 0),
                   COALESCE(SUM(profit), 0),
                   COUNT(DISTINCT date)
            FROM sales
            WHERE date BETWEEN ? AND ? AND deleted_at IS NULL
        """, (start_dt, end_dt))
        return cur.fetchone()
    finally:
        conn.close()


def get_top_products_datetime(limit=10, start_dt=None, end_dt=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
            SELECT p.name, SUM(s.quantity), SUM(s.total), SUM(s.profit)
            FROM sales s JOIN products p ON s.product_id = p.id
            WHERE s.deleted_at IS NULL
        """
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
        cur.execute("""
            SELECT name, stock, unit FROM products
            WHERE stock < ? ORDER BY stock ASC
        """, (threshold,))
        low_stock = cur.fetchall()
        return total_value, low_stock
    finally:
        conn.close()


def verify_sales_aggregates():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(SUM(total), 0), COALESCE(SUM(profit), 0) "
                    "FROM sales WHERE deleted_at IS NULL")
        all_total, all_profit = cur.fetchone()
        cur.execute("SELECT date, SUM(total), SUM(profit) "
                    "FROM sales WHERE deleted_at IS NULL GROUP BY date")
        groups = cur.fetchall()
        grouped_total = sum(g[1] for g in groups)
        grouped_profit = sum(g[2] for g in groups)
    finally:
        conn.close()

    print(f"All sales:   total={all_total:.2f}, profit={all_profit:.2f}")
    print(f"Grouped sum: total={grouped_total:.2f}, profit={grouped_profit:.2f}")
    if abs(all_total - grouped_total) > 0.01:
        print("MISMATCH DETECTED!")
    return all_total, all_profit, grouped_total, grouped_profit