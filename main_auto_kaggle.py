"""
Polygon Data Downloader - Auto Date Range & Kaggle Integration
- Descarga desde hoy hacia atrás el máximo posible
- Sube a Google Drive
- Notifica a Kaggle con el file ID para procesamiento
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

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = os.getenv('POLYGON_API_KEY', 'xDz4sl2a8Xht_z0TH8_svpSB309X17kv')
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

# Date range - AUTOMÁTICO: desde hoy hacia atrás
END_DATE = datetime.now()  # Hoy
# Máximo disponible en free tier de Polygon: ~2 años para stocks, menos para forex
DAYS_TO_DOWNLOAD = 365  # 1 año (ajusta según necesites)
START_DATE = END_DATE - timedelta(days=DAYS_TO_DOWNLOAD)

# Symbol options
FOREX_SYMBOL = "C:EURUSD"
STOCK_SYMBOL = "AAPL"

# Rate limiting
REQUESTS_PER_MINUTE = 5
DELAY_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE

# Google OAuth
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = 'token.json'

# Kaggle notification configuration
KAGGLE_WEBHOOK_URL = os.getenv('KAGGLE_WEBHOOK_URL', None)  # Webhook endpoint
KAGGLE_KERNEL_URL = os.getenv('KAGGLE_KERNEL_URL', None)    # Kaggle API endpoint
NOTIFICATION_FILE = 'drive_file_info.json'  # Local file with file info

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_optimal_date_range(symbol_type='stock'):
    """
    Calcula el rango de fechas óptimo según el tipo de dato
    
    Returns:
        tuple: (start_date, end_date, description)
    """
    end = datetime.now()
    
    # Diferentes límites según el tipo de dato
    if symbol_type == 'forex':
        # Forex en free tier es muy limitado, mejor usar menos días
        days = 30  # 1 mes
        desc = "Último mes (limitación forex free tier)"
    elif symbol_type == 'stock':
        # Stocks tienen mejor disponibilidad
        days = 365  # 1 año
        desc = "Último año completo"
    else:
        days = 90  # Por defecto 3 meses
        desc = "Últimos 3 meses"
    
    start = end - timedelta(days=days)
    
    return start, end, desc


def check_api_access(symbol, api_key):
    """Check if the API key has access to the specified symbol"""
    test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{test_date}/{test_date}?adjusted=true&sort=asc&limit=5&apiKey={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("resultsCount", 0) > 0:
                return True, f"✅ Access confirmed for {symbol}"
            else:
                return False, f"⚠️  No data available for {symbol} (may not be a trading day)"
        elif response.status_code == 403:
            return False, f"❌ No access to {symbol}. Your API plan may not include this data type."
        elif response.status_code == 429:
            return False, f"⚠️  Rate limited. Wait a moment and try again."
        else:
            return False, f"❌ Error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"


def download_data_with_rate_limit(symbol, start_date, end_date, api_key, delay=12):
    """Download historical data with automatic rate limiting"""
    print(f"\n📥 Downloading {symbol} data from {start_date.date()} to {end_date.date()}...")
    print(f"⏱️  Rate limit: {REQUESTS_PER_MINUTE} requests/minute ({delay:.1f}s between requests)")
    
    data = []
    current_date = start_date
    total_days = (end_date - start_date).days
    day_count = 0
    success_count = 0
    error_count = 0
    
    # Estimación de tiempo
    estimated_minutes = (total_days * delay) / 60
    print(f"⏰ Estimated time: {estimated_minutes:.1f} minutes for {total_days} days\n")
    
    while current_date < end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date_str}/{date_str}?adjusted=true&sort=asc&limit=50000&apiKey={api_key}"
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                
                if results:
                    for item in results:
                        data.append({
                            "timestamp": datetime.fromtimestamp(item["t"] / 1000),
                            "open": item["o"],
                            "high": item["h"],
                            "low": item["l"],
                            "close": item["c"],
                            "volume": item["v"]
                        })
                    success_count += 1
                
                day_count += 1
                if day_count % 10 == 0:
                    progress_pct = (day_count / total_days) * 100
                    print(f"   Progress: {progress_pct:.1f}% | {day_count}/{total_days} days | {len(data):,} records | ✓ {success_count} ✗ {error_count}")
            
            elif response.status_code == 403:
                print(f"\n❌ Access denied for {symbol}!")
                return None
            
            elif response.status_code == 429:
                print(f"\n⚠️  Rate limit hit on {date_str}. Waiting 60 seconds...")
                time.sleep(60)
                continue
            
            else:
                error_count += 1
                if error_count <= 3:
                    print(f"   ⚠️  Error {response.status_code} for {date_str}")
        
        except requests.exceptions.RequestException as e:
            error_count += 1
            if error_count <= 3:
                print(f"   ⚠️  Connection error for {date_str}: {e}")
        
        current_date += timedelta(days=1)
        
        if current_date < end_date:
            time.sleep(delay)
    
    print(f"\n✅ Download complete:")
    print(f"   Total records: {len(data):,}")
    print(f"   Successful days: {success_count}/{total_days}")
    print(f"   Errors: {error_count}")
    
    return pd.DataFrame(data) if data else None


def get_google_credentials(credentials_file, token_file, scopes):
    """Get Google Drive credentials"""
    creds = None
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
        print("🔓 Existing authorization token found")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("\n🔐 Starting Google Drive authorization...")
            flow = Flow.from_client_secrets_file(
                credentials_file,
                scopes=scopes,
                redirect_uri='http://localhost:8080'
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print("\n" + "="*80)
            print("🔗 STEP 1: Open this link in your browser:")
            print("="*80)
            print(auth_url)
            print("="*80)
            print("\n🔑 STEP 2: Paste the authorization code here:")
            
            code = input(">>> ").strip()
            
            if not code:
                raise ValueError("No authorization code provided")
            
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            
            print("✅ Authorization successful!")
    
    return creds


def make_file_public(file_id, credentials):
    """
    Hace un archivo de Drive públicamente accesible
    Necesario para que Kaggle pueda descargarlo sin autenticación
    
    Args:
        file_id: Google Drive file ID
        credentials: Google credentials
    
    Returns:
        bool: Success status
    """
    print(f"   🌍 Making file public...")
    
    service = build('drive', 'v3', credentials=credentials)
    
    try:
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id'
        ).execute()
        
        print(f"   ✅ File is now publicly accessible")
        return True
    
    except Exception as e:
        print(f"   ⚠️  Error making file public: {e}")
        print(f"   You may need to make it public manually")
        return False


def upload_to_drive(file_path, credentials, folder_id=None, make_public=True):
    """
    Upload file to Google Drive
    
    Args:
        file_path: Local file path
        credentials: Google credentials
        folder_id: Optional Drive folder ID to upload to
        make_public: If True, makes file publicly accessible for Kaggle
    
    Returns:
        tuple: (file_id, file_url, download_url)
    """
    print(f"\n☁️  Uploading {os.path.basename(file_path)} to Google Drive...")
    
    service = build('drive', 'v3', credentials=credentials)
    
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    file_id = file.get('id')
    web_link = file.get('webViewLink', f"https://drive.google.com/file/d/{file_id}/view")
    
    # Hacer público para Kaggle
    if make_public:
        make_file_public(file_id, credentials)
    
    # URL de descarga directa para gdown/Kaggle
    download_url = f"https://drive.google.com/uc?id={file_id}"
    
    return file_id, web_link, download_url


def notify_kaggle_webhook(file_id, file_url, metadata, webhook_url):
    """
    Envía notificación a Kaggle vía webhook
    
    Args:
        file_id: Google Drive file ID
        file_url: Google Drive file URL
        metadata: Dict con metadata adicional
        webhook_url: URL del webhook
    """
    print("\n📤 Sending notification to Kaggle webhook...")
    
    payload = {
        "drive_file_id": file_id,
        "drive_file_url": file_url,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Webhook notification sent successfully")
            return True
        else:
            print(f"⚠️  Webhook returned status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")
        return False


def save_file_info_locally(file_id, file_url, metadata, filename=NOTIFICATION_FILE):
    """
    Guarda información del archivo localmente en JSON
    Útil si no tienes webhook configurado
    """
    print(f"\n💾 Saving file info to {filename}...")
    
    info = {
        "drive_file_id": file_id,
        "drive_file_url": file_url,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"✅ File info saved: {filename}")
        print(f"   You can read this from Kaggle or other services")
        return True
    
    except Exception as e:
        print(f"❌ Error saving file info: {e}")
        return False


def trigger_kaggle_kernel(file_id, file_url, metadata):
    """
    Trigger a Kaggle kernel/notebook via API
    Requires Kaggle API credentials
    """
    print("\n🚀 Triggering Kaggle kernel...")
    
    # This would require kaggle API setup
    # For now, we'll create the command that the user can run
    
    kaggle_command = f"""
# To trigger a Kaggle kernel with this file:
# 1. Install kaggle CLI: pip install kaggle
# 2. Set up credentials: https://github.com/Kaggle/kaggle-api#api-credentials
# 3. Run this command:

kaggle kernels push -p /path/to/kernel \\
  -m "New data available: {file_id}" \\
  -e "DRIVE_FILE_ID={file_id}" \\
  -e "DRIVE_FILE_URL={file_url}"
"""
    
    print(kaggle_command)
    return kaggle_command


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🚀 Auto Data Downloader with Kaggle Integration")
    print("="*80)
    print(f"📅 Today: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"📊 Will download maximum available data")
    print("="*80)
    
    # Step 1: Check API access
    print("\n🔍 Checking API access...")
    
    forex_access, forex_msg = check_api_access(FOREX_SYMBOL, API_KEY)
    print(f"   Forex ({FOREX_SYMBOL}): {forex_msg}")
    
    stock_access, stock_msg = check_api_access(STOCK_SYMBOL, API_KEY)
    print(f"   Stock ({STOCK_SYMBOL}): {stock_msg}")
    
    # Determine which symbol to use and calculate optimal date range
    if forex_access:
        symbol = FOREX_SYMBOL
        symbol_type = 'forex'
        output_file = f"eurusd_data_{datetime.now().strftime('%Y%m%d')}.csv"
        print(f"\n✅ Using forex data: {symbol}")
    elif stock_access:
        symbol = STOCK_SYMBOL
        symbol_type = 'stock'
        output_file = f"stock_data_{datetime.now().strftime('%Y%m%d')}.csv"
        print(f"\n⚠️  Forex not available. Using stock data: {symbol}")
    else:
        print("\n❌ ERROR: No data access available!")
        return
    
    # Calculate optimal date range
    start_date, end_date, date_desc = calculate_optimal_date_range(symbol_type)
    print(f"\n📅 Date range: {date_desc}")
    print(f"   From: {start_date.strftime('%Y-%m-%d')}")
    print(f"   To: {end_date.strftime('%Y-%m-%d')}")
    print(f"   Days: {(end_date - start_date).days}")
    
    # Step 2: Download data
    df = download_data_with_rate_limit(
        symbol, 
        start_date, 
        end_date, 
        API_KEY, 
        DELAY_BETWEEN_REQUESTS
    )
    
    if df is None or df.empty:
        print("\n❌ No data downloaded. Exiting.")
        return
    
    # Step 3: Save to CSV
    print(f"\n💾 Saving data to {output_file}...")
    df.to_csv(output_file, index=False)
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"✅ File saved: {len(df):,} rows ({file_size_mb:.2f} MB)")
    
    # Prepare metadata
    metadata = {
        "symbol": symbol,
        "symbol_type": symbol_type,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "total_rows": len(df),
        "file_size_mb": round(file_size_mb, 2),
        "columns": list(df.columns),
        "generated_at": datetime.now().isoformat()
    }
    
    # Step 4: Upload to Google Drive
    try:
        creds = get_google_credentials(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        file_id, file_url, download_url = upload_to_drive(output_file, creds, make_public=True)
        
        print("\n" + "="*80)
        print("✅ SUCCESS! File uploaded to Google Drive")
        print("="*80)
        print(f"📄 File: {output_file}")
        print(f"📊 Records: {len(df):,}")
        print(f"🆔 Drive ID: {file_id}")
        print(f"🔗 View: {file_url}")
        print(f"📥 Direct Download: {download_url}")
        print("="*80)
        
        # Update metadata with download URL
        metadata['download_url'] = download_url
        
        # Step 5: Notify Kaggle / Save file info
        print("\n" + "="*80)
        print("📡 Notification Options")
        print("="*80)
        
        notification_sent = False
        
        # Option 1: Webhook
        if KAGGLE_WEBHOOK_URL:
            notification_sent = notify_kaggle_webhook(
                file_id, file_url, metadata, KAGGLE_WEBHOOK_URL
            )
        
        # Option 2: Save locally (always do this as backup)
        save_file_info_locally(file_id, file_url, metadata)
        
        # Option 3: Show Kaggle command
        if not notification_sent:
            print("\n💡 To use this data in Kaggle:")
            print("\n   Method 1: Read from Drive directly in Kaggle notebook:")
            print(f"   drive_file_id = '{file_id}'")
            print(f"   # Use gdown: gdown.download('https://drive.google.com/uc?id={file_id}')")
            
            print("\n   Method 2: Copy file info from drive_file_info.json")
            print(f"   # Upload {NOTIFICATION_FILE} to Kaggle dataset")
            
            print("\n   Method 3: Set environment variable in Kaggle:")
            print(f"   DRIVE_FILE_ID = {file_id}")
            
            print("\n   Method 4: Use direct download URL:")
            print(f"   URL = '{download_url}'")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Upload error: {e}")
        print(f"   Your data is saved locally in: {output_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Script interrupted by user")
        print("   Any downloaded data has been saved")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
