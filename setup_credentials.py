#!/usr/bin/env python3
"""
Credentials Manager - Interactive setup for credentials
"""

import os
import json
import getpass
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(text)
    print("="*70 + "\n")


def print_step(number, text):
    """Print step number"""
    print(f"\n📍 Step {number}: {text}")
    print("-"*70)


def get_input(prompt, default=None, password=False):
    """Get user input with optional default"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if password:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt).strip()
    
    return value if value else default


def setup_google_credentials():
    """Setup Google Drive credentials"""
    print_step(1, "Google Drive API Setup")
    
    print("""
To use Google Drive API, you need:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Create a new project (or select existing)
3. Enable "Google Drive API"
4. Create "OAuth 2.0 Client ID" (Desktop app type)
5. Download the JSON file
""")
    
    action = get_input("Do you have the credentials.json file? (yes/no)", "no")
    
    if action.lower() in ['yes', 'y']:
        path = get_input("Enter path to credentials.json", "credentials.json")
        
        if os.path.exists(path):
            # Validate JSON
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                
                if 'web' in data or 'installed' in data:
                    if path != 'credentials.json':
                        import shutil
                        shutil.copy(path, 'credentials.json')
                        print("✅ credentials.json copied to current directory")
                    else:
                        print("✅ credentials.json already in place")
                    return True
                else:
                    print("❌ Invalid credentials.json format")
                    return False
            except json.JSONDecodeError:
                print("❌ Invalid JSON file")
                return False
        else:
            print(f"❌ File not found: {path}")
            return False
    else:
        print("""
⚠️  Please download credentials.json first:
   1. Visit: https://console.cloud.google.com/apis/credentials
   2. Follow the steps to create OAuth credentials
   3. Download and save as 'credentials.json'
   4. Run this script again
""")
        return False


def setup_kaggle_credentials():
    """Setup Kaggle API credentials"""
    print_step(2, "Kaggle API Setup")
    
    print("""
To use Kaggle API, you need:
1. Go to: https://www.kaggle.com/settings/account
2. In "API" section, click "Create New API Token"
3. Download the kaggle.json file
""")
    
    action = get_input("Do you have the kaggle.json file? (yes/no)", "no")
    
    if action.lower() in ['yes', 'y']:
        path = get_input("Enter path to kaggle.json", "kaggle.json")
        
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                
                if 'username' in data and 'key' in data:
                    # Create .kaggle directory
                    kaggle_dir = os.path.expanduser('~/.kaggle')
                    os.makedirs(kaggle_dir, exist_ok=True)
                    
                    # Copy file
                    dest = os.path.join(kaggle_dir, 'kaggle.json')
                    import shutil
                    shutil.copy(path, dest)
                    
                    # Set permissions
                    os.chmod(dest, 0o600)
                    
                    print(f"✅ kaggle.json installed to {dest}")
                    print(f"✅ Permissions set to 600")
                    print(f"✅ Username: {data['username']}")
                    return data['username']
                else:
                    print("❌ Invalid kaggle.json format")
                    return None
            except json.JSONDecodeError:
                print("❌ Invalid JSON file")
                return None
        else:
            print(f"❌ File not found: {path}")
            return None
    else:
        print("""
⚠️  Please download kaggle.json first:
   1. Visit: https://www.kaggle.com/settings/account
   2. Click "Create New API Token"
   3. Save the downloaded file
   4. Run this script again
""")
        return None


def setup_github():
    """Setup GitHub configuration"""
    print_step(3, "GitHub Configuration")
    
    print("""
You need a GitHub Personal Access Token with 'repo' permissions:
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: repo (all), workflow
4. Generate and copy the token
""")
    
    username = get_input("GitHub username", os.getenv('USER', ''))
    repo = get_input("Repository name (for Forrest.py)", "MT5")
    token = get_input("Personal Access Token", password=True)
    
    if username and repo and token:
        return {
            'username': username,
            'repo': repo,
            'token': token
        }
    else:
        print("❌ Missing required information")
        return None


def create_env_file(github_config, kaggle_username):
    """Create .env file"""
    print_step(4, "Creating .env file")
    
    env_content = f"""# Auto-generated configuration file
# Generated: {os.popen('date').read().strip()}

# Google Drive API
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json

# GitHub
GITHUB_TOKEN={github_config['token']}
GITHUB_USERNAME={github_config['username']}
GITHUB_REPO={github_config['repo']}

# Kaggle
KAGGLE_CONFIG_PATH=kaggle.json
KAGGLE_USERNAME={kaggle_username}
KAGGLE_KERNEL_SLUG=forrest-trading-ml

# Data Configuration
FOREX_SYMBOL=EURUSD=X
STOCK_SYMBOL=AAPL
TIMEFRAME=1m
DAYS_TO_DOWNLOAD=365
CHUNK_SIZE_DAYS=7
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created")


def setup_git():
    """Setup git configuration"""
    print_step(5, "Git Configuration")
    
    # Check if git is installed
    if os.system('git --version > /dev/null 2>&1') != 0:
        print("❌ Git not installed")
        return False
    
    # Get current git config
    current_name = os.popen('git config user.name').read().strip()
    current_email = os.popen('git config user.email').read().strip()
    
    if current_name and current_email:
        print(f"Current git config:")
        print(f"  Name: {current_name}")
        print(f"  Email: {current_email}")
        
        change = get_input("Keep current config? (yes/no)", "yes")
        if change.lower() in ['yes', 'y']:
            return True
    
    name = get_input("Git user name", current_name or os.getenv('USER', ''))
    email = get_input("Git user email", current_email or f"{name}@users.noreply.github.com")
    
    os.system(f'git config --global user.name "{name}"')
    os.system(f'git config --global user.email "{email}"')
    
    print("✅ Git configured")
    return True


def verify_setup():
    """Verify all setup"""
    print_header("🔍 Verifying Setup")
    
    checks = {
        'credentials.json': os.path.exists('credentials.json'),
        '~/.kaggle/kaggle.json': os.path.exists(os.path.expanduser('~/.kaggle/kaggle.json')),
        '.env': os.path.exists('.env'),
        'git configured': os.popen('git config user.name').read().strip() != ''
    }
    
    print("\nSetup Status:")
    for item, status in checks.items():
        symbol = "✅" if status else "❌"
        print(f"  {symbol} {item}")
    
    if all(checks.values()):
        print("\n" + "="*70)
        print("🎉 SETUP COMPLETE!")
        print("="*70)
        print("""
Next steps:
1. Run: python test_setup.py (to verify everything)
2. Run: python main_chunk_kaggle.py (to test the pipeline)
3. Configure GitHub Actions secrets if using automation

For GitHub Actions, add these secrets:
- GOOGLE_CREDENTIALS (content of credentials.json)
- GOOGLE_TOKEN (content of token.json, after first run)
- KAGGLE_JSON (content of kaggle.json)
- GH_PAT (your GitHub Personal Access Token)
- GH_USERNAME (your GitHub username)
- KAGGLE_USERNAME (your Kaggle username)
""")
        return True
    else:
        print("\n⚠️  Some items are not configured")
        return False


def main():
    """Main setup flow"""
    print_header("🚀 Credentials Manager - Interactive Setup")
    
    print("""
This script will help you configure:
✓ Google Drive API credentials
✓ Kaggle API credentials
✓ GitHub Personal Access Token
✓ Environment variables
✓ Git configuration

Press Ctrl+C at any time to cancel.
""")
    
    try:
        # Step 1: Google Drive
        if not setup_google_credentials():
            print("\n⚠️  Skipping remaining setup. Please configure Google Drive first.")
            return
        
        # Step 2: Kaggle
        kaggle_username = setup_kaggle_credentials()
        if not kaggle_username:
            print("\n⚠️  Skipping remaining setup. Please configure Kaggle first.")
            return
        
        # Step 3: GitHub
        github_config = setup_github()
        if not github_config:
            print("\n⚠️  GitHub configuration incomplete.")
            return
        
        # Step 4: Create .env
        create_env_file(github_config, kaggle_username)
        
        # Step 5: Git config
        setup_git()
        
        # Verify
        verify_setup()
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")


if __name__ == "__main__":
    main()
