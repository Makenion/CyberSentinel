from src.utils.config_loader import get_config
from src.modules.cve_retriever import fetch_latest_cves
from src.modules.discord_notifier import send_cve_alert
from src.utils.history_manager import get_processed_cves, save_processed_cve
import time


def run_sentinel():
    print("🚀 Iniciando CyberSentinel - Día 4: Modo Filtrado Inteligente")

    config = get_config()
    if not config:
        print("❌ Error crítico: No se pudo cargar la configuración.")
        return

    # Cargar historial de vulnerabilidades ya notificadas
    processed_ids = get_processed_cves()

    # Solicitar las últimas vulnerabilidades
    vulnerabilidades = fetch_latest_cves(limit=20)

    if not vulnerabilidades:
        print("⚠️ No se recibieron datos de la API de NIST o la lista está vacía.")
        return

    nuevas_alertas = 0
    print(f"🔍 Analizando {len(vulnerabilidades)} vulnerabilidades recientes...")

    for v in vulnerabilidades:
        cve_id = v['cve']['id']

        # Extracción segura del puntaje CVSS
        metrics = v['cve'].get('metrics', {}).get('cvssMetricV31', [{}])[0]
        base_score = metrics.get('cvssData', {}).get('baseScore', 0.0)

        # LÓGICA DE FILTRADO
        if cve_id not in processed_ids and base_score >= config["MIN_SCORE"]:
                print(f"🔥 AMENAZA DETECTADA: {cve_id} (Puntaje: {base_score})")

                # Enviar a Discord
                success = send_cve_alert(config["DISCORD_WEBHOOK"], v, base_score)

                if success:
                    # Guardamos en el historial solo si se envió con éxito
                    save_processed_cve(cve_id)
                    nuevas_alertas += 1
                    time.sleep(1)
                else:
                    save_processed_cve(cve_id)
                    print(f"ℹ️ {cve_id} ignorado por bajo impacto (Score: {base_score})")

        if nuevas_alertas == 0:
            print("✅ Escaneo finalizado. Sin nuevas amenazas críticas detectadas.")
        else:
            print(f"🏁 Ciclo completado. {nuevas_alertas} alertas críticas enviadas a Discord.")


if __name__ == "__main__":
    run_sentinel()