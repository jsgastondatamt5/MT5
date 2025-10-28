import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 🔑 Polygon API Key (consider using environment variable: os.getenv('POLYGON_API_KEY'))
API_KEY = "xDz4sl2a8Xht_z0TH8_svpSB309X17kv"

# 📅 Rango de fechas
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 10, 2)

# 🧲 Descargar datos de EURUSD en timeframe de 1 minuto
symbol = "C:EURUSD"
data = []

print(f"📥 Descargando datos de {symbol} desde {start_date.date()} hasta {end_date.date()}...")
current_date = start_date
total_days = (end_date - start_date).days
day_count = 0

while current_date < end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date_str}/{date_str}?adjusted=true&sort=asc&limit=50000&apiKey={API_KEY}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
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
        
        day_count += 1
        if day_count % 10 == 0:
            print(f"   Progreso: {day_count}/{total_days} días descargados ({len(data)} registros)")
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Error descargando datos para {date_str}: {e}")
    
    current_date += timedelta(days=1)

print(f"✅ Descarga completa: {len(data)} registros obtenidos")

# Guardar CSV
df = pd.DataFrame(data)
csv_filename = "eurusd_1min.csv"
df.to_csv(csv_filename, index=False)
print(f"💾 Datos guardados en {csv_filename}")

# 🔐 Autenticación con Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']
creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    print("🔓 Token de autorización encontrado")

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        print("🔄 Refrescando token expirado...")
        creds.refresh(Request())
    else:
        print("\n🔐 Iniciando proceso de autorización de Google Drive...")
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=SCOPES,
            redirect_uri='http://localhost:8080'  # Debe coincidir con credentials.json
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        print("\n" + "="*80)
        print("🔗 PASO 1: Abre este enlace en tu navegador y autoriza el acceso:")
        print("="*80)
        print(auth_url)
        print("="*80)
        print("\n📝 PASO 2: Después de autorizar, copia el código de la URL")
        print("   (Ejemplo: http://localhost:8080/?code=ESTE_ES_EL_CODIGO&scope=...)")
        print("\n🔑 PASO 3: Pega el código aquí:")
        
        code = input(">>> ").strip()
        
        if not code:
            print("❌ Error: No se proporcionó ningún código")
            exit(1)
        
        try:
            flow.fetch_token(code=code)
            creds = flow.credentials
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("✅ Autorización exitosa! Token guardado en token.json")
        except Exception as e:
            print(f"❌ Error durante la autorización: {e}")
            exit(1)

# ☁️ Subir archivo a Drive
print("\n☁️  Subiendo archivo a Google Drive...")
file_path = csv_filename

try:
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    file_id = file.get('id')
    print(f"\n{'='*80}")
    print(f"✅ ¡Éxito! Archivo subido a Google Drive")
    print(f"{'='*80}")
    print(f"📄 Nombre: {os.path.basename(file_path)}")
    print(f"🆔 ID: {file_id}")
    print(f"🔗 URL: https://drive.google.com/file/d/{file_id}/view")
    print(f"{'='*80}")
    
except Exception as e:
    print(f"❌ Error al subir archivo a Google Drive: {e}")
    exit(1)
