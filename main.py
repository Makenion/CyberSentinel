from src.utils.config_loader import get_config
from src.modules.cve_retriever import fetch_latest_cves
from src.modules.discord_notifier import send_cve_alert
import time


def run_sentinel():
    print("🚀 Iniciando CyberSentinel...")
    config = get_config()

    if not config:
        return

    # 1. Buscamos los últimos 3 CVEs
    vulnerabilidades = fetch_latest_cves(limit=3)

    if not vulnerabilidades:
        print("✅ No se encontraron nuevas amenazas.")
        return

    print(f"📡 Procesando {len(vulnerabilidades)} vulnerabilidades...")

    # 2. Enviamos cada una a Discord
    for v in vulnerabilidades:
        success = send_cve_alert(config["DISCORD_WEBHOOK"], v)
        if success:
            print(f"🔔 Alerta enviada: {v['cve']['id']}")
        time.sleep(1)  # Pausa técnica para evitar spam


if __name__ == "__main__":
    run_sentinel()