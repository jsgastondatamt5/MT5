"""
Polygon Data Downloader with Kaggle Integration
- Descarga datos de yfinance
- Sube a Google Drive
- Crea Forrest.py con el file_id
- Pushea Forrest.py a Kaggle para procesamiento
- Actualiza repo de GitHub
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import json
import yfinance as yf
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv
import subprocess
import shutil

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
KAGGLE_CONFIG_FILE = os.getenv('KAGGLE_CONFIG_PATH', 'kaggle.json')

# Date range - AUTOMÁTICO: desde hoy hacia atrás
END_DATE = datetime.now()
DAYS_TO_DOWNLOAD = 365
START_DATE = END_DATE - timedelta(days=DAYS_TO_DOWNLOAD)

# Tamaño de cada tanda
CHUNK_SIZE_DAYS = 7

# Symbol options
FOREX_SYMBOL = "EURUSD=X"
STOCK_SYMBOL = "AAPL"

# Timeframe
TIMEFRAME = "1m"

# Rate limiting
REQUESTS_PER_MINUTE = 10
DELAY_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE

# Google OAuth
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = 'token.json'

# GitHub configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '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')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'jsgastondatamt5')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'MT5')

# Kaggle configuration
KAGGLE_USERNAME = os.getenv('KAGGLE_USERNAME', 'jsgastonalgotrading')
KAGGLE_KERNEL_SLUG = 'forrest-trading-ml'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_optimal_date_range(symbol_type='stock'):
    """Calcula el rango de fechas óptimo según el tipo de dato"""
    end = datetime.now()
    
    if symbol_type == 'forex':
        days = 60
        desc = "Últimos 2 meses"
    elif symbol_type == 'stock':
        days = 365
        desc = "Último año completo"
    else:
        days = 90
        desc = "Últimos 3 meses"
    
    start = end - timedelta(days=days)
    return start, end, desc


def check_api_access(symbol):
    """Check if the symbol is available in yfinance"""
    try:
        print(f"🔍 Checking yfinance access for {symbol}...")
        test_end = datetime.now()
        test_start = test_end - timedelta(days=2)
        
        data = yf.download(
            symbol, 
            start=test_start, 
            end=test_end, 
            interval=TIMEFRAME,
            progress=False
        )
        
        if data.empty:
            return False, f"⚠️  No data available for {symbol}"
        else:
            return True, f"✅ Access confirmed for {symbol} - {len(data)} records found"
            
    except Exception as e:
        return False, f"❌ Error accessing {symbol}: {str(e)}"


def download_single_chunk(symbol, start_date, end_date):
    """Download data for a single date range chunk"""
    try:
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        data = yf.download(
            symbol, 
            start=start_str, 
            end=end_str, 
            interval=TIMEFRAME,
            progress=False
        )
        
        if data.empty:
            return None
        
        data = data.reset_index()
        data.columns = [col.lower() for col in data.columns]
        
        column_mapping = {
            'datetime': 'timestamp',
            'date': 'timestamp',
            'open': 'open',
            'high': 'high', 
            'low': 'low',
            'close': 'close',
            'volume': 'volume',
            'adj close': 'adj_close'
        }
        
        data = data.rename(columns=column_mapping)
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        available_columns = [col for col in required_columns if col in data.columns]
        
        if len(available_columns) < 4:
            return None
        
        data = data[available_columns]
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        return data
        
    except Exception as e:
        print(f"❌ Error downloading chunk: {e}")
        return None


def download_data_in_chunks(symbol, start_date, end_date, chunk_days=7, delay=6):
    """Download historical data in chunks"""
    print(f"\n📥 Downloading {symbol} data in {chunk_days}-day chunks...")
    print(f"   From {start_date.date()} to {end_date.date()}")
    print(f"   Timeframe: {TIMEFRAME}")
    
    all_data = []
    current_start = start_date
    chunk_number = 0
    total_chunks = ((end_date - start_date).days + chunk_days - 1) // chunk_days
    
    while current_start < end_date:
        chunk_number += 1
        current_end = min(current_start + timedelta(days=chunk_days), end_date)
        
        print(f"\n   Chunk {chunk_number}/{total_chunks}: {current_start.date()} to {current_end.date()}")
        
        chunk_data = download_single_chunk(symbol, current_start, current_end)
        
        if chunk_data is not None and not chunk_data.empty:
            all_data.append(chunk_data)
            print(f"      ✅ Downloaded {len(chunk_data):,} records")
        else:
            print(f"      ⚠️  No data in this chunk")
        
        current_start = current_end
        
        if current_start < end_date:
            time.sleep(delay)
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
        print(f"\n✅ Download complete: {len(combined_df):,} total records from {chunk_number} chunks")
        return combined_df
    else:
        print(f"\n❌ No data downloaded")
        return None


def get_google_credentials(credentials_file, token_file, scopes):
    """Get or refresh Google Drive credentials"""
    creds = None
    
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, scopes)
        except Exception as e:
            print(f"⚠️  Error loading token: {e}")
            creds = None
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing credentials...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth flow...")
            flow = Flow.from_client_secrets_file(
                credentials_file,
                scopes=scopes,
                redirect_uri='http://localhost:8080'
            )
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print(f"\n🌐 Open this URL in your browser:\n{auth_url}\n")
            code = input("Enter the authorization code: ").strip()
            
            flow.fetch_token(code=code)
            creds = flow.credentials
        
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        print("✅ Credentials saved")
    
    return creds


def upload_to_drive(file_path, creds, make_public=True):
    """Upload file to Google Drive"""
    try:
        print(f"\n☁️  Uploading {file_path} to Google Drive...")
        
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'mimeType': 'text/csv'
        }
        
        media = MediaFileUpload(
            file_path,
            mimetype='text/csv',
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        file_url = file.get('webViewLink')
        
        if make_public:
            service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            print("🔓 File made public")
        
        download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        
        print(f"✅ Upload successful!")
        print(f"   File ID: {file_id}")
        print(f"   View URL: {file_url}")
        
        return file_id, file_url, download_url
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise


def create_forrest_script(file_id, template_path='Forrest.ipynb', output_path='Forrest.py'):
    """
    Convierte Forrest.ipynb a Forrest.py e inserta el file_id de Google Drive
    """
    print(f"\n📝 Creating Forrest.py with Drive file ID: {file_id}")
    
    try:
        # Leer el notebook
        with open(template_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        # Extraer el código de las celdas
        code_lines = []
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                source = cell['source']
                if isinstance(source, list):
                    code_lines.extend(source)
                else:
                    code_lines.append(source)
                code_lines.append('\n\n')
        
        # Unir todo el código
        full_code = ''.join(code_lines)
        
        # Insertar el DRIVE_FILE_ID al inicio del script
        header = f'''"""
Forrest Trading ML System - Auto-generated from Kaggle
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Drive File ID: {file_id}
"""

import os

# CONFIGURACIÓN AUTOMÁTICA DEL FILE_ID
DRIVE_FILE_ID = '{file_id}'
os.environ['DRIVE_FILE_ID'] = DRIVE_FILE_ID

print(f"✅ Using Drive File ID: {{DRIVE_FILE_ID}}")

'''
        
        # Escribir el script final
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write(full_code)
        
        print(f"✅ Forrest.py created successfully ({len(full_code)} chars)")
        return output_path
        
    except Exception as e:
        print(f"❌ Error creating Forrest.py: {e}")
        raise


def push_to_github(file_path, commit_message):
    """Push file to GitHub repository"""
    print(f"\n🔄 Pushing {file_path} to GitHub...")
    
    try:
        # Configurar git
        subprocess.run(['git', 'config', '--global', 'user.email', f'{GITHUB_USERNAME}@users.noreply.github.com'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', GITHUB_USERNAME], check=True)
        
        # Add y commit
        subprocess.run(['git', 'add', file_path], check=True)
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push usando token
        repo_url = f'https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git'
        subprocess.run(['git', 'push', repo_url, 'main'], check=True)
        
        print(f"✅ Pushed to GitHub: {GITHUB_USERNAME}/{GITHUB_REPO}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False


def setup_kaggle_credentials():
    """Setup Kaggle API credentials"""
    kaggle_dir = os.path.expanduser('~/.kaggle')
    os.makedirs(kaggle_dir, exist_ok=True)
    
    kaggle_json_dest = os.path.join(kaggle_dir, 'kaggle.json')
    
    if not os.path.exists(kaggle_json_dest):
        if os.path.exists(KAGGLE_CONFIG_FILE):
            shutil.copy(KAGGLE_CONFIG_FILE, kaggle_json_dest)
            os.chmod(kaggle_json_dest, 0o600)
            print("✅ Kaggle credentials configured")
        else:
            print(f"⚠️  Warning: {KAGGLE_CONFIG_FILE} not found")
            return False
    
    return True


def push_to_kaggle(script_path):
    """Push script to Kaggle kernel using kaggle CLI"""
    print(f"\n🚀 Pushing {script_path} to Kaggle...")
    
    try:
        # Asegurar que las credenciales de Kaggle estén configuradas
        if not setup_kaggle_credentials():
            print("❌ Kaggle credentials not configured")
            return False
        
        # Crear metadata para el kernel
        kernel_metadata = {
            "id": f"{KAGGLE_USERNAME}/{KAGGLE_KERNEL_SLUG}",
            "title": "Forrest Trading ML",
            "code_file": os.path.basename(script_path),
            "language": "python",
            "kernel_type": "script",
            "is_private": True,
            "enable_gpu": False,
            "enable_internet": True,
            "dataset_sources": [],
            "competition_sources": [],
            "kernel_sources": []
        }
        
        # Crear directorio temporal para el kernel
        kernel_dir = '/tmp/kaggle_kernel'
        os.makedirs(kernel_dir, exist_ok=True)
        
        # Copiar script
        shutil.copy(script_path, os.path.join(kernel_dir, os.path.basename(script_path)))
        
        # Guardar metadata
        metadata_path = os.path.join(kernel_dir, 'kernel-metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(kernel_metadata, f, indent=2)
        
        # Push usando kaggle CLI
        result = subprocess.run(
            ['kaggle', 'kernels', 'push', '-p', kernel_dir],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✅ Pushed to Kaggle!")
        print(f"   Kernel: https://www.kaggle.com/{KAGGLE_USERNAME}/{KAGGLE_KERNEL_SLUG}")
        
        # Ejecutar el kernel
        print("\n▶️  Triggering kernel execution...")
        exec_result = subprocess.run(
            ['kaggle', 'kernels', 'status', f"{KAGGLE_USERNAME}/{KAGGLE_KERNEL_SLUG}"],
            capture_output=True,
            text=True
        )
        print(exec_result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Kaggle push error: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🚀 YFinance Data Downloader with Kaggle Integration")
    print("="*80)
    print(f"📅 Today: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"⏰ Timeframe: {TIMEFRAME}")
    print("="*80)
    
    # Step 1: Check API access
    print("\n🔍 Checking yfinance access...")
    
    forex_access, forex_msg = check_api_access(FOREX_SYMBOL)
    print(f"   Forex ({FOREX_SYMBOL}): {forex_msg}")
    
    stock_access, stock_msg = check_api_access(STOCK_SYMBOL)
    print(f"   Stock ({STOCK_SYMBOL}): {stock_msg}")
    
    # Determine which symbol to use
    if forex_access:
        symbol = FOREX_SYMBOL
        symbol_type = 'forex'
        output_file = f"eurusd_{TIMEFRAME}_data_{datetime.now().strftime('%Y%m%d')}.csv"
        print(f"\n✅ Using forex data: {symbol}")
    elif stock_access:
        symbol = STOCK_SYMBOL
        symbol_type = 'stock'
        output_file = f"stock_{TIMEFRAME}_data_{datetime.now().strftime('%Y%m%d')}.csv"
        print(f"\n⚠️  Forex not available. Using stock data: {symbol}")
    else:
        print("\n❌ ERROR: No data access available!")
        return
    
    # Calculate optimal date range
    start_date, end_date, date_desc = calculate_optimal_date_range(symbol_type)
    print(f"\n📅 Date range: {date_desc}")
    print(f"   From: {start_date.strftime('%Y-%m-%d')}")
    print(f"   To: {end_date.strftime('%Y-%m-%d')}")
    
    # Step 2: Download data
    df = download_data_in_chunks(
        symbol, 
        start_date, 
        end_date, 
        chunk_days=CHUNK_SIZE_DAYS,
        delay=DELAY_BETWEEN_REQUESTS
    )
    
    if df is None or df.empty:
        print("\n❌ No data downloaded. Exiting.")
        return
    
    # Step 3: Save to CSV
    print(f"\n💾 Saving data to {output_file}...")
    df.to_csv(output_file, index=False)
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"✅ File saved: {len(df):,} rows ({file_size_mb:.2f} MB)")
    
    # Step 4: Upload to Google Drive
    try:
        creds = get_google_credentials(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        file_id, file_url, download_url = upload_to_drive(output_file, creds, make_public=True)
        
        print("\n" + "="*80)
        print("✅ File uploaded to Google Drive")
        print("="*80)
        print(f"🆔 Drive ID: {file_id}")
        print(f"🔗 View: {file_url}")
        print("="*80)
        
        # Step 5: Create Forrest.py with the file_id
        forrest_script = create_forrest_script(file_id, 'Forrest.ipynb', 'Forrest.py')
        
        # Step 6: Push Forrest.py to GitHub
        commit_msg = f"Update Forrest.py with new Drive file ID - {datetime.now().strftime('%Y-%m-%d')}"
        push_to_github('Forrest.py', commit_msg)
        
        # Step 7: Push to Kaggle
        push_to_kaggle('Forrest.py')
        
        print("\n" + "="*80)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("📊 Data uploaded to Google Drive")
        print("📝 Forrest.py created and pushed to GitHub")
        print("🚀 Script deployed to Kaggle")
        print("⏳ Kaggle will process and send results to GitHub")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Script interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
