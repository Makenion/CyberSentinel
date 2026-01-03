import json
import os

HISTORY_FILE = "data/processed_cves.json"

def get_processed_cves():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_processed_cve(cve_id):
    history = get_processed_cves()
    if cve_id not in history:
        history.append(cve_id)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history[-100:], f)