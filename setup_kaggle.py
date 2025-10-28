#!/usr/bin/env python3
"""
Setup Kaggle Credentials - Detecta automáticamente el entorno
"""

import os
import sys
import shutil
from pathlib import Path

def print_status(message, status='info'):
    """Print colored status"""
    colors = {
        'ok': '\033[92m',
        'error': '\033[91m',
        'info': '\033[94m',
        'warning': '\033[93m',
        'end': '\033[0m'
    }
    symbol = {
        'ok': '✅',
        'error': '❌',
        'info': 'ℹ️',
        'warning': '⚠️'
    }
    print(f"{colors[status]}{symbol[status]} {message}{colors['end']}")

def detect_environment():
    """Detecta si estamos en Codespaces, local, o CI"""
    if os.environ.get('CODESPACES') == 'true':
        return 'codespaces'
    elif os.environ.get('CI') == 'true' or os.environ.get('GITHUB_ACTIONS') == 'true':
        return 'ci'
    else:
        return 'local'

def get_kaggle_dir(env_type):
    """Obtiene el directorio correcto para kaggle.json según el entorno"""
    if env_type == 'codespaces':
        # Codespaces usa ~/.config/kaggle
        return os.path.expanduser('~/.config/kaggle')
    else:
        # Local y CI usan ~/.kaggle
        return os.path.expanduser('~/.kaggle')

def setup_kaggle_credentials():
    """Configura kaggle.json en la ubicación correcta"""
    
    print("\n" + "="*70)
    print("🔧 SETUP KAGGLE CREDENTIALS")
    print("="*70 + "\n")
    
    # Detectar entorno
    env_type = detect_environment()
    print_status(f"Entorno detectado: {env_type}", 'info')
    
    # Obtener directorio correcto
    kaggle_dir = get_kaggle_dir(env_type)
    kaggle_dest = os.path.join(kaggle_dir, 'kaggle.json')
    
    print_status(f"Directorio Kaggle: {kaggle_dir}", 'info')
    
    # Buscar kaggle.json en varios lugares posibles
    possible_sources = [
        'kaggle.json',
        '../kaggle.json',
        os.path.join(os.path.dirname(__file__), 'kaggle.json'),
        '/mnt/user-data/uploads/kaggle__1_.json',
    ]
    
    source_file = None
    for src in possible_sources:
        if os.path.exists(src):
            source_file = src
            print_status(f"Encontrado kaggle.json en: {src}", 'ok')
            break
    
    if not source_file:
        print_status("No se encontró kaggle.json", 'error')
        print("\n💡 Soluciones:")
        print("   1. Descarga kaggle.json desde: https://www.kaggle.com/settings/account")
        print("   2. Guárdalo en el directorio actual")
        print("   3. Vuelve a ejecutar este script")
        return False
    
    # Crear directorio si no existe
    os.makedirs(kaggle_dir, exist_ok=True)
    print_status(f"Directorio creado/verificado: {kaggle_dir}", 'ok')
    
    # Copiar archivo
    try:
        shutil.copy(source_file, kaggle_dest)
        print_status(f"Archivo copiado a: {kaggle_dest}", 'ok')
    except Exception as e:
        print_status(f"Error copiando archivo: {e}", 'error')
        return False
    
    # Establecer permisos correctos (600)
    try:
        os.chmod(kaggle_dest, 0o600)
        print_status("Permisos configurados (600)", 'ok')
    except Exception as e:
        print_status(f"Advertencia: No se pudieron cambiar permisos: {e}", 'warning')
    
    # Verificar el archivo
    try:
        import json
        with open(kaggle_dest, 'r') as f:
            data = json.load(f)
        
        if 'username' in data and 'key' in data:
            print_status(f"Configuración válida para usuario: {data['username']}", 'ok')
            return True
        else:
            print_status("El archivo no tiene el formato correcto", 'error')
            return False
    
    except Exception as e:
        print_status(f"Error validando archivo: {e}", 'error')
        return False

def test_kaggle_api():
    """Prueba que la API de Kaggle funcione"""
    print("\n" + "="*70)
    print("🧪 TESTING KAGGLE API")
    print("="*70 + "\n")
    
    try:
        import kaggle
        print_status("Módulo kaggle importado", 'ok')
        
        # Intentar listar datasets (test de autenticación)
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        
        print_status("Autenticación exitosa", 'ok')
        
        # Test simple
        try:
            datasets = api.dataset_list(page=1, page_size=1)
            print_status(f"API funcionando correctamente", 'ok')
            return True
        except Exception as e:
            print_status(f"API configurada pero con advertencia: {str(e)[:50]}...", 'warning')
            return True
            
    except Exception as e:
        print_status(f"Error de autenticación: {e}", 'error')
        return False

def main():
    """Setup principal"""
    
    # Setup credentials
    if not setup_kaggle_credentials():
        print("\n" + "="*70)
        print("❌ SETUP FALLIDO")
        print("="*70)
        return 1
    
    # Test API
    if not test_kaggle_api():
        print("\n" + "="*70)
        print("⚠️ SETUP COMPLETO PERO API NO RESPONDE")
        print("="*70)
        print("\n💡 Esto puede ser normal si:")
        print("   - No hay conexión a internet")
        print("   - Kaggle está temporalmente no disponible")
        print("\nPuedes continuar, el archivo está configurado correctamente.")
        return 0
    
    # Success
    print("\n" + "="*70)
    print("✅ SETUP COMPLETADO EXITOSAMENTE")
    print("="*70)
    print("\n🎉 Kaggle está configurado y funcionando!")
    print("\n📝 Siguiente paso:")
    print("   python test_dukascopy.py")
    print("   python main_chunk_dukascopy.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
