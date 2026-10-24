"""file_scanner.py - custom module for the Project Directory Auditor.

Isko audit notebook import karta hai:  import file_scanner
"""
import math
import os
from datetime import datetime, timedelta

STALE_DAYS = 30          # itne din se purani file flag hogi
FINE_PER_DAY = 10        # har extra din ka jurmana (Rs)


def scan_folder(folder):
    """Folder (aur uske sub folders) ki har file ki details list mein deta hai."""
    results = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.isdir(path):
            results.extend(scan_folder(path))      # recursion: andar wale folder bhi
            continue
        info = os.stat(path)
        ext = os.path.splitext(name)[1].lower()
        results.append({
            "name": name,
            "path": path,
            "size_bytes": info.st_size,
            "type": ext if ext else "(no ext)",
            "modified": datetime.fromtimestamp(info.st_mtime),
        })
    return results


def age_in_days(modified, now=None):
    now = now or datetime.now()
    return (now - modified).days


def is_stale(modified, now=None):
    return age_in_days(modified, now) > STALE_DAYS


def calculate_fine(modified, now=None):
    """30 din ke baad har din ka FINE_PER_DAY. Thora sa bhi upar ho to poora din gina jata hai (math.ceil)."""
    now = now or datetime.now()
    overage = now - modified - timedelta(days=STALE_DAYS)
    if overage.total_seconds() <= 0:
        return 0
    return math.ceil(overage.total_seconds() / 86400) * FINE_PER_DAY


def size_kb(size_bytes):
    return round(size_bytes / 1024, 2)


if __name__ == "__main__":
    # direct run karne par sirf chhota sa test
    for item in scan_folder("."):
        print(item["name"], size_kb(item["size_bytes"]), "KB")
