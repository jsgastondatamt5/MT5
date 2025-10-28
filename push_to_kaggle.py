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
    """Push script to Kaggle kernel"""
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
        
        # Create kernel metadata
        kernel_metadata = {
            "id": f"{KAGGLE_USERNAME}/{KAGGLE_KERNEL_SLUG}",
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
        
        # Try push with python -m kaggle first
        print("\n🔄 Attempting push to Kaggle...")
        print("   Method 1: Using 'python -m kaggle'")
        
        try:
            result = subprocess.run(
                ['python', '-m', 'kaggle', 'kernels', 'push', '-p', kernel_dir],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            method = "python -m kaggle"
            
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"   Method 1 failed: {e}")
            print("   Method 2: Using 'kaggle' command directly")
            
            try:
                result = subprocess.run(
                    ['kaggle', 'kernels', 'push', '-p', kernel_dir],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(result.stdout)
                method = "kaggle"
                
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                print(f"   Method 2 failed: {e}")
                print("\n   Method 3: Using full path")
                
                # Try with full path
                kaggle_path = os.path.expanduser('~/.local/bin/kaggle')
                result = subprocess.run(
                    [kaggle_path, 'kernels', 'push', '-p', kernel_dir],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(result.stdout)
                method = "full path"
        
        print("\n" + "="*70)
        print("✅ PUSH SUCCESSFUL!")
        print("="*70)
        print(f"📍 Method used: {method}")
        print(f"🔗 Kernel: https://www.kaggle.com/{KAGGLE_USERNAME}/{KAGGLE_KERNEL_SLUG}")
        print(f"📊 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Try to get kernel status
        print("\n▶️  Checking kernel status...")
        try:
            if method == "python -m kaggle":
                status_result = subprocess.run(
                    ['python', '-m', 'kaggle', 'kernels', 'status', f"{KAGGLE_USERNAME}/{KAGGLE_KERNEL_SLUG}"],
                    capture_output=True,
                    text=True
                )
            else:
                status_result = subprocess.run(
                    ['kaggle', 'kernels', 'status', f"{KAGGLE_USERNAME}/{KAGGLE_KERNEL_SLUG}"],
                    capture_output=True,
                    text=True
                )
            print(status_result.stdout)
        except Exception as e:
            print(f"   (Could not get status: {e})")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "="*70)
        print("❌ PUSH FAILED")
        print("="*70)
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        print("\n💡 Troubleshooting:")
        print("   1. Check kaggle is installed: pip install kaggle")
        print("   2. Check credentials: ls -la ~/.kaggle/kaggle.json")
        print("   3. Test manually: python -m kaggle datasets list --max-size 1")
        print("   4. Check PATH: echo $PATH")
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
