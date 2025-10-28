#!/usr/bin/env python3
"""
Test Kaggle API - Quick verification
Prueba que la API de Python de Kaggle funciona correctamente
"""

import os
import sys

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
    print("🧪 KAGGLE API TEST")
    print("="*70 + "\n")
    
    success = True
    
    # Test 1: Import kaggle
    print("📦 Testing Kaggle package import...")
    try:
        from kaggle import api
        from kaggle.api.kaggle_api_extended import KaggleApi
        print_status("Kaggle package imported successfully", 'ok')
    except ImportError as e:
        print_status(f"Failed to import kaggle: {e}", 'error')
        print_status("Install: pip install kaggle", 'info')
        return 1
    
    # Test 2: Check credentials file
    print("\n🔑 Checking credentials...")
    kaggle_json = os.path.expanduser('~/.kaggle/kaggle.json')
    
    if os.path.exists(kaggle_json):
        print_status(f"kaggle.json found at {kaggle_json}", 'ok')
        
        # Check permissions
        stat_info = os.stat(kaggle_json)
        perms = oct(stat_info.st_mode)[-3:]
        
        if perms == '600':
            print_status(f"Permissions correct: {perms}", 'ok')
        else:
            print_status(f"Permissions should be 600, currently {perms}", 'warning')
            print_status("Fix: chmod 600 ~/.kaggle/kaggle.json", 'info')
    else:
        print_status(f"kaggle.json not found at {kaggle_json}", 'error')
        print_status("Setup: cp kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json", 'info')
        return 1
    
    # Test 3: Authenticate
    print("\n🔐 Testing authentication...")
    try:
        api.authenticate()
        print_status("Authentication successful", 'ok')
    except Exception as e:
        print_status(f"Authentication failed: {e}", 'error')
        return 1
    
    # Test 4: Test API call (list datasets)
    print("\n🌐 Testing API call (list datasets)...")
    try:
        # Get a small list of datasets as a test
        datasets = api.dataset_list(page_size=1)
        
        if datasets:
            print_status(f"API call successful - found {len(datasets)} dataset(s)", 'ok')
            if hasattr(datasets[0], 'ref'):
                print_status(f"Sample dataset: {datasets[0].ref}", 'info')
        else:
            print_status("API call returned no datasets (might be OK)", 'warning')
        
    except Exception as e:
        print_status(f"API call failed: {e}", 'error')
        success = False
    
    # Test 5: Check if kernel exists
    print("\n📊 Checking for existing kernel...")
    try:
        username = os.getenv('KAGGLE_USERNAME', 'jsgastonalgotrading')
        kernel_slug = 'forrest-trading-ml'
        
        # Try to get kernel info
        try:
            kernel = api.kernel_status(f"{username}/{kernel_slug}")
            print_status(f"Kernel exists: {username}/{kernel_slug}", 'ok')
            if hasattr(kernel, 'status'):
                print_status(f"Status: {kernel.status}", 'info')
        except Exception as e:
            error_msg = str(e).lower()
            if 'not found' in error_msg or 'does not exist' in error_msg:
                print_status(f"Kernel doesn't exist yet: {username}/{kernel_slug}", 'warning')
                print_status("Will be created on first push", 'info')
            else:
                print_status(f"Could not check kernel: {e}", 'warning')
    except Exception as e:
        print_status(f"Error checking kernel: {e}", 'warning')
    
    # Summary
    print("\n" + "="*70)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n🚀 You can now push to Kaggle:")
        print("   python push_to_kaggle.py")
        print("   # OR")
        print("   python main_chunk_dukascopy.py")
        print("\n💡 Kaggle Python API is working correctly!")
        return 0
    else:
        print("⚠️  SOME TESTS HAD WARNINGS")
        print("="*70)
        print("\n📝 API is authenticated but some features may not work")
        print("   You can still try to push to Kaggle")
        return 0

if __name__ == "__main__":
    sys.exit(main())
