import time
import discord
from datetime import datetime
from src.utils.config_loader import get_config
from src.modules.cve_retriever import fetch_latest_cves
from src.modules.discord_notifier import send_cve_alert, send_health_status
from src.utils.database_manager import init_db, is_cve_processed, save_detection
from src.utils.logger import setup_logger
from src.modules.report_generator import get_weekly_stats, generate_markdown_report
from discord.ext import commands
from discord.ext import tasks

logger = setup_logger()
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(hours=1)
async def background_scan():
    logger.info("🛰️ Iniciando escaneo programado...")
    run_sentinel()

@bot.event
async def on_ready():
    logger.info(f"🛡️ CyberSentinel conectado como {bot.user}")
    if not background_scan.is_running():
        background_scan.start()

# 123
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
        logger.error("❌ No se pudo cargar la configuración.")
        return

    # Cargamos activos de interés desde el .env
    target_cpes = config.get("CPE_LIST", [])
    keywords = config.get("KEYWORDS", [])
    min_score = config.get("MIN_SCORE", 7.0)

    logger.info("📡 Escaneando NIST NVD para nuevas amenazas...")
    vulnerabilidades = fetch_latest_cves(limit=30)

    if not vulnerabilidades:
        logger.warning("⚠️ No se obtuvieron vulnerabilidades en este ciclo.")
        return

    alertas_enviadas = 0

    for v in vulnerabilidades:
        cve_id = v['cve']['id']

        #  VERIFICACIÓN EN BASE DE DATOS
        if not is_cve_processed(cve_id):

            #  ANÁLISIS DE IMPACTO (CPE y Keywords)
            is_exact_match = check_cpe_match(v, target_cpes)
            description = v['cve'].get('descriptions', [{}])[0].get('value', "").lower()
            is_keyword_match = any(word.strip().lower() in description for word in keywords if word.strip())

            #  EXTRACCIÓN DE PUNTAJE CVSS
            metrics = v['cve'].get('metrics', {}).get('cvssMetricV31', [{}])[0]
            base_score = metrics.get('cvssData', {}).get('baseScore', 0.0)
            vuln_status = v['cve'].get('vulnStatus', 'N/A')

            # Define si es prioridad
            es_prioridad = is_exact_match or is_keyword_match

            #  LÓGICA DE TRIAGE
            if es_prioridad or base_score >= min_score:
                logger.info(f"🎯 Coincidencia detectada: {cve_id} (Score: {base_score})")

                # Enviar a Discord
                success = send_cve_alert(
                    config["DISCORD_WEBHOOK"],
                    v,
                    base_score,
                    is_priority=es_prioridad
                )

                if success:
                    # Guardar en SQLite
                    save_detection(
                        cve_id=cve_id,
                        description=description[:250],
                        score=base_score,
                        severity=vuln_status,
                        is_priority=es_prioridad
                    )
                    alertas_enviadas += 1
                    time.sleep(1)
            else:
                save_detection(cve_id, "Filtrado: Bajo impacto", base_score, "IGNORED", False)

    logger.info(f"🏁 Ciclo terminado. Alertas procesadas: {alertas_enviadas}")


if __name__ == "__main__":
    init_db()

    logger.info("🛡️ CyberSentinel v2.0 (SQL Engine) iniciado.")
    last_health_check = None

    while True:
        try:
            current_date = datetime.now().date()
            if last_health_check != current_date:
                config = get_config()
                if config:
                    from src.utils.database_manager import DB_PATH
                    import sqlite3

                    conn = sqlite3.connect(DB_PATH)
                    total_cves = conn.execute('SELECT COUNT(*) FROM detections').fetchone()[0]
                    conn.close()

                    stats = {
                        "total_processed": total_cves,
                        "last_run": datetime.now().strftime("%H:%M:%S")
                    }
                    send_health_status(config["DISCORD_WEBHOOK"], stats)
                    last_health_check = current_date
                    logger.info("💚 Healthcheck diario enviado exitosamente.")
                    if current_date.weekday() == 6:  # 6 es Domingo
                        logger.info("📅 Domingo detectado: Generando reporte semanal de impacto...")
                        stats = get_weekly_stats()
                        report_path = generate_markdown_report(stats)
                        logger.info(f"✅ Reporte semanal generado con éxito en: {report_path}")

            run_sentinel()

            logger.info("😴 Durmiendo 60 minutos hasta el próximo escaneo...")
            time.sleep(3600)

        except Exception as e:
            logger.error(f"❌ Error crítico en el ciclo principal: {e}")
            time.sleep(60)