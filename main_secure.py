"""
Secure EURUSD Data Downloader & Google Drive Uploader
Uses environment variables for credentials
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONFIGURATION - SECURE METHOD
# ============================================================================

# Get API key from environment variable
API_KEY = os.getenv('POLYGON_API_KEY')
if not API_KEY:
    print("❌ ERROR: POLYGON_API_KEY not found!")
    print("📝 Please create a .env file with:")
    print("   POLYGON_API_KEY=your_api_key_here")
    print("\n   Or set it as an environment variable:")
    print("   export POLYGON_API_KEY='your_api_key_here'")
    exit(1)

# Get credentials file path
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
if not os.path.exists(CREDENTIALS_FILE):
    print(f"❌ ERROR: Credentials file not found: {CREDENTIALS_FILE}")
    print("📝 Please download your OAuth credentials from Google Cloud Console")
    print("   and save them as credentials.json")
    exit(1)

# ============================================================================
# CONFIGURATION - DATA PARAMETERS
# ============================================================================

# 📅 Date range
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2023, 10, 2)

# 📊 Trading symbol
SYMBOL = "C:EURUSD"

# 📁 Output filename
OUTPUT_FILE = "eurusd_1min.csv"

# 🔐 Google OAuth settings
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = 'token.json'

# ============================================================================
# FUNCTION DEFINITIONS
# ============================================================================

def download_polygon_data(symbol, start_date, end_date, api_key):
    """
    Download historical forex data from Polygon API
    
    Args:
        symbol: Trading symbol (e.g., "C:EURUSD")
        start_date: Start date for data
        end_date: End date for data
        api_key: Polygon API key
    
    Returns:
        pandas.DataFrame with OHLCV data
    """
    print(f"\n📥 Downloading {symbol} data from {start_date.date()} to {end_date.date()}...")
    
    data = []
    current_date = start_date
    total_days = (end_date - start_date).days
    day_count = 0
    
    while current_date < end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        url = (
            f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/"
            f"{date_str}/{date_str}?adjusted=true&sort=asc&limit=50000&apiKey={api_key}"
        )
        
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
                print(f"   Progress: {day_count}/{total_days} days ({len(data)} records)")
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Error downloading data for {date_str}: {e}")
        
        current_date += timedelta(days=1)
    
    print(f"✅ Download complete: {len(data)} records obtained")
    return pd.DataFrame(data)


def get_google_credentials(credentials_file, token_file, scopes):
    """
    Get Google Drive credentials, handling OAuth flow if needed
    
    Args:
        credentials_file: Path to credentials.json
        token_file: Path to token.json
        scopes: List of OAuth scopes
    
    Returns:
        google.oauth2.credentials.Credentials object
    """
    creds = None
    
    # Load existing token if available
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
        print("🔓 Existing authorization token found")
    
    # Refresh or get new credentials
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
            print("\n📝 STEP 2: After authorization, copy the code from the URL")
            print("   Example: http://localhost:8080/?code=YOUR_CODE&scope=...")
            print("\n🔑 STEP 3: Paste the code here:")
            
            code = input(">>> ").strip()
            
            if not code:
                raise ValueError("No authorization code provided")
            
            try:
                flow.fetch_token(code=code)
                creds = flow.credentials
                
                # Save token for future use
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
                
                print(f"✅ Authorization successful! Token saved to {token_file}")
            
            except Exception as e:
                raise Exception(f"Authorization failed: {e}")
    
    return creds


def upload_to_drive(file_path, credentials):
    """
    Upload a file to Google Drive
    
    Args:
        file_path: Path to file to upload
        credentials: Google OAuth credentials
    
    Returns:
        File ID of uploaded file
    """
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
    """Main execution function"""
    
    print("\n" + "="*80)
    print("🚀 EURUSD Data Downloader & Google Drive Uploader")
    print("="*80)
    print(f"📊 Symbol: {SYMBOL}")
    print(f"📅 Period: {START_DATE.date()} to {END_DATE.date()}")
    print(f"💾 Output: {OUTPUT_FILE}")
    print("="*80)
    
    try:
        # Step 1: Download data from Polygon
        df = download_polygon_data(SYMBOL, START_DATE, END_DATE, API_KEY)
        
        if df.empty:
            print("❌ No data downloaded. Exiting.")
            return
        
        # Step 2: Save to CSV
        print(f"\n💾 Saving data to {OUTPUT_FILE}...")
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ File saved: {OUTPUT_FILE} ({len(df)} rows)")
        
        # Step 3: Get Google Drive credentials
        creds = get_google_credentials(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        
        # Step 4: Upload to Google Drive
        file_id = upload_to_drive(OUTPUT_FILE, creds)
        
        # Step 5: Success message
        print("\n" + "="*80)
        print("✅ SUCCESS! File uploaded to Google Drive")
        print("="*80)
        print(f"📄 File: {OUTPUT_FILE}")
        print(f"📊 Records: {len(df):,}")
        print(f"🆔 Drive ID: {file_id}")
        print(f"🔗 View: https://drive.google.com/file/d/{file_id}/view")
        print("="*80 + "\n")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        exit(1)


if __name__ == "__main__":
    main()
