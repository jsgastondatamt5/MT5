#!/bin/bash

# ============================================================================
# SETUP COMPLETO PARA CODESPACES/LOCAL
# Configura todo automáticamente
# ============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "========================================================================"
echo "🚀 SETUP COMPLETO - DUKASCOPY DATA PIPELINE"
echo "========================================================================"
echo -e "${NC}"

# Detectar entorno
if [ -n "$CODESPACES" ]; then
    ENVIRONMENT="Codespaces"
    KAGGLE_DIR="$HOME/.config/kaggle"
else
    ENVIRONMENT="Local"
    KAGGLE_DIR="$HOME/.kaggle"
fi

echo -e "${GREEN}✅ Entorno detectado: $ENVIRONMENT${NC}"
echo ""

# ============================================================================
# 1. INSTALAR DEPENDENCIAS
# ============================================================================

echo -e "${BLUE}[1/5] Instalando dependencias Python...${NC}"

if [ -f "requirements_dukascopy.txt" ]; then
    pip install -q -r requirements_dukascopy.txt
    echo -e "${GREEN}✅ Dependencias instaladas desde requirements_dukascopy.txt${NC}"
else
    # Instalar manualmente si no hay requirements
    pip install -q dukascopy-python pandas numpy google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client kaggle python-dotenv
    echo -e "${GREEN}✅ Dependencias instaladas manualmente${NC}"
fi

echo ""

# ============================================================================
# 2. CONFIGURAR KAGGLE
# ============================================================================

echo -e "${BLUE}[2/5] Configurando Kaggle...${NC}"

# Buscar kaggle.json
KAGGLE_SOURCE=""
if [ -f "kaggle.json" ]; then
    KAGGLE_SOURCE="kaggle.json"
elif [ -f "../kaggle.json" ]; then
    KAGGLE_SOURCE="../kaggle.json"
elif [ -f "/mnt/user-data/uploads/kaggle__1_.json" ]; then
    KAGGLE_SOURCE="/mnt/user-data/uploads/kaggle__1_.json"
fi

if [ -n "$KAGGLE_SOURCE" ]; then
    # Crear directorio
    mkdir -p "$KAGGLE_DIR"
    
    # Copiar archivo
    cp "$KAGGLE_SOURCE" "$KAGGLE_DIR/kaggle.json"
    
    # Establecer permisos
    chmod 600 "$KAGGLE_DIR/kaggle.json"
    
    echo -e "${GREEN}✅ Kaggle configurado en: $KAGGLE_DIR/kaggle.json${NC}"
else
    echo -e "${YELLOW}⚠️  kaggle.json no encontrado${NC}"
    echo -e "${YELLOW}   Descárgalo desde: https://www.kaggle.com/settings/account${NC}"
    echo -e "${YELLOW}   Guárdalo en el directorio actual y vuelve a ejecutar este script${NC}"
fi

echo ""

# ============================================================================
# 3. VERIFICAR ARCHIVOS REQUERIDOS
# ============================================================================

echo -e "${BLUE}[3/5] Verificando archivos requeridos...${NC}"

# Check main script
if [ -f "main_chunk_dukascopy.py" ]; then
    echo -e "${GREEN}✅ main_chunk_dukascopy.py presente${NC}"
else
    echo -e "${RED}❌ main_chunk_dukascopy.py NO ENCONTRADO${NC}"
    echo -e "${YELLOW}   Este es el script principal, debe estar en el directorio${NC}"
fi

# Check Forrest notebook
if [ -f "Forrest.ipynb" ]; then
    echo -e "${GREEN}✅ Forrest.ipynb presente${NC}"
else
    echo -e "${YELLOW}⚠️  Forrest.ipynb no encontrado${NC}"
    echo -e "${YELLOW}   Necesario para crear Forrest.py${NC}"
fi

# Check credentials
if [ -f "credentials.json" ]; then
    echo -e "${GREEN}✅ credentials.json presente${NC}"
else
    echo -e "${YELLOW}⚠️  credentials.json no encontrado${NC}"
    echo -e "${YELLOW}   Descárgalo desde: https://console.cloud.google.com/apis/credentials${NC}"
fi

echo ""

# ============================================================================
# 4. TEST DE INSTALACIÓN
# ============================================================================

echo -e "${BLUE}[4/5] Probando instalación...${NC}"

# Test Python imports
python3 << 'EOF'
import sys
packages = {
    'dukascopy_python': 'Dukascopy',
    'pandas': 'Pandas',
    'numpy': 'NumPy',
    'google.auth': 'Google Auth',
    'kaggle': 'Kaggle'
}

all_ok = True
for module, name in packages.items():
    try:
        __import__(module)
        print(f"✅ {name}")
    except ImportError:
        print(f"❌ {name} - NO instalado")
        all_ok = False

if all_ok:
    print("\n✅ Todos los paquetes importados correctamente")
else:
    print("\n⚠️ Algunos paquetes faltan")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Importaciones exitosas${NC}"
else
    echo -e "${RED}❌ Algunas importaciones fallaron${NC}"
fi

echo ""

# ============================================================================
# 5. TEST DE DUKASCOPY
# ============================================================================

echo -e "${BLUE}[5/5] Probando conexión a Dukascopy...${NC}"

if [ -f "test_dukascopy.py" ]; then
    python3 test_dukascopy.py
    TEST_RESULT=$?
else
    echo -e "${YELLOW}⚠️  test_dukascopy.py no encontrado, saltando test${NC}"
    TEST_RESULT=0
fi

echo ""

# ============================================================================
# RESUMEN FINAL
# ============================================================================

echo -e "${BLUE}"
echo "========================================================================"
echo "📊 RESUMEN DEL SETUP"
echo "========================================================================"
echo -e "${NC}"

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ SETUP COMPLETADO EXITOSAMENTE${NC}"
    echo ""
    echo "🎉 ¡Todo listo para usar!"
    echo ""
    echo "📝 Siguiente paso:"
    echo ""
    echo -e "${BLUE}   python main_chunk_dukascopy.py${NC}"
    echo ""
    echo "💡 Opciones:"
    echo "   • Cambiar par: FOREX_PAIR=GBPUSD python main_chunk_dukascopy.py"
    echo "   • Más días: DAYS_TO_DOWNLOAD=180 python main_chunk_dukascopy.py"
    echo ""
    echo "📖 Documentación:"
    echo "   • CODESPACES.md - Guía específica para Codespaces"
    echo "   • LEEME_DUKASCOPY.md - Resumen completo"
    echo "   • QUICKSTART_DUKASCOPY.md - Guía rápida"
else
    echo -e "${YELLOW}⚠️  SETUP COMPLETADO CON ADVERTENCIAS${NC}"
    echo ""
    echo "Revisa los mensajes de arriba para ver qué falta."
    echo ""
    echo "💡 Soluciones comunes:"
    echo "   • pip install -r requirements_dukascopy.txt"
    echo "   • python setup_kaggle.py"
    echo "   • Añadir credentials.json y kaggle.json"
fi

echo "========================================================================"
