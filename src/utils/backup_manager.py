import shutil
import os
from datetime import datetime
from src.utils.database_manager import DB_PATH

BACKUP_DIR = "backups"


def create_db_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"sentinel_backup_{timestamp}.db")

    try:
        shutil.copy2(DB_PATH, backup_file)
        return True, backup_file
    except Exception as e:
        return False, str(e)