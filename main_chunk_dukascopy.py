"""
Dukascopy Data Downloader with Kaggle Integration
- Descarga datos forex de alta calidad desde Dukascopy
- Sube a Google Drive
- Crea Forrest.py con el file_id
- Pushea Forrest.py a Kaggle para procesamiento
- Actualiza repo de GitHub
"""

import pandas as pd
from datetime import datetime, timedelta
import os
import json
import dukascopy_python
from dukascopy_python import instruments
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

CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH')
KAGGLE_CONFIG_FILE = os.getenv('KAGGLE_CONFIG_PATH')

# Date range - AUTOMÁTICO: desde hoy hacia atrás
END_DATE = datetime.now()
DAYS_TO_DOWNLOAD = int(os.getenv('DAYS_TO_DOWNLOAD', '365'))  # 12 meses por defecto
START_DATE = END_DATE - timedelta(days=DAYS_TO_DOWNLOAD)

# Dukascopy configuration
# Instrumentos disponibles: EURUSD, GBPUSD, USDJPY, etc.
FOREX_PAIRS = {
    'EURUSD': instruments.INSTRUMENT_FX_MAJORS_EUR_USD,
    'GBPUSD': instruments.INSTRUMENT_FX_MAJORS_GBP_USD,
    'USDJPY': instruments.INSTRUMENT_FX_MAJORS_USD_JPY,
    'USDCHF': instruments.INSTRUMENT_FX_MAJORS_USD_CHF,
    'AUDUSD': instruments.INSTRUMENT_FX_MAJORS_AUD_USD,
    'USDCAD': instruments.INSTRUMENT_FX_MAJORS_USD_CAD,
    'NZDUSD': instruments.INSTRUMENT_FX_MAJORS_NZD_USD,
}

DEFAULT_PAIR = os.getenv('FOREX_PAIR', 'EURUSD')
INSTRUMENT = FOREX_PAIRS.get(DEFAULT_PAIR, instruments.INSTRUMENT_FX_MAJORS_EUR_USD)

# Timeframe: INTERVAL_MIN_1, INTERVAL_MIN_5, INTERVAL_MIN_15, INTERVAL_MIN_30, INTERVAL_HOUR_1, INTERVAL_DAY_1
TIMEFRAME = dukascopy_python.INTERVAL_MIN_1

# Offer side: OFFER_SIDE_BID, OFFER_SIDE_ASK
OFFER_SIDE = dukascopy_python.OFFER_SIDE_BID

# Google OAuth
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = os.getenv('GOOGLE_TOKEN_PATH')

# GitHub configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'MT5')

# Kaggle configuration
KAGGLE_USERNAME = os.getenv('KAGGLE_USERNAME')
KAGGLE_KERNEL_SLUG = 'forrest-trading-ml'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_optimal_date_range():
    """
    Calcula el rango de fechas óptimo para Dukascopy
    Dukascopy tiene datos históricos muy completos
    """
    end = datetime.now()
    
    # Podemos descargar mucho más datos con Dukascopy
    days = DAYS_TO_DOWNLOAD
    desc = f"Últimos {days} días"
    
    start = end - timedelta(days=days)
    
    return start, end, desc


def test_dukascopy_access():
    """
    Test de acceso a Dukascopy con una pequeña descarga
    """
    try:
        print(f"🔍 Testing Dukascopy access...")
        
        test_end = datetime.now()
        test_start = test_end - timedelta(days=2)
        
        # Test con pequeño rango
        test_df = dukascopy_python.fetch(
            INSTRUMENT,
            TIMEFRAME,
            OFFER_SIDE,
            test_start,
            test_end,
        )
        
        if test_df.empty:
            return False, f"⚠️  No data available from Dukascopy"
        else:
            return True, f"✅ Dukascopy access confirmed - {len(test_df)} records found"
            
    except Exception as e:
        return False, f"❌ Error accessing Dukascopy: {str(e)}"


def download_dukascopy_data(instrument, start_date, end_date, offer_side):
    """
    Download data from Dukascopy
    
    Args:
        instrument: Dukascopy instrument constant
        start_date: Start datetime
        end_date: End datetime
        offer_side: BID or ASK
    
    Returns:
        pd.DataFrame: Downloaded data
    """
    print(f"\n📥 Downloading from Dukascopy...")
    print(f"   Pair: {DEFAULT_PAIR}")
    print(f"   From: {start_date.strftime('%Y-%m-%d')}")
    print(f"   To: {end_date.strftime('%Y-%m-%d')}")
    print(f"   Timeframe: 1 minute")
    print(f"   Offer Side: {'BID' if offer_side == dukascopy_python.OFFER_SIDE_BID else 'ASK'}")
    
    try:
        # Dukascopy puede descargar todo de una vez, no necesita chunks
        df = dukascopy_python.fetch(
            instrument,
            TIMEFRAME,
            offer_side,
            start_date,
            end_date,
        )
        
        if df.empty:
            print("\n❌ No data downloaded")
            return None
        
        # Reset index para tener timestamp como columna
        df = df.reset_index()
        
        # Renombrar la columna del índice a 'timestamp'
        if 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        # Asegurar formato de columnas estándar
        # Dukascopy ya devuelve: timestamp, open, high, low, close, volume
        print(f"\n✅ Download complete: {len(df):,} records")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"   Columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"\n❌ Error downloading from Dukascopy: {e}")
        import traceback
        traceback.print_exc()
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
Data Source: Dukascopy
"""

import os

# CONFIGURACIÓN AUTOMÁTICA DEL FILE_ID
DRIVE_FILE_ID = '{file_id}'
os.environ['DRIVE_FILE_ID'] = DRIVE_FILE_ID

print(f"✅ Using Drive File ID: {{DRIVE_FILE_ID}}")
print("📊 Data Source: Dukascopy (High Quality Forex Data)")

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
            "title": "Forrest Trading ML - Dukascopy Data",
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
    print("🚀 Dukascopy Data Downloader with Kaggle Integration")
    print("="*80)
    print(f"📅 Today: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"💱 Forex Pair: {DEFAULT_PAIR}")
    print(f"⏰ Timeframe: 1 minute")
    print(f"📊 Data Source: Dukascopy (Bank Quality Data)")
    print("="*80)
    
    # Step 1: Test Dukascopy access
    print("\n🔍 Testing Dukascopy access...")
    access_ok, access_msg = test_dukascopy_access()
    print(f"   {access_msg}")
    
    if not access_ok:
        print("\n❌ ERROR: Cannot access Dukascopy!")
        print("   Check your internet connection and try again.")
        return
    
    # Calculate optimal date range
    start_date, end_date, date_desc = calculate_optimal_date_range()
    print(f"\n📅 Date range: {date_desc}")
    print(f"   From: {start_date.strftime('%Y-%m-%d')}")
    print(f"   To: {end_date.strftime('%Y-%m-%d')}")
    print(f"   Days: {(end_date - start_date).days}")
    
    # Output filename
    output_file = f"{DEFAULT_PAIR.lower()}_1min_dukascopy_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # Step 2: Download data
    df = download_dukascopy_data(
        INSTRUMENT,
        start_date,
        end_date,
        OFFER_SIDE
    )
    
    if df is None or df.empty:
        print("\n❌ No data downloaded. Exiting.")
        return
    
    # Step 3: Save to CSV
    print(f"\n💾 Saving data to {output_file}...")
    df.to_csv(output_file, index=False)
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"✅ File saved: {len(df):,} rows ({file_size_mb:.2f} MB)")
    
    # Show data sample
    print(f"\n📊 Data Sample (first 5 rows):")
    print(df.head().to_string())
    
    # Prepare metadata
    metadata = {
        "pair": DEFAULT_PAIR,
        "data_source": "Dukascopy",
        "timeframe": "1min",
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "total_rows": len(df),
        "file_size_mb": round(file_size_mb, 2),
        "columns": list(df.columns),
        "offer_side": "BID" if OFFER_SIDE == dukascopy_python.OFFER_SIDE_BID else "ASK",
        "generated_at": datetime.now().isoformat(),
        "first_timestamp": str(df['timestamp'].min()),
        "last_timestamp": str(df['timestamp'].max())
    }
    
    # Step 4: Upload to Google Drive
    try:
        creds = get_google_credentials(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        file_id, file_url, download_url = upload_to_drive(output_file, creds, make_public=True)
        
        print("\n" + "="*80)
        print("✅ File uploaded to Google Drive")
        print("="*80)
        print(f"📄 File: {output_file}")
        print(f"📊 Records: {len(df):,}")
        print(f"🆔 Drive ID: {file_id}")
        print(f"🔗 View: {file_url}")
        print(f"📥 Direct Download: {download_url}")
        print("="*80)
        
        # Update metadata with download URL
        metadata['file_id'] = file_id
        metadata['download_url'] = download_url
        
        # Save metadata locally
        metadata_file = f"{DEFAULT_PAIR.lower()}_metadata_{datetime.now().strftime('%Y%m%d')}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"\n💾 Metadata saved to {metadata_file}")
        
        # Step 5: Create Forrest.py with the file_id
        forrest_script = create_forrest_script(file_id, 'Forrest.ipynb', 'Forrest.py')
        
        # Step 6: Push Forrest.py to GitHub
        commit_msg = f"Update Forrest.py with Dukascopy data (file_id: {file_id}) - {datetime.now().strftime('%Y-%m-%d')}"
        push_to_github('Forrest.py', commit_msg)
        
        # Step 7: Push to Kaggle
        push_to_kaggle('Forrest.py')
        
        print("\n" + "="*80)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("📊 Dukascopy data uploaded to Google Drive")
        print("📝 Forrest.py created and pushed to GitHub")
        print("🚀 Script deployed to Kaggle")
        print("⏳ Kaggle will process and send results to GitHub")
        print("\n💡 Data Quality: Dukascopy provides bank-quality tick data")
        print("   Perfect for high-frequency trading strategies!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n   Your data is saved locally in: {output_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Script interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
