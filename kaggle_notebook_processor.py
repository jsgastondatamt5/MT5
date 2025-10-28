# Kaggle Notebook: Process Data from Google Drive
# Este notebook lee el file ID de Google Drive y procesa los datos

"""
Cómo usar este notebook en Kaggle:

Opción 1: Leer desde variable de entorno
  - En Kaggle: Add-ons → Environment Variables
  - Agregar: DRIVE_FILE_ID = tu_file_id

Opción 2: Leer desde archivo JSON
  - Subir drive_file_info.json como dataset
  - El notebook lo leerá automáticamente

Opción 3: Hardcodear el file ID (no recomendado para producción)
  - Copiar file ID directamente en el código
"""

import pandas as pd
import json
import os
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Método 1: Desde variable de entorno (recomendado)
DRIVE_FILE_ID = os.getenv('DRIVE_FILE_ID', None)

# Método 2: Desde archivo JSON subido como dataset
FILE_INFO_PATH = '/kaggle/input/drive-file-info/drive_file_info.json'

# Método 3: Hardcoded (solo para testing)
# DRIVE_FILE_ID = 'tu_file_id_aqui'

# ============================================================================
# FUNCIONES
# ============================================================================

def get_file_id_from_json(json_path):
    """Lee el file ID desde archivo JSON"""
    if os.path.exists(json_path):
        print(f"📄 Reading file info from: {json_path}")
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data.get('drive_file_id'), data.get('metadata', {})
    return None, None


def download_from_drive_gdown(file_id, output_path='data.csv'):
    """
    Descarga archivo desde Google Drive usando gdown
    
    Args:
        file_id: Google Drive file ID
        output_path: Path donde guardar el archivo
    
    Returns:
        Path to downloaded file
    """
    import gdown
    
    print(f"📥 Downloading from Google Drive...")
    print(f"   File ID: {file_id}")
    
    # Construir URL de descarga
    url = f'https://drive.google.com/uc?id={file_id}'
    
    try:
        # Descargar archivo
        gdown.download(url, output_path, quiet=False)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Download complete: {output_path} ({file_size:.2f} MB)")
            return output_path
        else:
            print("❌ Download failed")
            return None
    
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return None


def download_from_drive_pydrive(file_id, output_path='data.csv', credentials_json=None):
    """
    Descarga archivo desde Google Drive usando PyDrive
    Requiere autenticación OAuth
    
    Args:
        file_id: Google Drive file ID
        output_path: Path donde guardar el archivo
        credentials_json: Path to credentials.json (optional)
    """
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    
    print(f"📥 Downloading from Google Drive with PyDrive...")
    
    # Authenticate
    gauth = GoogleAuth()
    
    if credentials_json and os.path.exists(credentials_json):
        gauth.LoadCredentialsFile(credentials_json)
    
    if gauth.credentials is None:
        # Si no hay credenciales, hacer OAuth flow
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh si expiró
        gauth.Refresh()
    else:
        # Ya autenticado
        gauth.Authorize()
    
    # Guardar credenciales para próxima vez
    gauth.SaveCredentialsFile("credentials.txt")
    
    # Create Drive instance
    drive = GoogleDrive(gauth)
    
    try:
        # Download file
        file = drive.CreateFile({'id': file_id})
        file.GetContentFile(output_path)
        
        print(f"✅ Download complete: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return None


def make_file_public_shareable(file_id):
    """
    Función auxiliar: hace que un archivo sea públicamente accesible
    Esto debe ejecutarse en el script de UPLOAD, no en Kaggle
    """
    from googleapiclient.discovery import build
    
    service = build('drive', 'v3', credentials=credentials)
    
    try:
        # Hacer el archivo público
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()
        
        print(f"✅ File {file_id} is now publicly accessible")
        return True
    
    except Exception as e:
        print(f"❌ Error making file public: {e}")
        return False


# ============================================================================
# PROCESAMIENTO DE DATOS
# ============================================================================

def analyze_trading_data(df):
    """
    Análisis básico de datos de trading
    
    Args:
        df: DataFrame con columnas: timestamp, open, high, low, close, volume
    """
    print("\n" + "="*80)
    print("📊 DATA ANALYSIS")
    print("="*80)
    
    # Info básica
    print(f"\n📈 Dataset Info:")
    print(f"   Rows: {len(df):,}")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Estadísticas de precios
    print(f"\n💰 Price Statistics:")
    print(f"   Open: ${df['open'].mean():.4f} (avg), ${df['open'].min():.4f} - ${df['open'].max():.4f}")
    print(f"   Close: ${df['close'].mean():.4f} (avg), ${df['close'].min():.4f} - ${df['close'].max():.4f}")
    print(f"   High: ${df['high'].max():.4f}")
    print(f"   Low: ${df['low'].min():.4f}")
    
    # Volatilidad
    df['daily_return'] = df['close'].pct_change()
    print(f"\n📉 Volatility:")
    print(f"   Daily return (mean): {df['daily_return'].mean()*100:.4f}%")
    print(f"   Daily return (std): {df['daily_return'].std()*100:.4f}%")
    
    # Volumen
    print(f"\n📊 Volume:")
    print(f"   Average: {df['volume'].mean():,.0f}")
    print(f"   Max: {df['volume'].max():,.0f}")
    
    # Missing data
    print(f"\n🔍 Data Quality:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("   ✅ No missing values")
    else:
        print(f"   ⚠️  Missing values found:")
        print(missing[missing > 0])
    
    return df


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🔬 Kaggle Data Processor - Google Drive Integration")
    print("="*80)
    
    # Step 1: Obtener file ID
    file_id = None
    metadata = {}
    
    # Intentar Método 1: Variable de entorno
    if DRIVE_FILE_ID:
        file_id = DRIVE_FILE_ID
        print(f"✅ File ID found in environment variable")
        print(f"   ID: {file_id}")
    
    # Intentar Método 2: Archivo JSON
    elif os.path.exists(FILE_INFO_PATH):
        file_id, metadata = get_file_id_from_json(FILE_INFO_PATH)
        if file_id:
            print(f"✅ File ID found in JSON file")
            print(f"   ID: {file_id}")
            print(f"   Metadata: {metadata}")
    
    if not file_id:
        print("\n❌ ERROR: No file ID found!")
        print("\nPlease provide file ID using one of these methods:")
        print("   1. Set DRIVE_FILE_ID environment variable")
        print("   2. Upload drive_file_info.json as dataset")
        print("   3. Hardcode file_id in the script (not recommended)")
        return
    
    # Step 2: Descargar datos desde Drive
    print("\n" + "="*80)
    print("📥 DOWNLOADING DATA")
    print("="*80)
    
    # Instalar gdown si no está disponible
    try:
        import gdown
    except ImportError:
        print("📦 Installing gdown...")
        import subprocess
        subprocess.check_call(['pip', 'install', '-q', 'gdown'])
        import gdown
    
    # Descargar archivo
    local_file = download_from_drive_gdown(file_id, 'trading_data.csv')
    
    if not local_file:
        print("\n❌ Failed to download file from Drive")
        print("\nTroubleshooting:")
        print("   1. Make sure the file is publicly accessible")
        print("   2. Verify the file ID is correct")
        print("   3. Check if the file still exists in Drive")
        return
    
    # Step 3: Cargar y procesar datos
    print("\n" + "="*80)
    print("🔄 LOADING DATA")
    print("="*80)
    
    try:
        df = pd.read_csv(local_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(f"✅ Data loaded successfully")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        # Análisis de datos
        df = analyze_trading_data(df)
        
        # Step 4: Aquí puedes agregar tu análisis/modelo
        print("\n" + "="*80)
        print("🤖 YOUR CUSTOM ANALYSIS HERE")
        print("="*80)
        print("   Add your trading strategy, ML model, or analysis below:")
        print()
        
        # Ejemplo: Calcular medias móviles
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        print("   ✅ Calculated SMA 20 and SMA 50")
        
        # Ejemplo: Detectar cruces
        df['signal'] = 0
        df.loc[df['sma_20'] > df['sma_50'], 'signal'] = 1
        df.loc[df['sma_20'] < df['sma_50'], 'signal'] = -1
        
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        print(f"   📈 Buy signals: {buy_signals}")
        print(f"   📉 Sell signals: {sell_signals}")
        
        # Step 5: Guardar resultados
        output_file = 'analysis_results.csv'
        df.to_csv(output_file, index=False)
        
        print(f"\n✅ Analysis complete! Results saved to: {output_file}")
        
        return df
    
    except Exception as e:
        print(f"\n❌ Error processing data: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Ejecutar análisis
    df = main()
    
    # El DataFrame 'df' ahora está disponible para análisis adicional
    if df is not None:
        print("\n" + "="*80)
        print("✅ Ready for further analysis!")
        print("="*80)
        print("\nDataFrame 'df' is now available with columns:")
        print(f"   {list(df.columns)}")
        print("\nYou can now:")
        print("   - Build ML models")
        print("   - Backtest trading strategies")
        print("   - Create visualizations")
        print("   - Export results")
