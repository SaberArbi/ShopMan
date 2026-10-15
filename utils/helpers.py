import os
from datetime import datetime
import shutil

PHOTO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets/products')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'stock.db')

def calculate_price(product, quantity):
    """Calculate final price - simple: price × quantity"""
    return product[5] * quantity

def calculate_profit(product, quantity):
    """Calculate profit - simple: (sell - buy) × quantity"""
    return (product[5] - product[4]) * quantity

def auto_backup():
    """Auto backup database"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"stock_backup_{date}.db")
    
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, backup_file)
        return True
    return False

def save_photo(photo_data, product_name):
    """Save product photo"""
    if not os.path.exists(PHOTO_DIR):
        os.makedirs(PHOTO_DIR)
    
    filename = f"{product_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(PHOTO_DIR, filename)
    
    with open(filepath, 'wb') as f:
        f.write(photo_data)
    
    return filepath