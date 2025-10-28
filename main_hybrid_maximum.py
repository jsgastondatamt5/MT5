"""
HYBRID Data Downloader - Maximum EURUSD Data
Combines Polygon API + Yahoo Finance for maximum data coverage
- Polygon: 1min data if available
- Yahoo Finance: Multi-interval fallback (1m, 5m, 1h)
- Auto-uploads to Google Drive
- Kaggle integration
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

# Install yfinance if needed
try:
    import yfinance as yf
    print("✅ yfinance loaded")
except ImportError:
    print("📦 Installing yfinance...")
    import subprocess
    subprocess.check_call(['pip', 'install', '-q', 'yfinance', '--break-system-packages'])
    import yfinance as yf

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# API Keys
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', 'xDz4sl2a8Xht_z0TH8_svpSB309X17kv')
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

# Symbols
POLYGON_FOREX = "C:EURUSD"
YAHOO_FOREX = "EURUSD=X"
FALLBACK_STOCK = "AAPL"

# Date ranges - AUTOMÁTICO desde HOY
END_DATE = datetime.now()

# Yahoo Finance limits por intervalo
YAHOO_LIMITS = {
    '1m': 7,      # 7 días
    '5m': 60,     # 60 días
    '15m': 60,    # 60 días
    '1h': 730,    # 2 años
    '1d': 3650    # 10 años
}

# Rate limiting for Polygon
REQUESTS_PER_MINUTE = 5
DELAY_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE

# Google OAuth
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = 'token.json'
NOTIFICATION_FILE = 'drive_file_info.json'

# ============================================================================
# POLYGON FUNCTIONS
# ============================================================================

def check_polygon_access(api_key):
    """Check if Polygon API has forex access"""
    test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://api.polygon.io/v2/aggs/ticker/{POLYGON_FOREX}/range/1/minute/{test_date}/{test_date}?adjusted=true&sort=asc&limit=5&apiKey={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("resultsCount", 0) > 0:
                return True, "✅ Polygon forex access confirmed"
        elif response.status_code == 403:
            return False, "❌ No forex access (upgrade plan needed)"
        elif response.status_code == 429:
            return False, "⚠️  Rate limited"
        return False, f"❌ Error {response.status_code}"
    except Exception as e:
        return False, f"❌ Connection error: {e}"


def download_polygon_data(symbol, start_date, end_date, api_key, delay=12):
    """Download data from Polygon with rate limiting"""
    print(f"\n📥 Downloading from Polygon API...")
    print(f"   Symbol: {symbol}")
    print(f"   Range: {start_date.date()} to {end_date.date()}")
    
    data = []
    current_date = start_date
    total_days = (end_date - start_date).days
    
    while current_date < end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date_str}/{date_str}?adjusted=true&sort=asc&limit=50000&apiKey={api_key}"
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                for item in results:
                    data.append({
                        "timestamp": datetime.fromtimestamp(item["t"] / 1000),
                        "open": item["o"],
                        "high": item["h"],
                        "low": item["l"],
                        "close": item["c"],
                        "volume": item["v"],
                        "source": "polygon",
                        "interval": "1m"
                    })
            elif response.status_code == 403:
                print(f"   ❌ Access denied - stopping Polygon download")
                break
            elif response.status_code == 429:
                print(f"   ⚠️  Rate limit - waiting...")
                time.sleep(60)
                continue
        
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
        
        current_date += timedelta(days=1)
        if current_date < end_date:
            time.sleep(delay)
    
    print(f"   ✅ Polygon: {len(data):,} records")
    return pd.DataFrame(data) if data else pd.DataFrame()


# ============================================================================
# YAHOO FINANCE FUNCTIONS
# ============================================================================

def download_yahoo_interval(pair, interval, days_back):
    """
    Download data from Yahoo Finance for specific interval
    
    Args:
        pair: Forex pair (e.g., "EURUSD=X")
        interval: Time interval (1m, 5m, 15m, 1h, 1d)
        days_back: Days to go back from today
    
    Returns:
        DataFrame with data
    """
    end = datetime.now()
    start = end - timedelta(days=days_back)
    
    print(f"\n📥 Downloading from Yahoo Finance...")
    print(f"   Pair: {pair}")
    print(f"   Interval: {interval}")
    print(f"   Range: {start.date()} to {end.date()} ({days_back} days)")
    
    try:
        df = yf.download(
            pair,
            start=start.strftime('%Y-%m-%d'),
            end=end.strftime('%Y-%m-%d'),
            interval=interval,
            progress=False
        )
        
        if df.empty:
            print(f"   ⚠️  No data for {interval}")
            return pd.DataFrame()
        
        # Rename columns
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Reset index
        df = df.reset_index()
        df = df.rename(columns={'Datetime': 'timestamp', 'Date': 'timestamp'})
        
        # Add metadata
        df['source'] = 'yahoo'
        df['interval'] = interval
        
        print(f"   ✅ Yahoo ({interval}): {len(df):,} records")
        print(f"      From {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        return df
    
    except Exception as e:
        print(f"   ❌ Error downloading {interval}: {e}")
        return pd.DataFrame()


def download_yahoo_multi_interval(pair):
    """
    Download maximum data from Yahoo Finance using multiple intervals
    Combines 1m, 5m, 1h data for comprehensive coverage
    """
    print("\n" + "="*80)
    print("📊 Yahoo Finance Multi-Interval Download")
    print("="*80)
    
    all_data = []
    
    # Strategy: Download different intervals for maximum coverage
    intervals_to_try = [
        ('1m', 7),      # 1-min for last 7 days (most granular recent data)
        ('5m', 60),     # 5-min for last 60 days
        ('1h', 730),    # 1-hour for last 2 years (maximum historical)
    ]
    
    for interval, days in intervals_to_try:
        df = download_yahoo_interval(pair, interval, days)
        if not df.empty:
            all_data.append(df)
    
    if not all_data:
        print("\n❌ No data downloaded from Yahoo Finance")
        return pd.DataFrame()
    
    # Combine all dataframes
    print(f"\n🔄 Combining data from {len(all_data)} intervals...")
    combined = pd.concat(all_data, ignore_index=True)
    
    # Remove duplicates (keep most granular)
    # Sort by timestamp and interval priority (1m > 5m > 1h)
    interval_priority = {'1m': 1, '5m': 2, '15m': 3, '1h': 4, '1d': 5}
    combined['interval_priority'] = combined['interval'].map(interval_priority)
    
    combined = combined.sort_values(['timestamp', 'interval_priority'])
    combined = combined.drop_duplicates(subset=['timestamp'], keep='first')
    combined = combined.drop('interval_priority', axis=1)
    
    # Sort by timestamp
    combined = combined.sort_values('timestamp').reset_index(drop=True)
    
    print(f"✅ Combined dataset: {len(combined):,} unique records")
    print(f"   Date range: {combined['timestamp'].min()} to {combined['timestamp'].max()}")
    
    return combined


# ============================================================================
# GOOGLE DRIVE FUNCTIONS
# ============================================================================

def make_file_public(file_id, credentials):
    """Make Drive file publicly accessible"""
    service = build('drive', 'v3', credentials=credentials)
    try:
        permission = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(fileId=file_id, body=permission).execute()
        print(f"   🌍 File is now public")
        return True
    except Exception as e:
        print(f"   ⚠️  Could not make public: {e}")
        return False


def get_google_credentials(credentials_file, token_file, scopes):
    """Get Google Drive credentials"""
    creds = None
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
        print("🔓 Existing token found")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing token...")
            creds.refresh(Request())
        else:
            print("\n🔐 Google Drive authorization...")
            flow = Flow.from_client_secrets_file(
                credentials_file, scopes=scopes, redirect_uri='http://localhost:8080'
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            print("\n" + "="*80)
            print("🔗 Open this link:")
            print("="*80)
            print(auth_url)
            print("="*80)
            print("\n🔑 Paste authorization code:")
            code = input(">>> ").strip()
            
            if not code:
                raise ValueError("No code provided")
            
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            print("✅ Authorized!")
    
    return creds


def upload_to_drive(file_path, credentials):
    """Upload to Drive and make public"""
    print(f"\n☁️  Uploading to Google Drive...")
    
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    file_id = file.get('id')
    web_link = file.get('webViewLink')
    download_url = f"https://drive.google.com/uc?id={file_id}"
    
    # Make public
    make_file_public(file_id, credentials)
    
    return file_id, web_link, download_url


def save_file_info(file_id, file_url, download_url, metadata):
    """Save file info for Kaggle"""
    info = {
        "drive_file_id": file_id,
        "drive_file_url": file_url,
        "download_url": download_url,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata
    }
    
    with open(NOTIFICATION_FILE, 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"💾 File info saved: {NOTIFICATION_FILE}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🚀 HYBRID EURUSD Downloader - Maximum Data")
    print("="*80)
    print("Strategy: Polygon (if available) + Yahoo Finance Multi-Interval")
    print("="*80)
    
    all_dataframes = []
    data_sources = []
    
    # ========================================================================
    # PHASE 1: Try Polygon (1-minute data if forex access available)
    # ========================================================================
    
    print("\n" + "="*80)
    print("PHASE 1: Polygon API")
    print("="*80)
    
    polygon_access, polygon_msg = check_polygon_access(POLYGON_API_KEY)
    print(f"Status: {polygon_msg}")
    
    if polygon_access:
        # Download last 30 days from Polygon (conservative for free tier)
        start_date = END_DATE - timedelta(days=30)
        
        print(f"\n💡 Downloading 30 days of 1-minute data from Polygon...")
        polygon_df = download_polygon_data(
            POLYGON_FOREX,
            start_date,
            END_DATE,
            POLYGON_API_KEY,
            DELAY_BETWEEN_REQUESTS
        )
        
        if not polygon_df.empty:
            all_dataframes.append(polygon_df)
            data_sources.append(f"Polygon: {len(polygon_df):,} records (1m)")
    else:
        print("⚠️  Skipping Polygon (no forex access)")
    
    # ========================================================================
    # PHASE 2: Yahoo Finance (multi-interval for maximum coverage)
    # ========================================================================
    
    print("\n" + "="*80)
    print("PHASE 2: Yahoo Finance Multi-Interval")
    print("="*80)
    
    yahoo_df = download_yahoo_multi_interval(YAHOO_FOREX)
    
    if not yahoo_df.empty:
        all_dataframes.append(yahoo_df)
        
        # Count by interval
        for interval in yahoo_df['interval'].unique():
            count = len(yahoo_df[yahoo_df['interval'] == interval])
            data_sources.append(f"Yahoo {interval}: {count:,} records")
    
    # ========================================================================
    # PHASE 3: Combine and Save
    # ========================================================================
    
    if not all_dataframes:
        print("\n❌ No data downloaded from any source!")
        return
    
    print("\n" + "="*80)
    print("PHASE 3: Combining Data")
    print("="*80)
    
    # Combine all sources
    final_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Remove duplicates (keep most granular)
    print(f"   Before dedup: {len(final_df):,} records")
    
    interval_priority = {'1m': 1, '5m': 2, '15m': 3, '1h': 4, '1d': 5}
    final_df['interval_priority'] = final_df['interval'].map(interval_priority)
    final_df = final_df.sort_values(['timestamp', 'interval_priority'])
    final_df = final_df.drop_duplicates(subset=['timestamp'], keep='first')
    final_df = final_df.drop('interval_priority', axis=1)
    final_df = final_df.sort_values('timestamp').reset_index(drop=True)
    
    print(f"   After dedup: {len(final_df):,} unique records")
    
    # Generate output filename
    output_file = f"eurusd_hybrid_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # Save to CSV
    print(f"\n💾 Saving to {output_file}...")
    final_df.to_csv(output_file, index=False)
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    
    # Display summary
    print("\n" + "="*80)
    print("📊 DOWNLOAD SUMMARY")
    print("="*80)
    print(f"Total records: {len(final_df):,}")
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"Date range: {final_df['timestamp'].min()} to {final_df['timestamp'].max()}")
    print(f"Time span: {(final_df['timestamp'].max() - final_df['timestamp'].min()).days} days")
    print(f"\nData sources:")
    for source in data_sources:
        print(f"  • {source}")
    
    # Interval breakdown
    print(f"\nInterval breakdown:")
    interval_counts = final_df.groupby('interval').size()
    for interval, count in interval_counts.items():
        print(f"  • {interval}: {count:,} records")
    
    # Source breakdown
    print(f"\nSource breakdown:")
    source_counts = final_df.groupby('source').size()
    for source, count in source_counts.items():
        print(f"  • {source}: {count:,} records")
    
    print("="*80)
    
    # ========================================================================
    # PHASE 4: Upload to Google Drive
    # ========================================================================
    
    print("\n" + "="*80)
    print("PHASE 4: Google Drive Upload")
    print("="*80)
    
    try:
        creds = get_google_credentials(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        file_id, file_url, download_url = upload_to_drive(output_file, creds)
        
        print("\n✅ SUCCESS! File uploaded")
        print(f"📄 File: {output_file}")
        print(f"🆔 Drive ID: {file_id}")
        print(f"🔗 View: {file_url}")
        print(f"📥 Download: {download_url}")
        
        # Save metadata for Kaggle
        metadata = {
            "symbol": "EURUSD",
            "total_records": len(final_df),
            "file_size_mb": round(file_size_mb, 2),
            "date_range": {
                "start": final_df['timestamp'].min().isoformat(),
                "end": final_df['timestamp'].max().isoformat(),
                "days": (final_df['timestamp'].max() - final_df['timestamp'].min()).days
            },
            "sources": data_sources,
            "intervals": interval_counts.to_dict(),
            "generated_at": datetime.now().isoformat()
        }
        
        save_file_info(file_id, file_url, download_url, metadata)
        
        print("\n💡 For Kaggle:")
        print(f"   1. Upload '{NOTIFICATION_FILE}' as dataset")
        print(f"   2. Or set DRIVE_FILE_ID = '{file_id}'")
        print(f"   3. File is public - gdown will work directly")
        
    except Exception as e:
        print(f"\n❌ Upload error: {e}")
        print(f"   Data saved locally: {output_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
