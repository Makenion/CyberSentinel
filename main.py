import time
from datetime import datetime
from src.utils.config_loader import get_config
from src.modules.cve_retriever import fetch_latest_cves
from src.modules.discord_notifier import send_cve_alert, send_health_status
from src.utils.history_manager import get_processed_cves, save_processed_cve
from src.utils.logger import setup_logger

logger = setup_logger()


def check_cpe_match(cve_item, target_cpes):
    configurations = cve_item.get('cve', {}).get('configurations', [])
    for config_item in configurations:
        for node in config_item.get('nodes', []):
            for cpe_match in node.get('cpeMatch', []):
                criteria = cpe_match.get('criteria', '')
                if any(target.lower() in criteria.lower() for target in target_cpes if target):
                    return True
    return False


def run_sentinel():
    config = get_config()
    if not config:
        return

    # Carga listas de interés
    target_cpes = config.get("CPE_LIST", [])
    keywords = config.get("KEYWORDS", [])
    processed_ids = get_processed_cves()

    logger.info("📡 Escaneando nuevas vulnerabilidades en NIST...")
    vulnerabilidades = fetch_latest_cves(limit=30)

    if not vulnerabilidades:
        return

    for v in vulnerabilidades:
        cve_id = v['cve']['id']

        if cve_id not in processed_ids:
            # FILTRADO QUIRÚRGICO
            is_exact_match = check_cpe_match(v, target_cpes)

            # FILTRADO POR PALABRAS CLAVE
            description = v['cve'].get('descriptions', [{}])[0].get('value', "").lower()
            is_keyword_match = any(word.strip().lower() in description for word in keywords if word.strip())

            # EVALUACIÓN DE PUNTAJE
            metrics = v['cve'].get('metrics', {}).get('cvssMetricV31', [{}])[0]
            base_score = metrics.get('cvssData', {}).get('baseScore', 0.0)

            # LÓGICA DE ALERTA
            if is_exact_match or is_keyword_match or base_score >= config.get("MIN_SCORE", 7.0):
                prioridad = is_exact_match or is_keyword_match

                logger.info(f"🔥 Coincidencia encontrada: {cve_id} (Exacta: {is_exact_match})")

                send_cve_alert(
                    config["DISCORD_WEBHOOK"],
                    v,
                    base_score,
                    is_priority=prioridad
                )
                save_processed_cve(cve_id)
            else:
                save_processed_cve(cve_id)


if __name__ == "__main__":
    logger.info("🛡️ CyberSentinel v1.8 - Modo Precisión CPE Activado")
    last_health_check = None

    while True:
        try:
            # Healthcheck Diario
            current_date = datetime.now().date()
            if last_health_check != current_date:
                config = get_config()
                stats = {
                    "total_processed": len(get_processed_cves()),
                    "last_run": datetime.now().strftime("%H:%M:%S")
                }
                send_health_status(config["DISCORD_WEBHOOK"], stats)
                last_health_check = current_date

            run_sentinel()
            logger.info("😴 Ciclo completado. Esperando 60 minutos...")
            time.sleep(3600)

        except Exception as e:
            logger.error(f"❌ Error en el ciclo principal: {e}")
            time.sleep(60)