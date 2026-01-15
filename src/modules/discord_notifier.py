import discord
from discord.ui import View, Button
from src.utils.database_manager import update_cve_status
from src.utils.cvss_parser import parse_vector

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

async def send_cve_alert(channel, cve_data, score, is_priority, links):
    embed = discord.Embed(
        title=f"{'🔥' if is_priority else '🚨'} CVE: {cve_data['cve']['id']}",
        description=cve_data['cve'].get('descriptions', [{}])[0].get('value', '')[:300],
        color=discord.Color.red() if is_priority else discord.Color.orange()
    )
    embed.add_field(name="📊 Puntaje", value=f"**{score}**", inline=True)

    if links:
        embed.add_field(name="🔗 Links", value="\n".join(links[:2]), inline=False)

    view = AlertView(cve_data['cve']['id'])
    await channel.send(embed=embed, view=view)

async def send_health_status(channel, stats):
        embed = discord.Embed(
            title="💚 CyberSentinel: Reporte de Salud Diario",
            color=3066993,  # Tu verde éxito
            description="Estado del sistema de monitoreo en Limache"
        )

        embed.add_field(name="✅ Estado del Servicio", value="Operativo", inline=True)
        embed.add_field(name="📦 CVEs Históricos", value=f"{stats['total_processed']}", inline=True)
        embed.add_field(name="🕒 Último Escaneo", value=f"{stats['last_run']}", inline=False)

        embed.set_footer(text="Sistema de monitoreo activo desatendido")

        await channel.send(embed=embed)


