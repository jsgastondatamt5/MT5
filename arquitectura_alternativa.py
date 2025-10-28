"""
ARQUITECTURA ALTERNATIVA: Template en Kaggle + File ID desde GitHub
- Sube Forrest_template_FIXED.py a Kaggle como notebook base
- Crea launcher.py que solo pasa el file_id
- Mucho más simple y sin problemas de comillas
"""

import os
import sys
import json
import shutil
from datetime import datetime
import subprocess
from dotenv import load_dotenv

load_dotenv()

KAGGLE_USERNAME = os.getenv('KAGGLE_USERNAME', 'jsgastonalgotrading')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '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')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'jsgastondatamt5')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'MT5')


def create_launcher_notebook(file_id):
    """
    Crea un notebook minimalista que:
    1. Configura el file_id
    2. Descarga y ejecuta el template desde GitHub
    """
    
    launcher_code = f"""# ============================================================================
# Forrest Trading ML - Launcher
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Drive File ID: {file_id}
# ============================================================================

import os
import sys

# CONFIGURACIÓN DEL FILE_ID
DRIVE_FILE_ID = '{file_id}'
os.environ['DRIVE_FILE_ID'] = DRIVE_FILE_ID

print("="*70)
print("🚀 FORREST TRADING ML - LAUNCHER")
print("="*70)
print(f"📊 Drive File ID: {{DRIVE_FILE_ID}}")
print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# Descargar template desde GitHub
print("\\n📥 Downloading template from GitHub...")

import subprocess
import urllib.request

GITHUB_URL = "https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/main/Forrest_template_FIXED.py"

try:
    # Descargar el template
    print(f"🔗 URL: {{GITHUB_URL}}")
    
    with urllib.request.urlopen(GITHUB_URL) as response:
        template_code = response.read().decode('utf-8')
    
    print(f"✅ Template downloaded ({{len(template_code)}} characters)")
    
    # Ejecutar el template
    print("\\n▶️  Executing template...")
    print("="*70)
    
    exec(template_code, globals())
    
    print("\\n" + "="*70)
    print("✅ FORREST EXECUTION COMPLETED!")
    print("="*70)
    
except Exception as e:
    print(f"\\n❌ Error: {{e}}")
    import traceback
    traceback.print_exc()
"""
    
    # Crear notebook
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": launcher_code.split('\n')
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = f'Forrest_launcher_{date_str}.ipynb'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)
    
    # También crear alias sin fecha
    shutil.copy(output_file, 'Forrest_launcher.ipynb')
    
    print(f"✅ Created launcher: {output_file}")
    print(f"✅ Created alias: Forrest_launcher.ipynb")
    
    return output_file


def push_template_to_github():
    """Sube el template FIXED a GitHub para que Kaggle pueda descargarlo"""
    
    print("\n📤 Pushing template to GitHub...")
    
    if not os.path.exists('Forrest_template_FIXED.py'):
        print("❌ Forrest_template_FIXED.py not found!")
        return False
    
    try:
        # Configurar git
        subprocess.run(['git', 'config', '--global', 'user.email', f'{GITHUB_USERNAME}@users.noreply.github.com'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', GITHUB_USERNAME], check=True)
        
        # Sync
        repo_url = f'https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git'
        
        try:
            subprocess.run(['git', 'pull', repo_url, 'main', '--rebase'], check=True)
        except:
            subprocess.run(['git', 'pull', repo_url, 'main', '--no-rebase'], check=True)
        
        # Add template
        subprocess.run(['git', 'add', 'Forrest_template_FIXED.py'], check=True)
        
        # Commit
        subprocess.run(['git', 'commit', '-m', 'Update Forrest template'], check=True)
        
        # Push
        subprocess.run(['git', 'push', repo_url, 'main'], check=True)
        
        print(f"✅ Template pushed to GitHub")
        print(f"🔗 URL: https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/main/Forrest_template_FIXED.py")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False


def push_launcher_to_kaggle(notebook_file, file_id):
    """Sube el launcher a Kaggle"""
    
    print(f"\n🚀 Pushing launcher to Kaggle...")
    
    try:
        # Import Kaggle API
        from kaggle import api
        
        # Authenticate
        api.authenticate()
        print("✅ Kaggle API authenticated")
        
        # Preparar metadata
        date_str = datetime.now().strftime('%Y%m%d')
        kernel_slug = f"{KAGGLE_USERNAME}/forrest-launcher-{date_str}"
        
        # Crear directorio temporal
        kernel_dir = f'/tmp/kaggle_launcher_{date_str}'
        os.makedirs(kernel_dir, exist_ok=True)
        
        # Copiar notebook
        notebook_dest = os.path.join(kernel_dir, 'Forrest_launcher.ipynb')
        shutil.copy(notebook_file, notebook_dest)
        
        # Crear metadata
        kernel_metadata = {
            "id": kernel_slug,
            "title": f"Forrest Launcher - {date_str}",
            "code_file": "Forrest_launcher.ipynb",
            "language": "python",
            "kernel_type": "notebook",
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
        
        # Push
        print("🔄 Pushing to Kaggle...")
        
        try:
            result = api.kernels_push(kernel_dir)
            print("✅ Pushed to Kaggle!")
            print(f"🔗 Kernel: https://www.kaggle.com/{kernel_slug}")
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if 'conflict' in error_msg or '409' in error_msg:
                print("⚠️  Kernel exists, trying update...")
                result = api.kernels_push(kernel_dir)
                print("✅ Updated!")
                return True
            else:
                print(f"❌ Failed: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main(file_id):
    """
    Main workflow:
    1. Push template to GitHub (solo una vez)
    2. Create launcher notebook with file_id
    3. Push launcher to Kaggle
    """
    
    print("\n" + "="*80)
    print("🏗️  ARQUITECTURA ALTERNATIVA - Template desde GitHub")
    print("="*80)
    print(f"📊 Drive File ID: {file_id}")
    print("="*80)
    
    # 1. Push template to GitHub (solo si no está ya)
    if os.path.exists('Forrest_template_FIXED.py'):
        print("\n📤 Step 1: Upload template to GitHub")
        push_template_to_github()
    else:
        print("\n⚠️  Forrest_template_FIXED.py not found, assuming it's already in GitHub")
    
    # 2. Create launcher
    print("\n📝 Step 2: Create launcher notebook")
    launcher_file = create_launcher_notebook(file_id)
    
    # 3. Push launcher to Kaggle
    print("\n🚀 Step 3: Push launcher to Kaggle")
    push_launcher_to_kaggle(launcher_file, file_id)
    
    print("\n" + "="*80)
    print("✅ WORKFLOW COMPLETED!")
    print("="*80)
    print("📦 Template in GitHub (reusable)")
    print("🚀 Launcher in Kaggle (with file_id)")
    print("💡 Ventajas:")
    print("   - Sin problemas de comillas")
    print("   - Template actualizable sin regenerar")
    print("   - Launcher muy simple (solo 40 líneas)")
    print("="*80)


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        file_id = sys.argv[1]
    else:
        # Default file_id (cambiar por el tuyo)
        file_id = "16xkD3sGMfuXiUCKREfRApSK7XddX18Ck"
        print(f"⚠️  Using default file_id: {file_id}")
        print(f"   Usage: python {sys.argv[0]} <file_id>")
    
    main(file_id)
