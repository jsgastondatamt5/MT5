"""
Polygon Data Downloader with Rate Limiting & Error Handling
Automatically detects if forex data is available, falls back to stock data if needed
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time
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

# Date range (smaller range for testing)
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 10, 31)  # Just January for now

# Symbol options - script will try forex first, then fall back to stocks
FOREX_SYMBOL = "C:EURUSD"
STOCK_SYMBOL = "AAPL"  # Apple stock as fallback

# Rate limiting
REQUESTS_PER_MINUTE = 5
DELAY_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE  # 12 seconds

# Google OAuth
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = 'token.json'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_api_access(symbol, api_key):
    """
    Check if the API key has access to the specified symbol
    
    Returns:
        tuple: (bool: has_access, str: message)
    """
    test_date = datetime(2024, 1, 2).strftime("%Y-%m-%d")
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
    """
    Download historical data with automatic rate limiting
    """
    print(f"\n📥 Downloading {symbol} data from {start_date.date()} to {end_date.date()}...")
    print(f"⏱️  Rate limit: {REQUESTS_PER_MINUTE} requests/minute ({delay:.1f}s between requests)")
    
    data = []
    current_date = start_date
    total_days = (end_date - start_date).days
    day_count = 0
    success_count = 0
    error_count = 0
    
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
                if day_count % 5 == 0:
                    print(f"   Progress: {day_count}/{total_days} days | {len(data)} records | ✓ {success_count} ✗ {error_count}")
            
            elif response.status_code == 403:
                print(f"\n❌ Access denied for {symbol}!")
                print("   Your API plan doesn't include this data type.")
                return None
            
            elif response.status_code == 429:
                print(f"\n⚠️  Rate limit hit on {date_str}. Waiting 60 seconds...")
                time.sleep(60)
                continue  # Retry this date
            
            else:
                error_count += 1
                if error_count <= 3:  # Only show first few errors
                    print(f"   ⚠️  Error {response.status_code} for {date_str}")
        
        except requests.exceptions.RequestException as e:
            error_count += 1
            if error_count <= 3:
                print(f"   ⚠️  Connection error for {date_str}: {e}")
        
        current_date += timedelta(days=1)
        
        # Rate limiting delay
        if current_date < end_date:
            time.sleep(delay)
    
    print(f"\n✅ Download complete:")
    print(f"   Total records: {len(data)}")
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


def upload_to_drive(file_path, credentials):
    """Upload file to Google Drive"""
    print(f"\n☁️  Uploading {os.path.basename(file_path)} to Google Drive...")
    
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    return file.get('id')


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🚀 Polygon Data Downloader & Google Drive Uploader")
    print("="*80)
    
    # Step 1: Check API access
    print("\n🔍 Checking API access...")
    
    forex_access, forex_msg = check_api_access(FOREX_SYMBOL, API_KEY)
    print(f"   Forex ({FOREX_SYMBOL}): {forex_msg}")
    
    stock_access, stock_msg = check_api_access(STOCK_SYMBOL, API_KEY)
    print(f"   Stock ({STOCK_SYMBOL}): {stock_msg}")
    
    # Determine which symbol to use
    if forex_access:
        symbol = FOREX_SYMBOL
        output_file = "eurusd_1min.csv"
        print(f"\n✅ Using forex data: {symbol}")
    elif stock_access:
        symbol = STOCK_SYMBOL
        output_file = "stock_data_1min.csv"
        print(f"\n⚠️  Forex not available. Using stock data: {symbol}")
        print(f"   Note: Upgrade your Polygon plan to access forex data")
    else:
        print("\n❌ ERROR: No data access available!")
        print("\nPossible solutions:")
        print("   1. Check your API key is correct")
        print("   2. Verify your Polygon subscription plan")
        print("   3. Wait a few minutes if rate limited")
        return
    
    # Step 2: Download data
    df = download_data_with_rate_limit(
        symbol, 
        START_DATE, 
        END_DATE, 
        API_KEY, 
        DELAY_BETWEEN_REQUESTS
    )
    
    if df is None or df.empty:
        print("\n❌ No data downloaded. Exiting.")
        return
    
    # Step 3: Save to CSV
    print(f"\n💾 Saving data to {output_file}...")
    df.to_csv(output_file, index=False)
    print(f"✅ File saved: {len(df):,} rows")
    
    # Step 4: Upload to Google Drive
    try:
        creds = get_google_credentials(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        file_id = upload_to_drive(output_file, creds)
        
        print("\n" + "="*80)
        print("✅ SUCCESS! File uploaded to Google Drive")
        print("="*80)
        print(f"📄 File: {output_file}")
        print(f"📊 Records: {len(df):,}")
        print(f"🆔 Drive ID: {file_id}")
        print(f"🔗 View: https://drive.google.com/file/d/{file_id}/view")
        print("="*80 + "\n")
    
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
