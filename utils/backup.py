"""Backup: hourly, on exit, and after each sale. Keeps last 10."""
import os
import shutil
import threading
import time
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "stock.db")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")

_KEEP = 10
_PREFIX = "auto_backup_"


def do_backup() -> bool:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        return False

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"{_PREFIX}{stamp}.db")
    shutil.copy2(DB_PATH, dest)

    backups = sorted(f for f in os.listdir(BACKUP_DIR)
                     if f.startswith(_PREFIX))
    for old in backups[:-_KEEP]:
        os.remove(os.path.join(BACKUP_DIR, old))
    return True


def _loop():
    while True:
        time.sleep(3600)
        try:
            do_backup()
        except Exception as e:
            print(f"Hourly backup failed: {e}")


def start_auto_backup() -> None:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    threading.Thread(target=_loop, daemon=True).start()