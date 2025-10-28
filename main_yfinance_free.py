"""
FREE Forex Data Downloader using Yahoo Finance
No API key required - downloads EURUSD data and uploads to Google Drive
"""
pip install yfinance

import pandas as pd
from datetime import datetime, timedelta
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ============================================================================
# INSTALL REQUIRED PACKAGE
# ============================================================================
# Run: pip install yfinance --break-system-packages
# Or add to requirements.txt: yfinance>=0.2.0

try:
    import yfinance as yf
    print("✅ yfinance loaded successfully")
except ImportError:
    print("❌ yfinance not installed!")
    print("   Run: pip install yfinance")
    print("   Or: pip install yfinance --break-system-packages")
    exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Date range
START_DATE = "2023-01-01"
END_DATE = "2023-10-02"

# Forex pair (Yahoo Finance format)
FOREX_PAIR = "EURUSD=X"  # Other options: GBPUSD=X, USDJPY=X, AUDUSD=X

# Output filename
OUTPUT_FILE = "eurusd_yfinance_1min.csv"

# Google OAuth
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def download_forex_data(pair, start_date, end_date):
    """
    Download forex data from Yahoo Finance
    
    Args:
        pair: Forex pair in Yahoo format (e.g., "EURUSD=X")
        start_date: Start date string "YYYY-MM-DD"
        end_date: End date string "YYYY-MM-DD"
    
    Returns:
        pandas.DataFrame with OHLCV data
    """
    print(f"\n📥 Downloading {pair} data from {start_date} to {end_date}...")
    print("   Source: Yahoo Finance (FREE)")
    print("   ⏱️  This may take a few minutes for large date ranges...")
    
    try:
        # Download data
        # Note: Yahoo Finance 1-minute data is limited to last 7 days
        # For historical data, we can only get daily/hourly
        
        # Try 1-minute first (will only work for recent data)
        df = yf.download(
            pair, 
            start=start_date, 
            end=end_date, 
            interval="1m",  # Try 1-minute
            progress=True
        )
        
        if df.empty:
            print("\n⚠️  1-minute data not available for this date range")
            print("   Yahoo Finance only provides 1-minute data for the last 7 days")
            print("   Downloading hourly data instead...")
            
            # Fall back to hourly
            df = yf.download(
                pair, 
                start=start_date, 
                end=end_date, 
                interval="1h",
                progress=True
            )
        
        if df.empty:
            print("\n❌ No data received from Yahoo Finance")
            return None
        
        # Rename columns to match expected format
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Reset index to make timestamp a column
        df = df.reset_index()
        df = df.rename(columns={'Datetime': 'timestamp', 'Date': 'timestamp'})
        
        print(f"\n✅ Downloaded {len(df):,} records")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        return df
    
    except Exception as e:
        print(f"\n❌ Error downloading data: {e}")
        return None


def get_google_credentials(credentials_file, token_file, scopes):
    """Get Google Drive credentials"""
    creds = None
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
        print("🔓 Using existing authorization token")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("\n🔐 Starting Google Drive authorization...")
            
            if not os.path.exists(credentials_file):
                print(f"❌ Credentials file not found: {credentials_file}")
                print("   Download it from Google Cloud Console")
                return None
            
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
                print("❌ No code provided")
                return None
            
            try:
                flow.fetch_token(code=code)
                creds = flow.credentials
                
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
                
                print("✅ Authorization successful!")
            except Exception as e:
                print(f"❌ Authorization failed: {e}")
                return None
    
    return creds


def upload_to_drive(file_path, credentials):
    """Upload file to Google Drive"""
    print(f"\n☁️  Uploading {os.path.basename(file_path)} to Google Drive...")
    
    try:
        service = build('drive', 'v3', credentials=credentials)
        file_metadata = {'name': os.path.basename(file_path)}
        media = MediaFileUpload(file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🚀 FREE Forex Data Downloader (Yahoo Finance)")
    print("="*80)
    print(f"📊 Pair: {FOREX_PAIR}")
    print(f"📅 Period: {START_DATE} to {END_DATE}")
    print(f"💾 Output: {OUTPUT_FILE}")
    print("="*80)
    
    # Important note about data availability
    print("\n📝 NOTE: Yahoo Finance data limitations:")
    print("   • 1-minute data: Only last 7 days available")
    print("   • Hourly data: Up to 730 days available")
    print("   • Daily data: Unlimited history available")
    print()
    
    # Calculate date range
    start_dt = datetime.strptime(START_DATE, "%Y-%m-%d")
    end_dt = datetime.strptime(END_DATE, "%Y-%m-%d")
    days_diff = (end_dt - start_dt).days
    
    if days_diff > 7:
        print(f"⚠️  Your date range is {days_diff} days")
        print("   1-minute data won't be available")
        print("   Script will automatically use hourly data instead")
        print()
        response = input("Continue? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled")
            return
    
    # Step 1: Download data
    df = download_forex_data(FOREX_PAIR, START_DATE, END_DATE)
    
    if df is None or df.empty:
        print("\n❌ Failed to download data. Exiting.")
        return
    
    # Step 2: Save to CSV
    print(f"\n💾 Saving data to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    file_size = os.path.getsize(OUTPUT_FILE) / 1024  # KB
    print(f"✅ File saved: {len(df):,} rows ({file_size:.1f} KB)")
    
    # Step 3: Upload to Google Drive
    print("\n" + "="*40)
    upload_choice = input("Upload to Google Drive? (y/n): ").strip().lower()
    
    if upload_choice == 'y':
        creds = get_google_credentials(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        
        if creds:
            file_id = upload_to_drive(OUTPUT_FILE, creds)
            
            if file_id:
                print("\n" + "="*80)
                print("✅ SUCCESS! File uploaded to Google Drive")
                print("="*80)
                print(f"📄 File: {OUTPUT_FILE}")
                print(f"📊 Records: {len(df):,}")
                print(f"🆔 Drive ID: {file_id}")
                print(f"🔗 View: https://drive.google.com/file/d/{file_id}/view")
                print("="*80 + "\n")
            else:
                print(f"\n⚠️  Upload failed, but data is saved locally in: {OUTPUT_FILE}")
        else:
            print(f"\n⚠️  Authorization failed, but data is saved locally in: {OUTPUT_FILE}")
    else:
        print(f"\n✅ Data saved locally in: {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Script interrupted by user")
        print(f"   Check if {OUTPUT_FILE} was created")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
Other forex pairs available:
- EURUSD=X  (Euro/US Dollar)
- GBPUSD=X  (British Pound/US Dollar)
- USDJPY=X  (US Dollar/Japanese Yen)
- AUDUSD=X  (Australian Dollar/US Dollar)
- USDCAD=X  (US Dollar/Canadian Dollar)
- USDCHF=X  (US Dollar/Swiss Franc)
- NZDUSD=X  (New Zealand Dollar/US Dollar)

Interval options:
- "1m"   - 1 minute (last 7 days only)
- "5m"   - 5 minutes (last 60 days)
- "15m"  - 15 minutes (last 60 days)
- "1h"   - 1 hour (last 730 days)
- "1d"   - 1 day (unlimited)
"""
