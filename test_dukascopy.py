#!/usr/bin/env python3
"""
Test Dukascopy Setup - Quick verification
"""

import sys
from datetime import datetime, timedelta

def print_status(message, status):
    """Print colored status"""
    colors = {
        'ok': '\033[92m',
        'error': '\033[91m',
        'info': '\033[94m',
        'end': '\033[0m'
    }
    symbol = {'ok': '✅', 'error': '❌', 'info': 'ℹ️'}
    print(f"{colors[status]}{symbol[status]} {message}{colors['end']}")

def main():
    print("\n" + "="*70)
    print("🧪 DUKASCOPY SETUP TEST")
    print("="*70 + "\n")
    
    all_ok = True
    
    # Test 1: Python version
    print("📋 Python Version:")
    if sys.version_info >= (3, 8):
        print_status(f"Python {sys.version_info.major}.{sys.version_info.minor} - Compatible", 'ok')
    else:
        print_status(f"Python {sys.version_info.major}.{sys.version_info.minor} - Need 3.8+", 'error')
        all_ok = False
    
    # Test 2: Import dukascopy_python
    print("\n📦 Dukascopy Package:")
    try:
        import dukascopy_python
        print_status("dukascopy-python installed", 'ok')
        
        # Test import of instruments
        from dukascopy_python import instruments
        print_status("dukascopy instruments module OK", 'ok')
        
        # Show available pairs
        pairs = [attr for attr in dir(instruments) if attr.startswith('INSTRUMENT_FX_MAJORS_')]
        print_status(f"Available pairs: {len(pairs)}", 'info')
        
    except ImportError as e:
        print_status(f"dukascopy-python NOT installed", 'error')
        print_status(f"  Install: pip install dukascopy-python", 'info')
        all_ok = False
    
    # Test 3: Basic dependencies
    print("\n📚 Core Dependencies:")
    packages = ['pandas', 'numpy', 'google.auth', 'kaggle']
    for pkg in packages:
        try:
            __import__(pkg)
            print_status(f"{pkg} - OK", 'ok')
        except ImportError:
            print_status(f"{pkg} - Missing", 'error')
            all_ok = False
    
    # Test 4: Test actual download (small sample)
    print("\n🔍 Testing Dukascopy Connection:")
    try:
        import dukascopy_python
        from dukascopy_python import instruments
        
        print_status("Attempting small test download...", 'info')
        
        end = datetime.now()
        start = end - timedelta(days=1)
        
        test_df = dukascopy_python.fetch(
            instruments.INSTRUMENT_FX_MAJORS_EUR_USD,
            dukascopy_python.INTERVAL_MIN_1,
            dukascopy_python.OFFER_SIDE_BID,
            start,
            end,
        )
        
        if not test_df.empty:
            print_status(f"Downloaded {len(test_df)} test records", 'ok')
            print_status(f"  Columns: {list(test_df.columns)}", 'info')
            print_status(f"  Date range: {test_df.index[0]} to {test_df.index[-1]}", 'info')
        else:
            print_status("No data received (might be weekend)", 'error')
            all_ok = False
            
    except Exception as e:
        print_status(f"Connection test failed: {str(e)}", 'error')
        all_ok = False
    
    # Test 5: Check files
    print("\n📄 Required Files:")
    import os
    files = {
        'main_chunk_dukascopy.py': 'Main script',
        'Forrest.ipynb': 'ML notebook',
        'credentials.json': 'Google Drive credentials',
        'kaggle.json': 'Kaggle credentials (or ~/.kaggle/kaggle.json)'
    }
    
    for filename, description in files.items():
        if filename == 'kaggle.json':
            exists = os.path.exists(filename) or os.path.exists(os.path.expanduser('~/.kaggle/kaggle.json'))
        else:
            exists = os.path.exists(filename)
        
        if exists:
            print_status(f"{filename} - Found ({description})", 'ok')
        else:
            print_status(f"{filename} - Missing ({description})", 'error')
            if filename != 'main_chunk_dukascopy.py':
                all_ok = False
    
    # Summary
    print("\n" + "="*70)
    if all_ok:
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n🚀 You can now run: python main_chunk_dukascopy.py")
        print("\n📊 Dukascopy provides bank-quality forex data")
        print("   Perfect for professional trading strategies!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        print("="*70)
        print("\n📝 Fix the issues above before running the main script")
        print("\n💡 Quick fixes:")
        print("   • Install dukascopy: pip install dukascopy-python")
        print("   • Install other deps: pip install -r requirements_dukascopy.txt")
        print("   • Add credentials files")
        return 1

if __name__ == "__main__":
    sys.exit(main())
