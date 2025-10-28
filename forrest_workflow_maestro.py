#!/usr/bin/env python3
"""
🚀 FORREST WORKFLOW MAESTRO
Script TODO-EN-UNO para elegir y ejecutar la solución correcta
"""

import os
import sys
from datetime import datetime

def print_banner():
    print("\n" + "="*80)
    print("🚀 FORREST TRADING ML - WORKFLOW MAESTRO")
    print("="*80)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def show_menu():
    print("\n🎯 SELECCIONA TU SOLUCIÓN:\n")
    
    print("1️⃣  SOLUCIÓN 1: Fix Rápido (main_chunk_v3_FIXED)")
    print("   ✅ Funciona de inmediato")
    print("   ✅ Mismo workflow que antes")
    print("   ✅ Sin comillas problemáticas")
    print("   ⚠️  Archivos grandes (~5000 líneas)\n")
    
    print("2️⃣  SOLUCIÓN 2: Arquitectura Alternativa")
    print("   ✅ Template en GitHub (actualizable)")
    print("   ✅ Launcher minimalista (~40 líneas)")
    print("   ✅ Más rápido de subir")
    print("   ⚠️  Requiere setup inicial\n")
    
    print("3️⃣  Ver diagnóstico del problema actual\n")
    print("4️⃣  Comparación detallada de soluciones\n")
    print("0️⃣  Salir\n")

def check_files():
    """Verifica qué archivos están disponibles"""
    files = {
        'v3_fixed': os.path.exists('main_chunk_dukascopy_v3_FIXED.py'),
        'alternativa': os.path.exists('arquitectura_alternativa.py'),
        'template': os.path.exists('Forrest_template_FIXED.py'),
        'v2_old': os.path.exists('main_chunk_dukascopy_v2.py')
    }
    return files

def diagnose_problem():
    """Muestra diagnóstico del problema"""
    print("\n" + "="*80)
    print("🔍 DIAGNÓSTICO DEL PROBLEMA")
    print("="*80)
    
    print("\n❌ Error actual:")
    print("   SyntaxError: unterminated triple-quoted string literal (line 243)")
    
    print("\n🔎 Causa raíz:")
    print("   El script v2 usa comillas triples (''') de forma incorrecta")
    print("   al generar el header del archivo Forrest.py")
    
    print("\n📝 Ejemplo del problema:")
    print("""
    # En main_chunk_v2, línea 326:
    header = f'''\"\"\"
    Forrest System
    \"\"\"
    '''  ← Estas comillas cierran antes de tiempo
    """)
    
    print("\n✅ Soluciones disponibles:")
    print("   1. Fix rápido: Usar comentarios (#) en lugar de comillas triples")
    print("   2. Arquitectura: Separar template de launcher")
    
    input("\n⏎ Presiona Enter para continuar...")

def compare_solutions():
    """Muestra comparación detallada"""
    print("\n" + "="*80)
    print("📊 COMPARACIÓN DETALLADA")
    print("="*80)
    
    print("\n" + "-"*80)
    print("| Aspecto              | Solución 1        | Solución 2           |")
    print("-"*80)
    print("| Complejidad          | Baja ⭐          | Media ⭐⭐           |")
    print("| Tamaño archivos      | 5000 líneas       | 40 líneas ✅         |")
    print("| Tiempo upload        | ~30 seg           | ~5 seg ✅            |")
    print("| Actualización        | Regenerar todo    | Automática ✅        |")
    print("| Setup inicial        | Ninguno ✅        | Una vez              |")
    print("| Mantenimiento        | Medio             | Fácil ✅             |")
    print("-"*80)
    
    print("\n💡 Recomendación:")
    print("   • AHORA: Usa Solución 1 (funciona de inmediato)")
    print("   • DESPUÉS: Migra a Solución 2 (mejor a largo plazo)")
    
    input("\n⏎ Presiona Enter para continuar...")

def run_solution_1():
    """Ejecuta la Solución 1"""
    print("\n" + "="*80)
    print("🚀 EJECUTANDO SOLUCIÓN 1: Fix Rápido")
    print("="*80)
    
    files = check_files()
    
    if not files['v3_fixed']:
        print("\n❌ Error: main_chunk_dukascopy_v3_FIXED.py no encontrado")
        print("   Descarga los archivos del output")
        return
    
    if not files['template']:
        print("\n⚠️  Warning: Forrest_template_FIXED.py no encontrado")
        print("   Asegúrate de tenerlo en el mismo directorio")
        cont = input("   ¿Continuar de todos modos? (y/n): ")
        if cont.lower() != 'y':
            return
    
    print("\n▶️  Ejecutando main_chunk_dukascopy_v3_FIXED.py...")
    print("="*80)
    
    os.system('python main_chunk_dukascopy_v3_FIXED.py')

def run_solution_2():
    """Ejecuta la Solución 2"""
    print("\n" + "="*80)
    print("🏗️  EJECUTANDO SOLUCIÓN 2: Arquitectura Alternativa")
    print("="*80)
    
    files = check_files()
    
    if not files['alternativa']:
        print("\n❌ Error: arquitectura_alternativa.py no encontrado")
        print("   Descarga los archivos del output")
        return
    
    if not files['template']:
        print("\n⚠️  Warning: Forrest_template_FIXED.py no encontrado")
        print("   Necesitas este archivo para la arquitectura alternativa")
        return
    
    print("\n📋 Esta solución requiere:")
    print("   1. Subir template a GitHub (una vez)")
    print("   2. Crear launcher con file_id")
    print("   3. Subir launcher a Kaggle")
    
    print("\n💡 Necesitas un Drive File ID")
    file_id = input("   Ingresa tu Drive File ID (o Enter para ejemplo): ").strip()
    
    if not file_id:
        file_id = "16xkD3sGMfuXiUCKREfRApSK7XddX18Ck"
        print(f"   Usando file_id de ejemplo: {file_id}")
    
    print("\n▶️  Ejecutando arquitectura_alternativa.py...")
    print("="*80)
    
    os.system(f'python arquitectura_alternativa.py {file_id}')

def show_next_steps():
    """Muestra los siguientes pasos"""
    print("\n" + "="*80)
    print("✅ SIGUIENTES PASOS")
    print("="*80)
    
    print("\n1️⃣  Si usaste Solución 1:")
    print("   • Verifica que Forrest.py se creó correctamente")
    print("   • Revisa que se subió a Kaggle sin errores")
    print("   • Ejecuta el kernel en Kaggle para verificar")
    
    print("\n2️⃣  Si usaste Solución 2:")
    print("   • Verifica que el template está en GitHub")
    print("   • Revisa que el launcher se creó correctamente")
    print("   • Ejecuta el kernel en Kaggle (debe descargar el template)")
    
    print("\n3️⃣  En caso de problemas:")
    print("   • Revisa los logs de Kaggle")
    print("   • Verifica que internet está habilitado en el kernel")
    print("   • Lee GUIA_SOLUCIONES.md para troubleshooting")
    
    print("\n📚 Archivos de ayuda:")
    print("   • GUIA_SOLUCIONES.md - Guía completa")
    print("   • EJEMPLO_PROBLEMA.py - Explicación del error")
    print("   • Este script - Workflow maestro")
    
    print("\n🔗 URLs útiles:")
    print("   • GitHub: https://github.com/jsgastondatamt5/MT5")
    print("   • Kaggle: https://www.kaggle.com/jsgastonalgotrading/code")
    print("   • Drive: https://drive.google.com")

def main():
    """Main menu loop"""
    while True:
        print_banner()
        show_menu()
        
        choice = input("👉 Selecciona una opción (0-4): ").strip()
        
        if choice == '1':
            run_solution_1()
            show_next_steps()
            input("\n⏎ Presiona Enter para volver al menú...")
            
        elif choice == '2':
            run_solution_2()
            show_next_steps()
            input("\n⏎ Presiona Enter para volver al menú...")
            
        elif choice == '3':
            diagnose_problem()
            
        elif choice == '4':
            compare_solutions()
            
        elif choice == '0':
            print("\n👋 ¡Hasta luego!\n")
            sys.exit(0)
            
        else:
            print("\n❌ Opción inválida. Intenta de nuevo.")
            input("⏎ Presiona Enter para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Interrumpido por el usuario")
        print("👋 ¡Hasta luego!\n")
        sys.exit(0)
