#!/bin/bash

# ============================================================================
# SCRIPT DE DEPLOYMENT RÁPIDO
# Despliega todo el sistema al repositorio de GitHub
# ============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=========================================="
echo "🚀 DEPLOYMENT AL REPOSITORIO GITHUB"
echo "=========================================="
echo -e "${NC}"

# Variables
REPO_URL="https://github.com/jsgastondatamt5/MT5.git"
GITHUB_TOKEN="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"
GITHUB_USERNAME="jsgastondatamt5"
GITHUB_REPO="MT5"

# Check if we're in the right directory
if [ ! -f "main_chunk_kaggle.py" ]; then
    echo -e "${RED}❌ Error: main_chunk_kaggle.py not found${NC}"
    echo "   Please run this script from the project directory"
    exit 1
fi

# Check git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Pre-checks passed${NC}\n"

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git remote add origin "https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${GITHUB_REPO}.git"
    echo -e "${GREEN}✅ Git initialized${NC}\n"
else
    echo "📦 Git repository already initialized"
    
    # Update remote to use token
    git remote set-url origin "https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${GITHUB_REPO}.git"
    echo -e "${GREEN}✅ Remote URL updated${NC}\n"
fi

# Configure git
echo "⚙️  Configuring git..."
git config user.email "${GITHUB_USERNAME}@users.noreply.github.com"
git config user.name "${GITHUB_USERNAME}"
echo -e "${GREEN}✅ Git configured${NC}\n"

# Create .gitignore if not exists
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
credentials.json
token.json
kaggle.json
.env
*.csv
__pycache__/
*.pyc
.vscode/
.DS_Store
EOF
    echo -e "${GREEN}✅ .gitignore created${NC}\n"
fi

# List files to be committed
echo "📋 Files to be deployed:"
echo "----------------------------------------"
ls -1 | grep -v ".git" | grep -v "credentials.json" | grep -v "token.json" | grep -v "kaggle.json" | grep -v ".env"
echo "----------------------------------------"
echo ""

# Confirm
read -p "$(echo -e ${YELLOW}Continue with deployment? [y/N]:${NC} )" -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⏸️  Deployment cancelled${NC}"
    exit 0
fi

# Git operations
echo ""
echo "📤 Starting deployment..."
echo ""

# Add files
echo "1️⃣  Adding files..."
git add .
echo -e "${GREEN}✅ Files added${NC}\n"

# Commit
echo "2️⃣  Committing..."
COMMIT_MSG="Initial deployment: Complete trading ML system with Kaggle integration - $(date +'%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG" || echo "No changes to commit"
echo -e "${GREEN}✅ Committed${NC}\n"

# Push
echo "3️⃣  Pushing to GitHub..."
git branch -M main
git push -u origin main --force
echo -e "${GREEN}✅ Pushed to GitHub${NC}\n"

# Success
echo -e "${GREEN}"
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETADO EXITOSAMENTE!"
echo "=========================================="
echo -e "${NC}"
echo ""
echo "📍 Repositorio: https://github.com/${GITHUB_USERNAME}/${GITHUB_REPO}"
echo "📊 Actions: https://github.com/${GITHUB_USERNAME}/${GITHUB_REPO}/actions"
echo ""
echo "🎯 Próximos pasos:"
echo "   1. Configura los Secrets en GitHub (ver README.md)"
echo "   2. Verifica el workflow en Actions"
echo "   3. Ejecuta manualmente o espera la ejecución programada"
echo ""
echo "----------------------------------------"

# Cleanup - remove token from git config for security
git remote set-url origin "https://github.com/${GITHUB_USERNAME}/${GITHUB_REPO}.git"

echo -e "${GREEN}🔒 Token limpiado de la configuración local${NC}"
echo ""
