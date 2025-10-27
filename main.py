import requests
import pandas as pd
from datetime import datetime, timedelta
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# 🔑 Polygon API Key
API_KEY = "	xDz4sl2a8Xht_z0TH8_svpSB309X17kv"

# 📅 Rango de fechas
start_date = datetime(2023, 10, 1)
end_date = datetime(2023, 10, 2)

# 🧲 Descargar datos de EURUSD en timeframe de 1 minuto
symbol = "C:EURUSD"  # Forex symbol en Polygon
data = []

current_date = start_date
while current_date < end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date_str}/{date_str}?adjusted=true&sort=asc&limit=50000&apiKey={API_KEY}"
    response = requests.get(url)
    results = response.json().get("results", [])
    for item in results:
        data.append({
            "timestamp": datetime.fromtimestamp(item["t"] / 1000),
            "open": item["o"],
            "high": item["h"],
            "low": item["l"],
            "close": item["c"],
            "volume": item["v"]
        })
    current_date += timedelta(days=1)

df = pd.DataFrame(data)
df.to_csv("eurusd_1min.csv", index=False)

# ☁️ Autenticación Google Drive
gauth = GoogleAuth()
gauth.LoadCredentialsFile("credentials.json")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("credentials.json")

drive = GoogleDrive(gauth)

# 📤 Subir archivo
file = drive.CreateFile({'title': 'eurusd_1min.csv'})
file.SetContentFile('eurusd_1min.csv')
file.Upload()

print("✅ Archivo EURUSD 1min subido a Google Drive.")
