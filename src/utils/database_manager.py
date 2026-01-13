import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "sentinel_vault.db")


def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cve_id TEXT UNIQUE,
            description TEXT,
            score REAL,
            severity TEXT,
            is_priority INTEGER,
            detection_date TIMESTAMP,
            status TEXT DEFAULT 'PENDING'
        )
    ''')
    try:
        cursor.execute('ALTER TABLE detections ADD COLUMN status TEXT DEFAULT "PENDING"')
        print("✅ Base de datos actualizada: Columna 'status' añadida.")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def is_cve_processed(cve_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM detections WHERE cve_id = ?', (cve_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def save_detection(cve_id, description, score, severity, is_priority):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO detections (cve_id, description, score, severity, is_priority, detection_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cve_id, description, score, severity, 1 if is_priority else 0, datetime.now()))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def update_cve_status(cve_id, new_status):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE detections 
            SET status = ? 
            WHERE cve_id = ?
        ''', (new_status, cve_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al actualizar estado: {e}")
        return False