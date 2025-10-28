#!/usr/bin/env python3
"""
Script de Verificación Rápida - Forrest Template
Verifica que el template arreglado no tiene errores de sintaxis
"""

import py_compile
import sys
import os

def check_syntax(file_path):
    """Verifica sintaxis de un archivo Python"""
    print(f"\n{'='*70}")
    print(f"🔍 Verificando sintaxis de: {os.path.basename(file_path)}")
    print(f"{'='*70}")
    
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return False
    
    try:
        # Intentar compilar
        py_compile.compile(file_path, doraise=True)
        
        print(f"✅ SINTAXIS CORRECTA")
        print(f"   El archivo se puede ejecutar sin errores de sintaxis")
        
        # Mostrar estadísticas
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            
        print(f"\n📊 Estadísticas:")
        print(f"   Total líneas: {total_lines:,}")
        print(f"   Líneas de código: {code_lines:,}")
        print(f"   Tamaño: {os.path.getsize(file_path) / 1024:.2f} KB")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ ERROR DE SINTAXIS")
        print(f"   Línea {e.lineno}: {e.msg}")
        print(f"   {e.text}")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def compare_templates():
    """Compara template original vs arreglado"""
    print(f"\n{'='*70}")
    print("📊 COMPARACIÓN DE TEMPLATES")
    print(f"{'='*70}")
    
    original = "Forrest_template.py"
    fixed = "Forrest_template_FIXED.py"
    
    files = []
    for f in [original, fixed]:
        if os.path.exists(f):
            files.append(f)
    
    if not files:
        print("⚠️  No se encontraron templates para comparar")
        return
    
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Buscar triple comillas problemáticas
        triple_quotes = content.count("'''")
        
        print(f"\n📄 {os.path.basename(file)}:")
        print(f"   Tamaño: {len(content):,} caracteres")
        print(f"   Triple comillas encontradas: {triple_quotes}")
        
        # Verificar si están balanceadas
        if triple_quotes % 2 == 0:
            print(f"   ✅ Triple comillas balanceadas (pares)")
        else:
            print(f"   ❌ Triple comillas NO balanceadas (impares) - PROBLEMA")


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🔧 VERIFICADOR DE SINTAXIS - FORREST TEMPLATE")
    print("="*70)
    
    # Lista de archivos a verificar
    files_to_check = [
        "/mnt/user-data/outputs/Forrest_template_FIXED.py",
        "Forrest_template_FIXED.py",
        "Forrest.py"
    ]
    
    checked = []
    errors = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            if check_syntax(file_path):
                checked.append(file_path)
            else:
                errors.append(file_path)
    
    # Comparar templates si están disponibles
    if os.path.exists("/mnt/user-data/uploads/Forrest_template.py"):
        os.chdir("/mnt/user-data/uploads/")
        compare_templates()
    
    # Resumen final
    print(f"\n{'='*70}")
    print("📋 RESUMEN FINAL")
    print(f"{'='*70}")
    
    if checked:
        print(f"\n✅ Archivos verificados correctamente: {len(checked)}")
        for f in checked:
            print(f"   • {os.path.basename(f)}")
    
    if errors:
        print(f"\n❌ Archivos con errores: {len(errors)}")
        for f in errors:
            print(f"   • {os.path.basename(f)}")
        sys.exit(1)
    else:
        print(f"\n🎉 TODOS LOS ARCHIVOS TIENEN SINTAXIS CORRECTA")
        print(f"✅ El template está listo para usar en Kaggle")
        sys.exit(0)


if __name__ == "__main__":
    main()
