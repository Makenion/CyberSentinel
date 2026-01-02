import os
from dotenv import load_dotenv

load_dotenv()

def get_config():
    config = {
        "NVD_API_KEY": os.getenv("NVD_API_KEY"),
        "DISCORD_WEBHOOK": os.getenv("DISCORD_WEBHOOK_URL")
    }

    if not config["NVD_API_KEY"] or not config["DISCORD_WEBHOOK"]:
        print(f"⚠️ ERROR: No se detectaron las variables en el .env")
        return None

    return config

if __name__ == "__main__":
    conf = get_config()
    if conf:
        print("✅ Configuración cargada correctamente.")