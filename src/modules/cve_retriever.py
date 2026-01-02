import requests
from src.utils.config_loader import get_config


def fetch_latest_cves(limit=5):
    config = get_config()
    if not config:
        return []

    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    headers = {
        "apiKey": config["NVD_API_KEY"]
    }

    params = {
        "resultsPerPage": limit
    }

    try:
        print(f"🔍 Consultando los últimos {limit} CVEs en NIST NVD...")
        response = requests.get(url, headers=headers, params=params, timeout=15)

        # Si la respuesta es exitosa (200 OK)
        response.raise_for_status()

        data = response.json()
        return data.get("vulnerabilities", [])

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return []


if __name__ == "__main__":
    vulnerabilidades = fetch_latest_cves()

    if vulnerabilidades:
        print(f"✅ Éxito: Se recuperaron {len(vulnerabilidades)} registros.")
        for v in vulnerabilidades:
            cve_id = v['cve']['id']
            status = v['cve']['vulnStatus']
            print(f"📌 {cve_id} | Estado: {status}")
    else:
        print("⚠️ No se pudieron recuperar datos.")