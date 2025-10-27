import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 🔑 Polygon API Key
API_KEY = "xDz4sl2a8Xht_z0TH8_svpSB309X17kv"

# 📅 Rango de fechas
start_date = datetime(2023, 10, 1)
end_date = datetime(2023, 10, 2)

# 🧲 Descargar datos de EURUSD en timeframe de 1 minuto
symbol = "C:EURUSD"
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

# 🔐 Autenticación manual para Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']
creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        print("🔗 Abre este enlace en tu navegador y autoriza el acceso:")
        print(auth_url)
        code = input("🔑 Pega aquí el código de autorización: ")
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

# ☁️ Subir archivo a Google Drive
file_path = "eurusd_1min.csv"
service = build('drive', 'v3', credentials=creds)
file_metadata = {'name': os.path.basename(file_path)}
media = MediaFileUpload(file_path, resumable=True)
file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

print(f"✅ Archivo subido a Google Drive con ID: {file.get('id')}")
print("✅ Archivo EURUSD 1min subido a Google Drive.")
