#!/usr/bin/env python3
"""
Script de Implementación del Fix - Paso a Paso
Reemplaza el template bugueado con el arreglado
"""

import os
import shutil
from datetime import datetime

def backup_file(file_path):
    """Crea backup de un archivo"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backup creado: {os.path.basename(backup_path)}")
        return backup_path
    return None


def main():
    print("\n" + "="*70)
    print("🔧 IMPLEMENTACIÓN DEL FIX - FORREST TEMPLATE")
    print("="*70)
    
    # Archivos
    original = "Forrest_template.py"
    fixed = "Forrest_template_FIXED.py"
    
    # Verificar que existe el arreglado
    if not os.path.exists(fixed):
        print(f"\n❌ Error: No se encuentra {fixed}")
        print(f"   Asegúrate de tener el archivo arreglado en el directorio actual")
        return False
    
    print(f"\n📋 PASOS A SEGUIR:")
    print(f"   1. Crear backup del template original")
    print(f"   2. Reemplazar con template arreglado")
    print(f"   3. Verificar sintaxis")
    print(f"   4. Probar generación de archivos")
    
    # Confirmar
    print(f"\n⚠️  IMPORTANTE:")
    print(f"   - Se creará un backup automático del template original")
    print(f"   - El template arreglado tiene sintaxis correcta verificada")
    print(f"   - Puedes restaurar el backup si algo sale mal")
    
    response = input(f"\n¿Continuar con la implementación? (s/n): ").lower().strip()
    
    if response != 's':
        print("\n❌ Implementación cancelada por el usuario")
        return False
    
    print(f"\n{'='*70}")
    print("🚀 INICIANDO IMPLEMENTACIÓN")
    print(f"{'='*70}")
    
    # Paso 1: Backup
    print(f"\n[1/4] Creando backup...")
    if os.path.exists(original):
        backup_path = backup_file(original)
        if backup_path:
            print(f"      Backup guardado en: {backup_path}")
    else:
        print(f"      ℹ️  Template original no existe (primera instalación)")
    
    # Paso 2: Reemplazar
    print(f"\n[2/4] Reemplazando template...")
    try:
        shutil.copy2(fixed, original)
        print(f"      ✅ {original} actualizado con versión arreglada")
    except Exception as e:
        print(f"      ❌ Error al copiar: {e}")
        return False
    
    # Paso 3: Verificar sintaxis
    print(f"\n[3/4] Verificando sintaxis...")
    try:
        import py_compile
        py_compile.compile(original, doraise=True)
        print(f"      ✅ Sintaxis verificada correctamente")
    except SyntaxError as e:
        print(f"      ❌ Error de sintaxis: {e}")
        return False
    
    # Paso 4: Mensaje de próximos pasos
    print(f"\n[4/4] Implementación completada")
    
    print(f"\n{'='*70}")
    print("✅ FIX IMPLEMENTADO EXITOSAMENTE")
    print(f"{'='*70}")
    
    print(f"\n📋 PRÓXIMOS PASOS:")
    print(f"\n1️⃣  Probar la generación de archivos:")
    print(f"   python main_chunk_dukascopy_v2.py")
    
    print(f"\n2️⃣  Verificar que se crean los archivos:")
    print(f"   - Forrest_YYYYMMDD.py")
    print(f"   - Forrest_YYYYMMDD.ipynb")
    print(f"   - Forrest.py")
    print(f"   - Forrest.ipynb")
    
    print(f"\n3️⃣  Push a GitHub:")
    print(f"   git add Forrest*")
    print(f"   git commit -m 'Fixed template syntax error'")
    print(f"   git push")
    
    print(f"\n4️⃣  Push a Kaggle:")
    print(f"   python push_to_kaggle_fixed.py")
    
    print(f"\n5️⃣  Ejecutar en Kaggle y verificar:")
    print(f"   - NO debe aparecer: 'SyntaxError: unterminated triple-quoted string'")
    print(f"   - Debe aparecer: '✅ Importaciones completadas'")
    print(f"   - Verificar instalación de 'ta' en los logs")
    
    print(f"\n{'='*70}")
    print("💡 NOTAS IMPORTANTES")
    print(f"{'='*70}")
    print(f"• Si algo sale mal, restaura el backup:")
    if backup_path:
        print(f"  cp {os.path.basename(backup_path)} {original}")
    print(f"• El código ahora usa try/except para 'ta':")
    print(f"  - Si 'ta' se instala → la usa")
    print(f"  - Si 'ta' falla → usa implementación manual")
    print(f"• Ambos escenarios son válidos y funcionales")
    
    return True


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
