#!/usr/bin/env python3
"""
Test Dukascopy Setup - Quick verification
Versión mejorada que no falla si faltan credenciales
"""

import sys
from datetime import datetime, timedelta

def print_status(message, status):
    """Print colored status"""
    colors = {
        'ok': '\033[92m',
        'error': '\033[91m',
        'warning': '\033[93m',
        'info': '\033[94m',
        'end': '\033[0m'
    }
    symbol = {'ok': '✅', 'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}
    print(f"{colors[status]}{symbol[status]} {message}{colors['end']}")

def main():
    print("\n" + "="*70)
    print("🧪 DUKASCOPY SETUP TEST")
    print("="*70 + "\n")
    
    all_ok = True
    warnings = []
    
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
    packages = ['pandas', 'numpy', 'google.auth']
    for pkg in packages:
        try:
            __import__(pkg)
            print_status(f"{pkg} - OK", 'ok')
        except ImportError:
            print_status(f"{pkg} - Missing", 'error')
            all_ok = False
    
    # Test kaggle separately (it auto-authenticates on import)
    print("\n🏆 Kaggle:")
    try:
        import os
        # Check if kaggle.json exists first
        kaggle_path = os.path.expanduser('~/.kaggle/kaggle.json')
        if os.path.exists(kaggle_path):
            import kaggle
            print_status("kaggle package - OK", 'ok')
            print_status("kaggle.json - Found", 'ok')
        else:
            # Try to import without authentication
            import importlib.util
            spec = importlib.util.find_spec("kaggle")
            if spec is not None:
                print_status("kaggle package - Installed", 'ok')
                print_status("kaggle.json - Not configured (optional for testing)", 'warning')
                warnings.append("Kaggle credentials not configured. Needed for Kaggle push.")
            else:
                print_status("kaggle package - Missing", 'error')
                all_ok = False
    except Exception as e:
        print_status(f"kaggle check failed: {str(e)}", 'error')
        all_ok = False
    
    # Test 4: Test actual download (small sample)
    print("\n🔍 Testing Dukascopy Connection:")
    try:
        import dukascopy_python
        from dukascopy_python import instruments
        
        print_status("Attempting small test download...", 'info')
        
        end = datetime.now()
        start = end - timedelta(days=2)
        
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
            print_status("No data received (might be weekend)", 'warning')
            warnings.append("No data in test download (market might be closed)")
            
    except Exception as e:
        print_status(f"Connection test failed: {str(e)}", 'error')
        all_ok = False
    
    # Test 5: Check files
    print("\n📄 Required Files:")
    import os
    files = {
        'main_chunk_dukascopy.py': ('Main script', True),
        'Forrest.ipynb': ('ML notebook', True),
        'credentials.json': ('Google Drive credentials', True),
        'kaggle.json': ('Kaggle credentials', False)
    }
    
    for filename, (description, required) in files.items():
        if filename == 'kaggle.json':
            exists = os.path.exists(filename) or os.path.exists(os.path.expanduser('~/.kaggle/kaggle.json'))
        else:
            exists = os.path.exists(filename)
        
        if exists:
            print_status(f"{filename} - Found ({description})", 'ok')
        else:
            if required:
                print_status(f"{filename} - Missing ({description})", 'error')
                all_ok = False
            else:
                print_status(f"{filename} - Not configured ({description})", 'warning')
                warnings.append(f"{filename} not configured. Needed for {description}.")
    
    # Summary
    print("\n" + "="*70)
    if all_ok and not warnings:
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n🚀 You can now run: python main_chunk_dukascopy.py")
        print("\n📊 Dukascopy provides bank-quality forex data")
        print("   Perfect for professional trading strategies!")
        return 0
    elif all_ok and warnings:
        print("⚠️  ALL CRITICAL TESTS PASSED (with warnings)")
        print("="*70)
        print("\n🎯 Core functionality is ready!")
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"   • {warning}")
        print("\n💡 You can still test Dukascopy download:")
        print("   python main_chunk_dukascopy.py")
        print("\n📝 To configure missing items for full functionality:")
        print("   1. Setup kaggle.json:")
        print("      mkdir -p ~/.kaggle")
        print("      cp kaggle.json ~/.kaggle/kaggle.json")
        print("      chmod 600 ~/.kaggle/kaggle.json")
        print("\n   2. Or run: python setup_credentials.py")
        return 0
    else:
        print("❌ SOME CRITICAL TESTS FAILED")
        print("="*70)
        print("\n📝 Fix the issues above before running the main script")
        print("\n💡 Quick fixes:")
        print("   • Install dukascopy: pip install dukascopy-python")
        print("   • Install other deps: pip install -r requirements_dukascopy.txt")
        print("   • Add credentials files")
        print("\n🔧 Setup help:")
        print("   python setup_credentials.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
