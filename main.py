# main.py actualizado
from src.utils.config_loader import get_config
from src.modules.cve_retriever import fetch_latest_cves
from src.modules.discord_notifier import send_cve_alert
from src.utils.history_manager import get_processed_cves, save_processed_cve
from src.utils.logger import setup_logger
from src.modules.discord_notifier import send_health_status
from datetime import datetime
import time

logger = setup_logger()


def run_sentinel():
    config = get_config()
    if not config: return

    keywords = config.get("KEYWORDS", [])
    processed_ids = get_processed_cves()
    total_processed = len(processed_ids)


    logger.info("📡 Iniciando ciclo de escaneo...")
    vulnerabilidades = fetch_latest_cves(limit=25)

    if not vulnerabilidades:
        logger.warning("⚠️ No se pudo obtener datos de NIST.")
        return

    for v in vulnerabilidades:
        cve_id = v['cve']['id']
        description = v['cve'].get('descriptions', [{}])[0].get('value', "").lower()
        metrics = v['cve'].get('metrics', {}).get('cvssMetricV31', [{}])[0]
        base_score = metrics.get('cvssData', {}).get('baseScore', 0.0)

        is_local_tech = any(word.strip().lower() in description for word in keywords if word.strip())

        if cve_id not in processed_ids:
            if is_local_tech or base_score >= config.get("MIN_SCORE", 7.0):
                logger.info(f"🔥 Alerta detectada: {cve_id} (Score: {base_score})")
                send_cve_alert(config["DISCORD_WEBHOOK"], v, base_score, is_priority=is_local_tech)
                save_processed_cve(cve_id)
            else:
                save_processed_cve(cve_id)
    return total_processed

if __name__ == "__main__":
    logger.info("🛡️ CyberSentinel activado en modo servicio.")
    last_health_check = None
    while True:
        try:
            current_date = datetime.now().date()

            if last_health_check != current_date:
                config = get_config()
                total = len(get_processed_cves())
                stats = {
                    "total_processed": total,
                    "last_run": datetime.now().strftime("%H:%M:%S")
                }

                send_health_status(config["DISCORD_WEBHOOK"], stats)
                last_health_check = current_date
                logger.info("💚 Reporte de salud diario enviado a Discord.")

            run_sentinel()
            logger.info("😴 Ciclo completado. Durmiendo por 60 minutos...")
            time.sleep(3600)
        except KeyboardInterrupt:
            logger.info("🛑 Servicio detenido por el usuario.")
            break
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            time.sleep(60)