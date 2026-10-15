import os
from datetime import datetime
import shutil
import threading
import time

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'stock.db')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')

def do_backup():
    """Perform a single backup"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    if os.path.exists(DB_PATH):
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"auto_backup_{date}.db")
        shutil.copy2(DB_PATH, backup_file)
        
        # Keep only last 10 backups
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('auto_backup_')])
        if len(backups) > 10:
            for old in backups[:-10]:
                os.remove(os.path.join(BACKUP_DIR, old))
        return True
    return False

def backup_loop():
    """Run backup every hour"""
    while True:
        time.sleep(3600)  # 1 hour
        do_backup()

def start_auto_backup():
    """Start backup thread"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    thread = threading.Thread(target=backup_loop, daemon=True)
    thread.start()