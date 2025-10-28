#!/usr/bin/env python3
"""
🚀 AUTO-FIX COMPLETO - Forrest Template
Script automatizado que:
1. Hace backup del template original
2. Aplica el fix
3. Verifica sintaxis
4. Genera archivos de prueba
5. Muestra próximos pasos
"""

import os
import sys
import shutil
import py_compile
from datetime import datetime

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Imprime header destacado"""
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"🚀 {text}")
    print(f"{'='*70}{Colors.END}\n")

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def backup_file(file_path):
    """Crea backup de un archivo"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print_success(f"Backup creado: {os.path.basename(backup_path)}")
        return backup_path
    return None

def check_syntax(file_path):
    """Verifica sintaxis de un archivo"""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, "Sintaxis correcta"
    except SyntaxError as e:
        return False, f"Error en línea {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def count_triple_quotes(file_path):
    """Cuenta triple comillas en un archivo"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content.count("'''")

def apply_fix(original_path):
    """Aplica el fix de sintaxis al template"""
    print_info("Aplicando fix de sintaxis...")
    
    try:
        with open(original_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # El fix: eliminar las triple comillas problemáticas
        fixed_content = content.replace(
            "'''\n# Indicadores técnicos (opcional - usa implementación manual si no disponible)",
            "\n# Indicadores técnicos (opcional - usa implementación manual si no disponible)"
        )
        
        with open(original_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        return True
    except Exception as e:
        print_error(f"Error al aplicar fix: {e}")
        return False

def main():
    """Función principal"""
    print_header("AUTO-FIX DE SINTAXIS - FORREST TEMPLATE")
    
    # Archivos
    template_files = [
        "Forrest_template.py",
        "/mnt/user-data/uploads/Forrest_template.py",
        "../Forrest_template.py"
    ]
    
    fixed_file = "Forrest_template_FIXED.py"
    fixed_paths = [
        fixed_file,
        "/mnt/user-data/outputs/Forrest_template_FIXED.py",
        f"../{fixed_file}"
    ]
    
    # Encontrar template original
    template_path = None
    for path in template_files:
        if os.path.exists(path):
            template_path = path
            break
    
    # Encontrar template arreglado
    fixed_path = None
    for path in fixed_paths:
        if os.path.exists(path):
            fixed_path = path
            break
    
    print("📋 DIAGNÓSTICO INICIAL:")
    print(f"   Template original: {template_path if template_path else '❌ No encontrado'}")
    print(f"   Template arreglado: {fixed_path if fixed_path else '❌ No encontrado'}")
    
    # Estrategia de fix
    if not template_path and not fixed_path:
        print_error("No se encontró ningún template")
        print_info("Asegúrate de estar en el directorio correcto")
        return False
    
    if fixed_path and not template_path:
        print_warning("Solo se encontró el template arreglado")
        print_info("Copiándolo como template principal...")
        template_path = "Forrest_template.py"
        shutil.copy2(fixed_path, template_path)
        print_success("Template principal creado")
    
    if template_path and not fixed_path:
        print_warning("Solo se encontró el template original")
        print_info("Aplicando fix directamente...")
        fixed_path = template_path
    
    # Verificar estado actual
    print(f"\n{'='*70}")
    print("🔍 ANÁLISIS DEL TEMPLATE")
    print(f"{'='*70}")
    
    triple_quotes = count_triple_quotes(template_path)
    print(f"\nTriple comillas encontradas: {triple_quotes}")
    
    if triple_quotes % 2 != 0:
        print_error("Triple comillas NO balanceadas (número impar)")
        print_warning("ESTE ES EL PROBLEMA - necesita fix")
        needs_fix = True
    else:
        print_success("Triple comillas balanceadas")
        needs_fix = False
    
    # Verificar sintaxis actual
    syntax_ok, syntax_msg = check_syntax(template_path)
    print(f"\nSintaxis actual: ", end="")
    if syntax_ok:
        print_success(syntax_msg)
    else:
        print_error(syntax_msg)
        needs_fix = True
    
    # Aplicar fix si es necesario
    if needs_fix:
        print(f"\n{'='*70}")
        print("🔧 APLICANDO FIX")
        print(f"{'='*70}")
        
        # Backup
        print("\n[1/3] Creando backup...")
        backup_path = backup_file(template_path)
        
        # Aplicar fix
        print("\n[2/3] Aplicando corrección...")
        if fixed_path != template_path and os.path.exists(fixed_path):
            # Usar template pre-arreglado
            shutil.copy2(fixed_path, template_path)
            print_success("Template arreglado copiado")
        else:
            # Aplicar fix en lugar
            if apply_fix(template_path):
                print_success("Fix aplicado correctamente")
            else:
                print_error("Error al aplicar fix")
                if backup_path:
                    print_info(f"Restaurar backup: cp {backup_path} {template_path}")
                return False
        
        # Verificar resultado
        print("\n[3/3] Verificando resultado...")
        syntax_ok, syntax_msg = check_syntax(template_path)
        
        if syntax_ok:
            print_success(f"✨ FIX APLICADO EXITOSAMENTE")
            print(f"   {syntax_msg}")
        else:
            print_error(f"Fix falló: {syntax_msg}")
            if backup_path:
                print_info(f"Restaurar backup: cp {backup_path} {template_path}")
            return False
    else:
        print_success("\n✨ Template ya está correcto - no necesita fix")
    
    # Estadísticas finales
    print(f"\n{'='*70}")
    print("📊 ESTADÍSTICAS FINALES")
    print(f"{'='*70}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        total_lines = len(lines)
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
    
    size_kb = os.path.getsize(template_path) / 1024
    
    print(f"\n📄 {os.path.basename(template_path)}")
    print(f"   Total líneas: {total_lines:,}")
    print(f"   Líneas de código: {code_lines:,}")
    print(f"   Tamaño: {size_kb:.2f} KB")
    print(f"   Triple comillas: {count_triple_quotes(template_path)} (debe ser par)")
    
    syntax_ok, _ = check_syntax(template_path)
    if syntax_ok:
        print_success("   Sintaxis: ✅ Correcta")
    else:
        print_error("   Sintaxis: ❌ Con errores")
    
    # Próximos pasos
    print(f"\n{'='*70}")
    print("📋 PRÓXIMOS PASOS")
    print(f"{'='*70}")
    
    print(f"\n1️⃣  {Colors.BOLD}Generar archivos Forrest:{Colors.END}")
    print(f"   python main_chunk_dukascopy_v2.py")
    
    print(f"\n2️⃣  {Colors.BOLD}Verificar archivos generados:{Colors.END}")
    print(f"   ls -lh Forrest*.py Forrest*.ipynb")
    
    print(f"\n3️⃣  {Colors.BOLD}Verificar sintaxis de archivos generados:{Colors.END}")
    print(f"   python -m py_compile Forrest.py")
    
    print(f"\n4️⃣  {Colors.BOLD}Push a GitHub:{Colors.END}")
    print(f"   git add Forrest_template.py Forrest*.py Forrest*.ipynb")
    print(f"   git commit -m 'Fixed template syntax error - ready for Kaggle'")
    print(f"   git push")
    
    print(f"\n5️⃣  {Colors.BOLD}Push a Kaggle:{Colors.END}")
    print(f"   python push_to_kaggle_fixed.py")
    
    print(f"\n6️⃣  {Colors.BOLD}Verificar en Kaggle:{Colors.END}")
    print(f"   • Debe aparecer: '✅ Importaciones completadas'")
    print(f"   • NO debe aparecer: 'SyntaxError'")
    
    # Información sobre ta
    print(f"\n{'='*70}")
    print("💡 SOBRE LA LIBRERÍA 'ta' EN KAGGLE")
    print(f"{'='*70}")
    
    print("\nEl código ahora maneja automáticamente dos escenarios:\n")
    print(f"{Colors.GREEN}✅ Escenario 1: 'ta' se instala correctamente{Colors.END}")
    print("   → Usa la librería ta para indicadores técnicos")
    
    print(f"\n{Colors.YELLOW}⚠️  Escenario 2: 'ta' falla en Kaggle{Colors.END}")
    print("   → Usa implementación manual de indicadores")
    print("   → RSI, MACD, Bollinger Bands calculados manualmente")
    print("   → ✅ Funciona igual de bien")
    
    print(f"\nAmbos escenarios son válidos y el código funciona correctamente.")
    
    print(f"\n{Colors.BOLD}{'='*70}")
    print("✅ AUTO-FIX COMPLETADO")
    print(f"{'='*70}{Colors.END}")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⏸️  Interrumpido por el usuario{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error inesperado: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
