"""
Polygon Data Downloader - EURUSD (Batch 30 Days, Full Year)
Descarga en tandas de 30 días del último año,
guarda todos los CSV intermedios, los une y sube el final a Google Drive.
creado con claude main_auto_kaggle.py y luego con chatgpt
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# ============================================================================
# CONFIG
# ============================================================================
load_dotenv()

API_KEY = os.getenv('POLYGON_API_KEY', 'xDz4sl2a8Xht_z0TH8_svpSB309X17kv')
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = 'token.json'
KAGGLE_WEBHOOK_URL = os.getenv('KAGGLE_WEBHOOK_URL', None)
NOTIFICATION_FILE = 'drive_file_info.json'
REQUESTS_PER_MINUTE = 5
DELAY_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE

# ============================================================================
# HELPERS
# ============================================================================

def download_data_with_rate_limit(symbol, start_date, end_date, api_key, delay=12):
    """Descarga datos minuto a minuto dentro del rango indicado"""
    print(f"\n📥 Descargando {symbol} del {start_date.date()} al {end_date.date()}...")
    data = []
    current_date = start_date
    total_days = (end_date - start_date).days

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date_str}/{date_str}?adjusted=true&sort=asc&limit=50000&apiKey={api_key}"

        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                results = r.json().get("results", [])
                for item in results:
                    data.append({
                        "timestamp": datetime.fromtimestamp(item["t"] / 1000),
                        "open": item["o"],
                        "high": item["h"],
                        "low": item["l"],
                        "close": item["c"],
                        "volume": item["v"]
                    })
            elif r.status_code == 429:
                print(f"⚠️ Rate limit alcanzado ({date_str}), esperando 60s...")
                time.sleep(60)
                continue
            elif r.status_code == 403:
                print("❌ Sin acceso a los datos (403). Verifica tu plan de Polygon.")
                return None
        except Exception as e:
            print(f"⚠️ Error {e} en {date_str}")
        current_date += timedelta(days=1)
        time.sleep(delay)

    df = pd.DataFrame(data)
    print(f"✅ {len(df)} registros descargados en total para este rango.")
    return df

def get_google_credentials(credentials_file, token_file, scopes):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(credentials_file, scopes=scopes, redirect_uri='http://localhost:8080')
            auth_url, _ = flow.authorization_url(prompt='consent')
            print("Abre esta URL y pega el código aquí:\n", auth_url)
            code = input("Código: ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
    return creds

def make_file_public(file_id, credentials):
    service = build('drive', 'v3', credentials=credentials)
    permission = {'type': 'anyone', 'role': 'reader'}
    service.permissions().create(fileId=file_id, body=permission).execute()

def upload_to_drive(file_path, credentials):
    service = build('drive', 'v3', credentials=credentials)
    media = MediaFileUpload(file_path, resumable=True)
    file_metadata = {'name': os.path.basename(file_path)}
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    file_id = file.get('id')
    make_file_public(file_id, credentials)
    download_url = f"https://drive.google.com/uc?id={file_id}"
    print(f"☁️ Subido a Drive: {download_url}")
    return file_id, download_url

def save_file_info_locally(file_id, file_url, metadata, filename=NOTIFICATION_FILE):
    info = {
        "drive_file_id": file_id,
        "drive_file_url": file_url,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata
    }
    with open(filename, 'w') as f:
        json.dump(info, f, indent=2)
    print(f"💾 Guardada info local en {filename}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    symbol = "C:EURUSD"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    batch_size = 30

    print("\n==============================================")
    print(f"🚀 Descargando EUR/USD del último año en tandas de {batch_size} días")
    print("==============================================")

    all_batches = []
    current_start = start_date
    batch_idx = 1

    while current_start < end_date:
        current_end = min(current_start + timedelta(days=batch_size - 1), end_date)
        batch_name = f"eurusd_batch_{batch_idx}_{current_start.date()}_to_{current_end.date()}.csv"

        df_batch = download_data_with_rate_limit(symbol, current_start, current_end, API_KEY, DELAY_BETWEEN_REQUESTS)

        if df_batch is not None and not df_batch.empty:
            df_batch.to_csv(batch_name, index=False)
            print(f"💾 Guardado {batch_name} ({len(df_batch)} filas)")
            all_batches.append(df_batch)
        else:
            print(f"⚠️ Sin datos en el rango {current_start.date()} - {current_end.date()}")

        batch_idx += 1
        current_start = current_end + timedelta(days=1)

    # Unir todo
    if not all_batches:
        print("❌ No se descargaron datos. Saliendo.")
        return

    df_full = pd.concat(all_batches, ignore_index=True).sort_values("timestamp")
    output_file = f"eurusd_data_{datetime.now().strftime('%Y%m%d')}.csv"
    df_full.to_csv(output_file, index=False)
    size_mb = os.path.getsize(output_file) / (1024 * 1024)

    print(f"\n✅ Archivo final: {output_file} ({len(df_full)} filas, {size_mb:.2f} MB)")

    # Subida y notificación
    creds = get_google_credentials(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
    file_id, download_url = upload_to_drive(output_file, creds)

    metadata = {
        "symbol": symbol,
        "batches": batch_idx - 1,
        "rows_total": len(df_full),
        "file_size_mb": round(size_mb, 2),
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "download_url": download_url
    }

    save_file_info_locally(file_id, download_url, metadata)
    print("\n🎯 Proceso completado con éxito.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏸️ Interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
