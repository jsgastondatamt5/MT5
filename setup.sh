#!/bin/bash

echo "=========================================="
echo "🚀 Setup Script for Daily Data Pipeline"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Check Python installation
echo "📋 Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# 2. Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

# 3. Setup Kaggle directory
echo ""
echo "📁 Setting up Kaggle directory..."
mkdir -p ~/.kaggle
if [ -f "kaggle.json" ]; then
    cp kaggle.json ~/.kaggle/kaggle.json
    chmod 600 ~/.kaggle/kaggle.json
    echo -e "${GREEN}✅ Kaggle credentials configured${NC}"
else
    echo -e "${YELLOW}⚠️  kaggle.json not found. Please add it manually to ~/.kaggle/${NC}"
    echo "   Get your API token from: https://www.kaggle.com/settings/account"
fi

# 4. Check Google Drive credentials
echo ""
echo "🔐 Checking Google Drive credentials..."
if [ -f "credentials.json" ]; then
    echo -e "${GREEN}✅ credentials.json found${NC}"
else
    echo -e "${YELLOW}⚠️  credentials.json not found${NC}"
    echo "   Download from: https://console.cloud.google.com/apis/credentials"
fi

# 5. Check .env file
echo ""
echo "⚙️  Checking environment variables..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file found${NC}"
else
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}   Please edit .env with your actual values${NC}"
    else
        echo -e "${RED}❌ .env.example not found${NC}"
    fi
fi

# 6. Git configuration
echo ""
echo "🔧 Configuring Git..."
git config --global user.email "github-actions[bot]@users.noreply.github.com"
git config --global user.name "github-actions[bot]"
echo -e "${GREEN}✅ Git configured${NC}"

# 7. Test imports
echo ""
echo "🧪 Testing Python imports..."
python3 << 'EOF'
import sys
packages = ['pandas', 'numpy', 'yfinance', 'google.auth', 'kaggle']
failed = []

for pkg in packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg}")
    except ImportError:
        print(f"❌ {pkg}")
        failed.append(pkg)

if failed:
    print(f"\n⚠️  Failed to import: {', '.join(failed)}")
    sys.exit(1)
else:
    print("\n✅ All core packages imported successfully")
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Some imports failed${NC}"
    exit 1
fi

# 8. Final instructions
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env with your credentials"
echo "   2. Add credentials.json (Google Drive)"
echo "   3. Add kaggle.json (Kaggle API)"
echo "   4. Add Forrest.ipynb template"
echo "   5. Run: python main_chunk_kaggle.py"
echo ""
echo "🔄 To automate daily:"
echo "   - GitHub Actions is configured in .github/workflows/"
echo "   - Set secrets in GitHub Settings > Secrets:"
echo "     • GOOGLE_CREDENTIALS"
echo "     • GOOGLE_TOKEN"
echo "     • KAGGLE_JSON"
echo "     • GH_PAT (Personal Access Token)"
echo "     • GH_USERNAME"
echo "     • KAGGLE_USERNAME"
echo ""
echo "=========================================="
