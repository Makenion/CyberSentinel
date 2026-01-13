import requests
import discord
from discord.ui import View, Button
from src.utils.database_manager import update_cve_status

class AlertView(View):
    def __init__(self, cve_id):
        super().__init__(timeout=None)
        self.cve_id = cve_id

    @discord.ui.button(label="En Revisión", style=discord.ButtonStyle.blurple, custom_id="review")
    async def review_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        update_cve_status(self.cve_id, "REVIEWING")
        await interaction.response.send_message(f"🟠 {self.cve_id} marcado como 'En Revisión'", ephemeral=True)

    @discord.ui.button(label="Ignorar", style=discord.ButtonStyle.gray, custom_id="snooze")
    async def snooze_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        update_cve_status(self.cve_id, "SNOOZED")
        await interaction.response.send_message(f"💤 {self.cve_id} silenciado", ephemeral=True)

def get_severity_color(score, is_priority):
    if is_priority:
        return 10181046  # Color Púrpura (Destaca más)

    if score >= 9.0:
        return 15158332  # Rojo (Crítico)
    elif score >= 7.0:
        return 15105570  # Naranja (Alto)
    elif score >= 4.0:
        return 15844367  # Amarillo (Medio)
    return 3066993  # Verde (Bajo)

def send_cve_alert(webhook_url, cve_data, score, is_priority=False):
    cve_id = cve_data['cve']['id']
    description = cve_data['cve'].get('descriptions', [{}])[0].get('value', 'Sin descripción')
    short_desc = (description[:300] + '...') if len(description) > 300 else description

    title_prefix = "🔥 [PRIORIDAD LOCAL]" if is_priority else "🚨 Vulnerabilidad Detectada"
    dynamic_color = get_severity_color(score, is_priority)

    nist_url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"

    # Construcción del mensaje para Discord
    payload = {
        "embeds": [{
            "title": f"{title_prefix}: {cve_id}",
            "description": short_desc,
            "url": nist_url,
            "color": dynamic_color,
            "fields": [
                {
                    "name": "📊 Puntaje CVSS",
                    "value": f"**{score}**",
                    "inline": True
                },
                {
                    "name": "🛠️ Estado",
                    "value": cve_data['cve'].get('vulnStatus', 'N/A'),
                    "inline": True
                },
                {
                    "name": "📌 Interés",
                    "value": "Stack Tecnológico" if is_priority else "General",
                    "inline": True
                }
            ],
            "footer": {
                "text": "CyberSentinel v1.5 - Inteligencia de Amenazas"
            }
        }]
    }

def send_health_status(webhook_url, stats):
    payload = {
        "embeds": [{
            "title": "💚 CyberSentinel: Reporte de Salud Diario",
            "color": 3066993,  # Verde éxito
            "fields": [
                {"name": "Estado del Servicio", "value": "✅ Operativo", "inline": True},
                {"name": "CVEs Históricos", "value": f"📦 {stats['total_processed']}", "inline": True},
                {"name": "Último Escaneo", "value": f"🕒 {stats['last_run']}", "inline": False}
            ],
            "footer": {"text": "Sistema de monitoreo activo desatendido"}
        }]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            return True
        else:
            print(f"⚠️ Discord respondió con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al enviar healthcheck: {e}")
        return False
