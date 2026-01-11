import sqlite3
import os
from datetime import datetime, timedelta
from src.utils.database_manager import DB_PATH


def get_weekly_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    una_semana_atras = datetime.now() - timedelta(days=7)

    cursor.execute('SELECT COUNT(*) FROM detections WHERE detection_date > ?', (una_semana_atras,))
    total = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM detections WHERE detection_date > ? AND is_priority = 1', (una_semana_atras,))
    prioritarios = cursor.fetchone()[0]

    cursor.execute('''
        SELECT cve_id, score, severity FROM detections 
        WHERE detection_date > ? AND score > 0
        ORDER BY score DESC LIMIT 5
    ''', (una_semana_atras,))
    top_cves = cursor.fetchall()

    conn.close()
    return {
        "total": total,
        "prioritarios": prioritarios,
        "top_cves": top_cves,
        "fecha": datetime.now().strftime("%Y-%m-%d")
    }


def generate_markdown_report(stats):
    report_dir = "reports"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    file_path = os.path.join(report_dir, f"reporte_semanal_{stats['fecha']}.md")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# 📊 Reporte Semanal de Impacto - CyberSentinel\n")
        f.write(f"**Fecha de generación:** {stats['fecha']}\n\n")
        f.write(f"## 📈 Resumen de Actividad\n")
        f.write(f"- **Vulnerabilidades analizadas:** {stats['total']}\n")
        f.write(f"- **Alertas de alta prioridad (Stack Técnico):** {stats['prioritarios']}\n\n")
        f.write(f"## 🛡️ Top 5 Amenazas Detectadas\n")
        f.write(f"| CVE ID | Score CVSS | Estado |\n")
        f.write(f"| :--- | :--- | :--- |\n")
        for cve in stats['top_cves']:
            f.write(f"| {cve[0]} | {cve[1]} | {cve[2]} |\n")
        f.write(f"\n\n---\n*Generado automáticamente por CyberSentinel v2.0*")

    return file_path