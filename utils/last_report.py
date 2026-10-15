import os
import json
from datetime import datetime

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
LAST_REPORT_FILE = os.path.join(REPORTS_DIR, 'last_report.json')

def save_last_report(end_dt):
    """Save the end datetime of the last generated report."""
    data = {'last_end': end_dt}
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    with open(LAST_REPORT_FILE, 'w') as f:
        json.dump(data, f)

def load_last_report():
    """Return the last end datetime string, or None if not exists."""
    if os.path.exists(LAST_REPORT_FILE):
        with open(LAST_REPORT_FILE, 'r') as f:
            data = json.load(f)
            return data.get('last_end')
    return None