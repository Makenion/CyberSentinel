from src.utils.config_loader import get_config
from src.modules.cve_retriever import fetch_latest_cves
from src.modules.discord_notifier import send_cve_alert
from src.utils.history_manager import get_processed_cves, save_processed_cve
import time


def run_sentinel():
    print("🚀 CyberSentinel v1.5 - Modo: Escaneo de Stack Técnico")

    # Carga de configuración
    config = get_config()
    if not config:
        return

    keywords = config.get("KEYWORDS", [])
    min_score = config.get("MIN_SCORE", 7.0)

    # Historial y obtención de datos
    processed_ids = get_processed_cves()
    vulnerabilidades = fetch_latest_cves(limit=25)

    if not vulnerabilidades:
        print("⚠️ No hay datos nuevos para procesar.")
        return

    alertas_enviadas = 0
    print(f"🔍 Analizando {len(vulnerabilidades)} vulnerabilidades contra el stack: {keywords}")

    for v in vulnerabilidades:
        cve_id = v['cve']['id']
        description = v['cve'].get('descriptions', [{}])[0].get('value', "").lower()

        metrics = v['cve'].get('metrics', {}).get('cvssMetricV31', [{}])[0]
        base_score = metrics.get('cvssData', {}).get('baseScore', 0.0)

        is_local_tech = any(word.strip().lower() in description for word in keywords if word.strip())

        if cve_id not in processed_ids:
            if is_local_tech or base_score >= min_score:

                prioridad_msg = "🎯 [TECH LOCAL]" if is_local_tech else "🔥 [CRÍTICO]"
                print(f"{prioridad_msg} {cve_id} (Score: {base_score})")

                success = send_cve_alert(
                    config["DISCORD_WEBHOOK"],
                    v,
                    base_score,
                    is_priority=is_local_tech
                )

                if success:
                    save_processed_cve(cve_id)
                    alertas_enviadas += 1
                    time.sleep(1)
            else:
                save_processed_cve(cve_id)

    print(f"🏁 Escaneo terminado. Alertas enviadas hoy: {alertas_enviadas}")


if __name__ == "__main__":
    run_sentinel()