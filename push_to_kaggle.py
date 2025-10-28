#!/usr/bin/env python3
"""
Push Forrest.py to Kaggle - Helper Script
Solo hace el push a Kaggle sin descargar datos de nuevo
"""

import os
import json
import shutil
import subprocess
from datetime import datetime

# Configuración
KAGGLE_USERNAME = os.getenv('KAGGLE_USERNAME', 'jsgastonalgotrading')
KAGGLE_KERNEL_SLUG = 'forrest-trading-ml'

def setup_kaggle_credentials():
    """Setup Kaggle API credentials"""
    kaggle_dir = os.path.expanduser('~/.kaggle')
    os.makedirs(kaggle_dir, exist_ok=True)
    
    kaggle_json_dest = os.path.join(kaggle_dir, 'kaggle.json')
    
    if not os.path.exists(kaggle_json_dest):
        if os.path.exists('kaggle.json'):
            shutil.copy('kaggle.json', kaggle_json_dest)
            os.chmod(kaggle_json_dest, 0o600)
            print("✅ Kaggle credentials configured")
        else:
            print(f"⚠️  Warning: kaggle.json not found")
            return False
    
    return True

def push_to_kaggle(script_path='Forrest.py'):
    """Push script to Kaggle kernel using Python API"""
    print("\n" + "="*70)
    print("🚀 PUSHING TO KAGGLE")
    print("="*70 + "\n")
    
    if not os.path.exists(script_path):
        print(f"❌ Error: {script_path} not found")
        return False
    
    print(f"📄 Script: {script_path}")
    
    try:
        # Setup credentials
        if not setup_kaggle_credentials():
            print("❌ Kaggle credentials not configured")
            return False
        
        # Import Kaggle API
        try:
            from kaggle import api
            print("✅ Kaggle API imported")
        except ImportError:
            print("❌ Kaggle package not found")
            print("   Install: pip install kaggle")
            return False
        
        # Authenticate
        try:
            api.authenticate()
            print("✅ Kaggle API authenticated")
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            print("\n💡 Check credentials:")
            print("   ls -la ~/.kaggle/kaggle.json")
            return False
        
        # Create kernel metadata
        kernel_slug = f"{KAGGLE_USERNAME}/{KAGGLE_KERNEL_SLUG}"
        
        kernel_metadata = {
            "id": kernel_slug,
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
        
        # Create temp directory
        kernel_dir = '/tmp/kaggle_kernel_push'
        os.makedirs(kernel_dir, exist_ok=True)
        
        # Copy script
        shutil.copy(script_path, os.path.join(kernel_dir, os.path.basename(script_path)))
        print(f"✅ Script copied to {kernel_dir}")
        
        # Save metadata
        metadata_path = os.path.join(kernel_dir, 'kernel-metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(kernel_metadata, f, indent=2)
        print(f"✅ Metadata created")
        
        # Push using Python API
        print("\n🔄 Pushing to Kaggle using Python API...")
        
        try:
            result = api.kernels_push(kernel_dir)
            
            print("\n" + "="*70)
            print("✅ PUSH SUCCESSFUL!")
            print("="*70)
            print(f"🔗 Kernel: https://www.kaggle.com/{kernel_slug}")
            print(f"📊 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if result and hasattr(result, 'ref'):
                print(f"📍 Ref: {result.ref}")
            
            print("="*70)
            
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # If kernel doesn't exist, try to create
            if 'not found' in error_msg or 'does not exist' in error_msg:
                print("⚠️  Kernel doesn't exist, creating new one...")
                
                try:
                    result = api.kernels_push_cli(kernel_dir)
                    
                    print("\n" + "="*70)
                    print("✅ NEW KERNEL CREATED!")
                    print("="*70)
                    print(f"🔗 Kernel: https://www.kaggle.com/{kernel_slug}")
                    print("="*70)
                    
                    return True
                    
                except Exception as create_error:
                    print("\n" + "="*70)
                    print("❌ FAILED TO CREATE KERNEL")
                    print("="*70)
                    print(f"Error: {create_error}")
                    print("\n💡 Try manually:")
                    print(f"   1. Go to: https://www.kaggle.com/code")
                    print(f"   2. Create a new notebook named: {KAGGLE_KERNEL_SLUG}")
                    print(f"   3. Run this script again")
                    return False
            else:
                print("\n" + "="*70)
                print("❌ PUSH FAILED")
                print("="*70)
                print(f"Error: {e}")
                print("\n💡 Troubleshooting:")
                print("   1. Check kernel exists: https://www.kaggle.com/code")
                print("   2. Check credentials: cat ~/.kaggle/kaggle.json")
                print("   3. Test API: python -c 'from kaggle import api; api.authenticate()'")
                return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    
    # Check for Forrest.py
    if not os.path.exists('Forrest.py'):
        print("❌ Error: Forrest.py not found")
        print("   Run main_chunk_dukascopy.py first to create it")
        sys.exit(1)
    
    # Push
    success = push_to_kaggle()
    
    sys.exit(0 if success else 1)
