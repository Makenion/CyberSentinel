from src.utils.config_loader import get_config
from src.modules.cve_retriever import fetch_latest_cves
from src.modules.discord_notifier import send_cve_alert
from src.utils.history_manager import get_processed_cves, save_processed_cve
import time


def run_sentinel():
    print("🚀 Ejecutando CyberSentinel...")
    config = get_config()
    if not config: return

    # 1. Cargamos historial y buscamos CVEs
    processed_ids = get_processed_cves()
    vulnerabilidades = fetch_latest_cves(limit=10)

    nuevos_cves = 0
    for v in vulnerabilidades:
        cve_id = v['cve']['id']

        # 2. Solo procesamos si NO está en el historial
        if cve_id not in processed_ids:
            print(f"🆕 Nueva amenaza detectada: {cve_id}")
            success = send_cve_alert(config["DISCORD_WEBHOOK"], v)

            if success:
                save_processed_cve(cve_id)
                nuevos_cves += 1
                time.sleep(1)  # Evitar rate limit de Discord

    if nuevos_cves == 0:
        print("✅ Todo bajo control. No hay amenazas nuevas desde la última revisión.")
    else:
        print(f"🏁 Ciclo completado. {nuevos_cves} alertas enviadas.")


if __name__ == "__main__":
    run_sentinel()