import os
import glob
import time
from datetime import datetime, timedelta

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "reports")

def _ensure_dir():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

def get_last_report(ticker: str) -> str | None:
    _ensure_dir()
    pattern = os.path.join(REPORTS_DIR, f"{ticker}_*.md")
    files = glob.glob(pattern)
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r', encoding='utf-8') as f:
        return f.read()

def list_reports(ticker: str = None) -> list[dict]:
    _ensure_dir()
    pattern = os.path.join(REPORTS_DIR, f"{ticker}_*.md") if ticker else os.path.join(REPORTS_DIR, "*.md")
    files = glob.glob(pattern)
    reports = []
    for filepath in files:
        filename = os.path.basename(filepath)
        # Expected format: TICKER_YYYYMMDD_HHMM.md
        parts = filename.replace(".md", "").split("_", 1)
        if len(parts) == 2:
            t, ts = parts
            reports.append({
                "ticker": t,
                "timestamp": ts,
                "filepath": filepath,
                "ctime": os.path.getctime(filepath)
            })
    # Sort by newest first
    reports.sort(key=lambda x: x['ctime'], reverse=True)
    return reports

def cleanup_old_reports(days: int = 7):
    _ensure_dir()
    files = glob.glob(os.path.join(REPORTS_DIR, "*.md"))
    now = time.time()
    cutoff = now - (days * 86400)
    for filepath in files:
        if os.path.getctime(filepath) < cutoff:
            try:
                os.remove(filepath)
            except OSError:
                pass
