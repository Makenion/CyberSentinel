import requests
from src.utils.config_loader import get_config
from datetime import datetime, timedelta

def fetch_latest_cves(limit=20):
    config = get_config()
    if not config: return []

    past_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%S.000')

    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    headers = {"apiKey": config["NVD_API_KEY"]}

    now = datetime.utcnow()
    pub_end = now.strftime('%Y-%m-%dT%H:%M:%S.000')

    params = {
        "resultsPerPage": limit,
        "startIndex": 0,
        "pubStartDate": past_date,
        "pubEndDate": pub_end
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
            references = v['cve'].get('references', [])
            links = [ref.get('url') for ref in references[:3]]
            print(f"📌 {cve_id} | Estado: {status}")
    else:
        print("⚠️ No se pudieron recuperar datos.")