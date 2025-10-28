#!/usr/bin/env python3
"""
Push to Kaggle - FIXED VERSION
Maneja correctamente el error 409 y los conflictos de slug
"""

import os
import sys
import json
import shutil
from datetime import datetime

# Configuration
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


def push_to_kaggle(script_path='Forrest.py', use_date_slug=True):
    """
    Push script to Kaggle kernel using Python API
    
    Args:
        script_path: Path to the Python script
        use_date_slug: If True, uses date in slug to avoid conflicts
    """
    print("\n" + "="*70)
    print("🚀 PUSHING TO KAGGLE - FIXED VERSION")
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
            return False
        
        # Determine slug
        date_str = datetime.now().strftime('%Y%m%d')
        
        if use_date_slug:
            # Use date to avoid conflicts
            kernel_slug = f"{KAGGLE_USERNAME}/forrest-{date_str}"
            title = f"Forrest Trading ML {date_str}"
        else:
            # Try to match title with slug
            kernel_slug = f"{KAGGLE_USERNAME}/forrest-trading-ml-dukascopy-data"
            title = "Forrest Trading ML - Dukascopy Data"
        
        print(f"📊 Kernel slug: {kernel_slug}")
        print(f"📝 Title: {title}")
        
        # Create temp directory
        kernel_dir = '/tmp/kaggle_kernel_fixed'
        os.makedirs(kernel_dir, exist_ok=True)
        
        # Copy script
        script_dest = os.path.join(kernel_dir, os.path.basename(script_path))
        shutil.copy(script_path, script_dest)
        print(f"✅ Script copied")
        
        # Create metadata
        kernel_metadata = {
            "id": kernel_slug,
            "title": title,
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
        
        metadata_path = os.path.join(kernel_dir, 'kernel-metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(kernel_metadata, f, indent=2)
        print("✅ Metadata created")
        
        # Show metadata for debugging
        print("\n📋 Metadata:")
        print(f"   ID: {kernel_slug}")
        print(f"   Title: {title}")
        
        # Push using Python API
        print("\n🔄 Pushing to Kaggle...")
        
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
            print("\n💡 Nota: Usa fechas en el slug para evitar conflictos")
            print("   Cada día crea un kernel diferente")
            
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle 409 conflict
            if '409' in error_msg or 'conflict' in error_msg:
                print("\n⚠️  ERROR 409: Kernel ya existe")
                print("\n💡 Opciones:")
                print("   1. Usar fecha en slug (ejecuta con use_date_slug=True)")
                print("   2. Eliminar kernel viejo: https://www.kaggle.com/code")
                print("   3. Cambiar KAGGLE_KERNEL_SLUG en el script")
                
                if not use_date_slug:
                    print("\n🔄 Reintentando con fecha en slug...")
                    return push_to_kaggle(script_path, use_date_slug=True)
                
                return False
            
            # Handle other errors
            else:
                print("\n" + "="*70)
                print("❌ PUSH FAILED")
                print("="*70)
                print(f"Error: {e}")
                print("\n💡 Troubleshooting:")
                print("   1. Check kernel exists: https://www.kaggle.com/code")
                print("   2. Verify slug matches title")
                print("   3. Try with date in slug")
                return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    
    # Check for Forrest.py
    if not os.path.exists('Forrest.py'):
        print("❌ Error: Forrest.py not found")
        print("   Run main_chunk_dukascopy.py first to create it")
        sys.exit(1)
    
    print("\n🔧 PUSH TO KAGGLE - FIXED VERSION")
    print("   Automatically handles 409 conflicts")
    print("   Uses dates to avoid slug conflicts\n")
    
    # Push with date slug (recommended)
    success = push_to_kaggle('Forrest.py', use_date_slug=True)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
