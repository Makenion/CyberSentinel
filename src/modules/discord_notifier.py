import requests


def send_cve_alert(webhook_url, cve_data):

    cve_id = cve_data['cve']['id']
    description = cve_data['cve']['descriptions'][0]['value']
    short_desc = (description[:300] + '...') if len(description) > 300 else description

    payload = {
        "embeds": [{
            "title": f"🚨 Vulnerabilidad Detectada: {cve_id}",
            "description": short_desc,
            "color": 15158332,  # Color Rojo (hex: #E74C3C)
            "fields": [
                {"name": "Estado", "value": cve_data['cve']['vulnStatus'], "inline": True},
                {"name": "Fuente", "value": "NIST NVD", "inline": True}
            ],
            "footer": {"text": "CyberSentinel - Alerta de Seguridad"}
        }]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        return response.status_code == 204
    except Exception as e:
        print(f"❌ Error al enviar a Discord: {e}")
        return False