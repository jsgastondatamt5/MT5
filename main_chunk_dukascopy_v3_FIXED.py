"""
Dukascopy Data Downloader with Kaggle Integration - V3 FIXED
- Arregla el problema de comillas triples
- Crea Forrest.py y Forrest.ipynb correctamente
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

CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
KAGGLE_CONFIG_FILE = os.getenv('KAGGLE_CONFIG_PATH', 'kaggle.json')

# Date range - AUTOMÁTICO: desde hoy hacia atrás
END_DATE = datetime.now()
DAYS_TO_DOWNLOAD = int(os.getenv('DAYS_TO_DOWNLOAD', '365'))
START_DATE = END_DATE - timedelta(days=DAYS_TO_DOWNLOAD)

# Dukascopy configuration
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

TIMEFRAME = dukascopy_python.INTERVAL_MIN_1
OFFER_SIDE = dukascopy_python.OFFER_SIDE_BID

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

def calculate_optimal_date_range():
    """Calcula el rango de fechas óptimo para Dukascopy"""
    end = datetime.now()
    days = DAYS_TO_DOWNLOAD
    desc = f"Últimos {days} días"
    start = end - timedelta(days=days)
    return start, end, desc


def test_dukascopy_access():
    """Test de acceso a Dukascopy"""
    try:
        print(f"🔍 Testing Dukascopy access...")
        test_end = datetime.now()
        test_start = test_end - timedelta(days=2)
        
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
    """Download data from Dukascopy"""
    print(f"\n📥 Downloading from Dukascopy...")
    print(f"   Pair: {DEFAULT_PAIR}")
    print(f"   From: {start_date.strftime('%Y-%m-%d')}")
    print(f"   To: {end_date.strftime('%Y-%m-%d')}")
    
    try:
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
        
        df = df.reset_index()
        if 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        print(f"\n✅ Download complete: {len(df):,} records")
        return df
        
    except Exception as e:
        print(f"\n❌ Error downloading: {e}")
        return None


def get_google_credentials(credentials_file, token_file, scopes):
    """Get or refresh Google Drive credentials"""
    creds = None
    
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, scopes)
        except:
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
            print(f"\n🌐 Open this URL:\n{auth_url}\n")
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
        
        media = MediaFileUpload(file_path, mimetype='text/csv', resumable=True)
        
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
        
        download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        
        print(f"✅ Upload successful! File ID: {file_id}")
        return file_id, file_url, download_url
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise


def create_forrest_files_fixed(file_id, template_path='Forrest_template_FIXED.py'):
    """
    VERSIÓN ARREGLADA: Crea Forrest.py sin problemas de comillas
    """
    print(f"\n📝 Creating Forrest files from template...")
    
    try:
        # Leer el template
        with open(template_path, 'r', encoding='utf-8') as f:
            template_code = f.read()
        
        # Crear el header SIN USAR COMILLAS TRIPLES
        # Usamos comentarios simples en lugar de docstring
        date_str = datetime.now().strftime('%Y%m%d')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        header_lines = [
            "# ============================================================================",
            "# Forrest Trading ML System - Auto-generated",
            f"# Generated: {timestamp}",
            f"# Drive File ID: {file_id}",
            "# Data Source: Dukascopy",
            "# ============================================================================",
            "",
            "import os",
            "",
            "# CONFIGURACIÓN AUTOMÁTICA DEL FILE_ID",
            f"DRIVE_FILE_ID = '{file_id}'",
            "os.environ['DRIVE_FILE_ID'] = DRIVE_FILE_ID",
            "",
            'print(f"✅ Using Drive File ID: {DRIVE_FILE_ID}")',
            'print("📊 Data Source: Dukascopy (High Quality Forex Data)")',
            "",
            "# ============================================================================",
            "# CÓDIGO DEL TEMPLATE",
            "# ============================================================================",
            ""
        ]
        
        header = '\n'.join(header_lines)
        
        # Combinar header + template
        full_code = header + '\n' + template_code
        
        # Crear archivos con fecha
        output_py = f'Forrest_{date_str}.py'
        output_ipynb = f'Forrest_{date_str}.ipynb'
        
        # 1. Crear archivo .py
        with open(output_py, 'w', encoding='utf-8') as f:
            f.write(full_code)
        
        print(f"✅ Created: {output_py}")
        
        # 2. Crear notebook .ipynb
        notebook = {
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": full_code.split('\n')
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.11.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        with open(output_ipynb, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        print(f"✅ Created: {output_ipynb}")
        
        # Copiar también como Forrest.py y Forrest.ipynb (sin fecha)
        shutil.copy(output_py, 'Forrest.py')
        shutil.copy(output_ipynb, 'Forrest.ipynb')
        print(f"✅ Also created: Forrest.py and Forrest.ipynb (aliases)")
        
        return output_py, output_ipynb
        
    except Exception as e:
        print(f"❌ Error creating Forrest files: {e}")
        raise


def push_to_github(files, commit_message):
    """Push multiple files to GitHub"""
    print(f"\n🔄 Pushing {len(files)} files to GitHub...")
    
    try:
        # Configurar git
        subprocess.run(['git', 'config', '--global', 'user.email', f'{GITHUB_USERNAME}@users.noreply.github.com'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', GITHUB_USERNAME], check=True)
        
        # Sync
        print("🔄 Syncing with remote...")
        repo_url = f'https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git'
        
        try:
            subprocess.run(['git', 'pull', repo_url, 'main', '--rebase'], check=True)
        except:
            subprocess.run(['git', 'pull', repo_url, 'main', '--no-rebase'], check=True)
        
        # Add all files
        for file_path in files:
            subprocess.run(['git', 'add', file_path], check=True)
            print(f"  ✅ Added: {file_path}")
        
        # Commit
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push
        subprocess.run(['git', 'push', repo_url, 'main'], check=True)
        
        print(f"✅ Pushed to GitHub: {GITHUB_USERNAME}/{GITHUB_REPO}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False


def push_to_kaggle(notebook_file):
    """Push notebook to Kaggle using Python API"""
    print(f"\n🚀 Pushing {notebook_file} to Kaggle...")
    
    try:
        # Import Kaggle API
        from kaggle import api
        
        # Authenticate
        api.authenticate()
        print("✅ Kaggle API authenticated")
        
        # Preparar metadata del kernel
        date_str = datetime.now().strftime('%Y%m%d')
        kernel_slug = f"{KAGGLE_USERNAME}/{KAGGLE_KERNEL_SLUG}-{date_str}"
        
        # Crear directorio temporal
        kernel_dir = f'/tmp/kaggle_kernel_{date_str}'
        os.makedirs(kernel_dir, exist_ok=True)
        
        # Copiar notebook
        notebook_dest = os.path.join(kernel_dir, 'Forrest.ipynb')
        shutil.copy(notebook_file, notebook_dest)
        print(f"✅ Notebook copied to {kernel_dir}")
        
        # Crear metadata
        kernel_metadata = {
            "id": kernel_slug,
            "title": f"Forrest Trading ML - Dukascopy {date_str}",
            "code_file": "Forrest.ipynb",
            "language": "python",
            "kernel_type": "notebook",
            "is_private": True,
            "enable_gpu": False,
            "enable_internet": True,
            "dataset_sources": [],
            "competition_sources": [],
            "kernel_sources": []
        }
        
        metadata_path = os.path.join(kernel_dir, 'kernel-metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(kernel_metadata, f, indent=2)
        print("✅ Metadata created")
        
        # Push usando la API
        print("🔄 Pushing to Kaggle...")
        
        try:
            result = api.kernels_push(kernel_dir)
            print("✅ Pushed to Kaggle!")
            print(f"   Kernel: https://www.kaggle.com/{kernel_slug}")
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if 'conflict' in error_msg or '409' in error_msg:
                print("⚠️  Kernel already exists, updating...")
                result = api.kernels_push(kernel_dir)
                print("✅ Kernel updated!")
                return True
            else:
                print(f"❌ Push failed: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🚀 Dukascopy Data Downloader with Kaggle Integration V3 - FIXED")
    print("="*80)
    print(f"📅 Today: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"💱 Forex Pair: {DEFAULT_PAIR}")
    print(f"📊 Data Source: Dukascopy")
    print("="*80)
    
    # Test Dukascopy
    access_ok, access_msg = test_dukascopy_access()
    print(f"   {access_msg}")
    
    if not access_ok:
        print("\n❌ Cannot access Dukascopy!")
        return
    
    # Calculate date range
    start_date, end_date, date_desc = calculate_optimal_date_range()
    print(f"\n📅 Date range: {date_desc}")
    
    # Output filename
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = f"{DEFAULT_PAIR.lower()}_1min_dukascopy_{date_str}.csv"
    
    # Download data
    df = download_dukascopy_data(INSTRUMENT, start_date, end_date, OFFER_SIDE)
    
    if df is None or df.empty:
        print("\n❌ No data downloaded")
        return
    
    # Save CSV
    print(f"\n💾 Saving data to {output_file}...")
    df.to_csv(output_file, index=False)
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"✅ File saved: {len(df):,} rows ({file_size_mb:.2f} MB)")
    
    # Upload to Drive
    try:
        creds = get_google_credentials(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        file_id, file_url, download_url = upload_to_drive(output_file, creds, make_public=True)
        
        print("\n" + "="*80)
        print("✅ File uploaded to Google Drive")
        print(f"🆔 Drive ID: {file_id}")
        print("="*80)
        
        # Create Forrest files (VERSIÓN ARREGLADA)
        forrest_py, forrest_ipynb = create_forrest_files_fixed(file_id, 'Forrest_template_FIXED.py')
        
        # Push to GitHub (both files with date + aliases)
        files_to_push = [forrest_py, forrest_ipynb, 'Forrest.py', 'Forrest.ipynb']
        commit_msg = f"Update Forrest files with Dukascopy data (file_id: {file_id}) - {date_str}"
        push_to_github(files_to_push, commit_msg)
        
        # Push to Kaggle (notebook)
        push_to_kaggle(forrest_ipynb)
        
        print("\n" + "="*80)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("📊 Dukascopy data uploaded to Google Drive")
        print("📝 Forrest files created (SIN ERRORES DE COMILLAS)")
        print("📦 Pushed to GitHub with date in filename")
        print("🚀 Notebook deployed to Kaggle")
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
