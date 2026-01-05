import requests


def send_cve_alert(webhook_url, cve_data, score):
    def get_severity_color(s):
        if s >= 9.0: return 15158332  # Rojo Crítico
        if s >= 7.0: return 15105570  # Naranja Alto
        if s >= 4.0: return 15844367  # Amarillo Medio
        return 3066993  # Verde Bajo

    dynamic_color = get_severity_color(score)

    cve_id = cve_data['cve']['id']
    description = cve_data['cve']['descriptions'][0]['value']
    short_desc = (description[:300] + '...') if len(description) > 300 else description

    nist_url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"

    payload = {
        "embeds": [{
            "title": f"🚨 Vulnerabilidad Detectada: {cve_id}",
            "url": nist_url,
            "description": short_desc,
            "color": dynamic_color,
            "fields": [
                {"name": "Puntaje CVSS", "value": f"**{score}**", "inline": True},
                {"name": "Estado", "value": cve_data['cve']['vulnStatus'], "inline": True}
            ],
            "footer": {"text": "CyberSentinel - Sistema de Triaje"}
        }]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        return response.status_code == 204
    except Exception as e:
        print(f"❌ Error al enviar a Discord: {e}")
        return False