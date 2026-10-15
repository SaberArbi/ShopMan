"""Product queries and mutations."""
from .connection import get_connection
from .errors import BarcodeExists

__all__ = [
    "get_all_products", "get_telecom_products", "get_product_by_barcode",
    "search_products_by_name", "add_product", "update_product",
    "delete_product", "update_stock",
]


_PRODUCT_COLUMNS = (
    "id, barcode, name, photo, buy_price, sell_price, unit, stock, "
    "single_price, pieces_per_pack, product_type, single_cigarette_price"
)


def get_all_products():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT {_PRODUCT_COLUMNS} FROM products ORDER BY name")
        return cur.fetchall()
    finally:
        conn.close()


def get_telecom_products():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, buy_price, sell_price, product_type "
            "FROM products WHERE product_type = 'telecom' ORDER BY name"
        )
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
        cur.execute(
            f"SELECT {_PRODUCT_COLUMNS} FROM products "
            "WHERE name LIKE ? ORDER BY name",
            (f"%{search_term}%",),
        )
        return cur.fetchall()
    finally:
        conn.close()


def _assert_barcode_free(cur, barcode, exclude_id=None):
    if not barcode or not barcode.strip():
        return
    if exclude_id is None:
        cur.execute("SELECT id FROM products WHERE barcode = ?", (barcode,))
    else:
        cur.execute(
            "SELECT id FROM products WHERE barcode = ? AND id != ?",
            (barcode, exclude_id),
        )
    if cur.fetchone():
        raise BarcodeExists(barcode)


def add_product(barcode, name, photo, buy_price, sell_price, unit, stock,
                single_price=0, pieces_per_pack=20, product_type="normal",
                single_cigarette_price=0):
    conn = get_connection()
    try:
        cur = conn.cursor()
        _assert_barcode_free(cur, barcode)
        cur.execute("""
            INSERT INTO products
                (barcode, name, photo, buy_price, sell_price, unit, stock,
                 single_price, pieces_per_pack, product_type, single_cigarette_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (barcode, name, photo, buy_price, sell_price, unit, stock,
              single_price, pieces_per_pack, product_type, single_cigarette_price))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_product(id, barcode, name, photo, buy_price, sell_price, unit, stock,
                   single_price=0, pieces_per_pack=20, product_type="normal",
                   single_cigarette_price=0):
    conn = get_connection()
    try:
        cur = conn.cursor()
        _assert_barcode_free(cur, barcode, exclude_id=id)
        cur.execute("""
            UPDATE products
            SET barcode = ?, name = ?, photo = ?, buy_price = ?, sell_price = ?,
                unit = ?, stock = ?, single_price = ?, pieces_per_pack = ?,
                product_type = ?, single_cigarette_price = ?
            WHERE id = ?
        """, (barcode, name, photo, buy_price, sell_price, unit, stock,
              single_price, pieces_per_pack, product_type,
              single_cigarette_price, id))
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
        cur.execute("UPDATE products SET stock = stock - ? WHERE id = ?",
                    (quantity_sold, product_id))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()