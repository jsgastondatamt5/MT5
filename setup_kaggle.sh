#!/bin/bash

# ============================================================================
# CONFIGURAR KAGGLE.JSON - Script Helper
# ============================================================================

echo "=========================================="
echo "🏆 Configurando Kaggle Credentials"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Kaggle directory
KAGGLE_DIR="$HOME/.kaggle"
KAGGLE_FILE="$KAGGLE_DIR/kaggle.json"

# Check if kaggle.json exists in current directory
if [ -f "kaggle.json" ]; then
    echo -e "${GREEN}✅ Found kaggle.json in current directory${NC}"
    
    # Create .kaggle directory
    echo "📁 Creating $KAGGLE_DIR directory..."
    mkdir -p "$KAGGLE_DIR"
    
    # Copy kaggle.json
    echo "📋 Copying kaggle.json..."
    cp kaggle.json "$KAGGLE_FILE"
    
    # Set permissions
    echo "🔒 Setting permissions (600)..."
    chmod 600 "$KAGGLE_FILE"
    
    # Verify
    if [ -f "$KAGGLE_FILE" ]; then
        echo ""
        echo -e "${GREEN}=========================================="
        echo "✅ KAGGLE CONFIGURED SUCCESSFULLY!"
        echo -e "==========================================${NC}"
        echo ""
        echo "📍 Location: $KAGGLE_FILE"
        echo "🔒 Permissions: $(ls -l $KAGGLE_FILE | awk '{print $1}')"
        echo ""
        echo "🧪 Test it with:"
        echo "   kaggle datasets list --max-size 1"
        echo ""
        echo "Or run the full test:"
        echo "   python test_dukascopy.py"
        echo ""
    else
        echo -e "${RED}❌ Error: Could not copy kaggle.json${NC}"
        exit 1
    fi
    
elif [ -f "$KAGGLE_FILE" ]; then
    echo -e "${GREEN}✅ kaggle.json already configured at $KAGGLE_FILE${NC}"
    echo ""
    echo "🔒 Permissions: $(ls -l $KAGGLE_FILE | awk '{print $1}')"
    echo ""
    
    # Check if permissions are correct
    PERMS=$(stat -c '%a' "$KAGGLE_FILE" 2>/dev/null || stat -f '%A' "$KAGGLE_FILE" 2>/dev/null)
    if [ "$PERMS" != "600" ]; then
        echo -e "${YELLOW}⚠️  Permissions should be 600${NC}"
        echo "Fixing permissions..."
        chmod 600 "$KAGGLE_FILE"
        echo -e "${GREEN}✅ Permissions fixed${NC}"
    fi
    
    echo ""
    echo "🧪 Test it with:"
    echo "   kaggle datasets list --max-size 1"
    echo ""
    
else
    echo -e "${RED}❌ Error: kaggle.json not found${NC}"
    echo ""
    echo "📝 How to get kaggle.json:"
    echo "   1. Go to: https://www.kaggle.com/settings/account"
    echo "   2. Scroll to 'API' section"
    echo "   3. Click 'Create New API Token'"
    echo "   4. Download and save as 'kaggle.json' in this directory"
    echo "   5. Run this script again"
    echo ""
    exit 1
fi
