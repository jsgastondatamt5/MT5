#!/bin/bash

# ============================================================================
# CONFIGURAR Y VERIFICAR KAGGLE CLI
# ============================================================================

echo "========================================"
echo "🔍 Buscando comando Kaggle"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Buscar kaggle en diferentes ubicaciones
echo "📍 Buscando ejecutable de kaggle..."
echo ""

FOUND=0

# 1. which kaggle
if command -v kaggle &> /dev/null; then
    KAGGLE_PATH=$(which kaggle)
    echo -e "${GREEN}✅ Método 1: which kaggle${NC}"
    echo "   Path: $KAGGLE_PATH"
    FOUND=1
fi

# 2. ~/.local/bin/kaggle
if [ -f "$HOME/.local/bin/kaggle" ]; then
    echo -e "${GREEN}✅ Método 2: ~/.local/bin/kaggle${NC}"
    echo "   Path: $HOME/.local/bin/kaggle"
    if [ $FOUND -eq 0 ]; then
        KAGGLE_PATH="$HOME/.local/bin/kaggle"
        FOUND=1
    fi
fi

# 3. Buscar con find
FIND_RESULT=$(find $HOME/.local -name "kaggle" -type f -executable 2>/dev/null | head -n 1)
if [ ! -z "$FIND_RESULT" ]; then
    echo -e "${GREEN}✅ Método 3: find en ~/.local${NC}"
    echo "   Path: $FIND_RESULT"
    if [ $FOUND -eq 0 ]; then
        KAGGLE_PATH="$FIND_RESULT"
        FOUND=1
    fi
fi

echo ""

if [ $FOUND -eq 0 ]; then
    echo -e "${RED}❌ No se encontró el comando kaggle${NC}"
    echo ""
    echo "💡 Soluciones:"
    echo "   1. Verificar instalación: pip show kaggle"
    echo "   2. Reinstalar: pip install --user kaggle"
    echo "   3. Buscar manualmente: find ~ -name 'kaggle' -type f 2>/dev/null"
    exit 1
fi

echo "=========================================="
echo -e "${GREEN}✅ KAGGLE ENCONTRADO${NC}"
echo "=========================================="
echo "📍 Path: $KAGGLE_PATH"
echo ""

# Verificar permisos
if [ -x "$KAGGLE_PATH" ]; then
    echo -e "${GREEN}✅ Permisos de ejecución: OK${NC}"
else
    echo -e "${YELLOW}⚠️  Sin permisos de ejecución${NC}"
    echo "Agregando permisos..."
    chmod +x "$KAGGLE_PATH"
    echo -e "${GREEN}✅ Permisos agregados${NC}"
fi

echo ""

# Verificar PATH
echo "🔍 Verificando PATH..."
if echo $PATH | grep -q "$(dirname $KAGGLE_PATH)"; then
    echo -e "${GREEN}✅ Directorio de kaggle está en PATH${NC}"
else
    echo -e "${YELLOW}⚠️  Directorio de kaggle NO está en PATH${NC}"
    echo ""
    echo "Agregando a PATH..."
    KAGGLE_DIR=$(dirname $KAGGLE_PATH)
    
    # Agregar a .bashrc
    if ! grep -q "$KAGGLE_DIR" ~/.bashrc 2>/dev/null; then
        echo "" >> ~/.bashrc
        echo "# Kaggle CLI" >> ~/.bashrc
        echo "export PATH=\"$KAGGLE_DIR:\$PATH\"" >> ~/.bashrc
        echo -e "${GREEN}✅ Agregado a ~/.bashrc${NC}"
    fi
    
    # Agregar a sesión actual
    export PATH="$KAGGLE_DIR:$PATH"
    echo -e "${GREEN}✅ PATH actualizado en sesión actual${NC}"
fi

echo ""

# Test de funcionamiento
echo "🧪 Probando kaggle..."
if $KAGGLE_PATH --version &> /dev/null; then
    VERSION=$($KAGGLE_PATH --version 2>&1)
    echo -e "${GREEN}✅ Kaggle funciona correctamente${NC}"
    echo "   $VERSION"
else
    echo -e "${RED}❌ Kaggle no funciona correctamente${NC}"
    exit 1
fi

echo ""

# Test de credenciales
echo "🔑 Verificando credenciales..."
if [ -f "$HOME/.kaggle/kaggle.json" ]; then
    echo -e "${GREEN}✅ kaggle.json encontrado${NC}"
    echo "   Path: $HOME/.kaggle/kaggle.json"
    
    # Verificar permisos
    PERMS=$(stat -c '%a' "$HOME/.kaggle/kaggle.json" 2>/dev/null || stat -f '%A' "$HOME/.kaggle/kaggle.json" 2>/dev/null)
    if [ "$PERMS" = "600" ]; then
        echo -e "${GREEN}✅ Permisos correctos (600)${NC}"
    else
        echo -e "${YELLOW}⚠️  Permisos incorrectos ($PERMS), corrigiendo...${NC}"
        chmod 600 "$HOME/.kaggle/kaggle.json"
        echo -e "${GREEN}✅ Permisos corregidos${NC}"
    fi
    
    # Test de API
    echo ""
    echo "🧪 Probando API de Kaggle..."
    if $KAGGLE_PATH datasets list --max-size 1 &> /dev/null; then
        echo -e "${GREEN}✅ API de Kaggle funciona${NC}"
    else
        echo -e "${RED}❌ Error al conectar con Kaggle API${NC}"
        echo "   Verifica las credenciales en ~/.kaggle/kaggle.json"
    fi
else
    echo -e "${RED}❌ kaggle.json no encontrado${NC}"
    echo ""
    echo "💡 Configurar:"
    echo "   1. Descargar de: https://www.kaggle.com/settings/account"
    echo "   2. Copiar a: ~/.kaggle/kaggle.json"
    echo "   3. Ejecutar: chmod 600 ~/.kaggle/kaggle.json"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ VERIFICACIÓN COMPLETA${NC}"
echo "=========================================="
echo ""
echo "📝 Información:"
echo "   Comando: $KAGGLE_PATH"
echo "   En PATH: $(if echo $PATH | grep -q "$(dirname $KAGGLE_PATH)"; then echo "Sí"; else echo "No"; fi)"
echo "   Credenciales: $(if [ -f "$HOME/.kaggle/kaggle.json" ]; then echo "✅ Configuradas"; else echo "❌ No configuradas"; fi)"
echo ""
echo "💡 Uso:"
echo "   $KAGGLE_PATH datasets list --max-size 1"
echo "   $KAGGLE_PATH kernels list --user USUARIO"
echo ""
echo "🚀 Ahora puedes ejecutar:"
echo "   python main_chunk_dukascopy.py"
echo ""
