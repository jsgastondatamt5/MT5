#!/usr/bin/env python3
"""
Test script to verify all configurations and credentials
"""

import os
import sys
import json
from pathlib import Path

def print_status(message, status):
    """Print colored status message"""
    colors = {
        'ok': '\033[92m',      # Green
        'warning': '\033[93m',  # Yellow
        'error': '\033[91m',    # Red
        'info': '\033[94m',     # Blue
        'end': '\033[0m'        # Reset
    }
    
    symbol = {
        'ok': '✅',
        'warning': '⚠️ ',
        'error': '❌',
        'info': 'ℹ️ '
    }
    
    print(f"{colors[status]}{symbol[status]} {message}{colors['end']}")


def test_python_version():
    """Test Python version"""
    print("\n" + "="*70)
    print("📋 Testing Python Version")
    print("="*70)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 10:
        print_status(f"Python {version_str} - Compatible", 'ok')
        return True
    else:
        print_status(f"Python {version_str} - Need 3.10+", 'error')
        return False


def test_imports():
    """Test required Python packages"""
    print("\n" + "="*70)
    print("📦 Testing Python Packages")
    print("="*70)
    
    packages = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'yfinance': 'yfinance',
        'google.auth': 'google-auth',
        'google.oauth2': 'google-auth-oauthlib',
        'googleapiclient': 'google-api-python-client',
        'kaggle': 'kaggle',
        'dotenv': 'python-dotenv'
    }
    
    all_ok = True
    for module, package in packages.items():
        try:
            __import__(module)
            print_status(f"{package} - Installed", 'ok')
        except ImportError:
            print_status(f"{package} - Missing (pip install {package})", 'error')
            all_ok = False
    
    return all_ok


def test_credentials():
    """Test credential files"""
    print("\n" + "="*70)
    print("🔐 Testing Credentials")
    print("="*70)
    
    files = {
        'credentials.json': 'Google Drive OAuth credentials',
        'kaggle.json': 'Kaggle API token',
        '.env': 'Environment variables'
    }
    
    all_ok = True
    for filename, description in files.items():
        if os.path.exists(filename):
            print_status(f"{filename} - Found ({description})", 'ok')
            
            # Validate JSON files
            if filename.endswith('.json'):
                try:
                    with open(filename, 'r') as f:
                        json.load(f)
                    print_status(f"  └─ Valid JSON format", 'info')
                except json.JSONDecodeError:
                    print_status(f"  └─ Invalid JSON format!", 'error')
                    all_ok = False
        else:
            print_status(f"{filename} - Missing ({description})", 'warning')
            all_ok = False
    
    # Check Kaggle in home directory
    kaggle_home = os.path.expanduser('~/.kaggle/kaggle.json')
    if os.path.exists(kaggle_home):
        print_status(f"~/.kaggle/kaggle.json - Found (alternative location)", 'ok')
        # Check permissions
        stat = os.stat(kaggle_home)
        if oct(stat.st_mode)[-3:] == '600':
            print_status(f"  └─ Correct permissions (600)", 'info')
        else:
            print_status(f"  └─ Wrong permissions. Run: chmod 600 {kaggle_home}", 'warning')
    
    return all_ok


def test_github_config():
    """Test GitHub configuration"""
    print("\n" + "="*70)
    print("🐙 Testing GitHub Configuration")
    print("="*70)
    
    all_ok = True
    
    # Check git installed
    if os.system('git --version > /dev/null 2>&1') == 0:
        print_status("Git - Installed", 'ok')
    else:
        print_status("Git - Not installed", 'error')
        return False
    
    # Check git config
    user_name = os.popen('git config user.name').read().strip()
    user_email = os.popen('git config user.email').read().strip()
    
    if user_name:
        print_status(f"Git user.name: {user_name}", 'info')
    else:
        print_status("Git user.name not configured", 'warning')
    
    if user_email:
        print_status(f"Git user.email: {user_email}", 'info')
    else:
        print_status("Git user.email not configured", 'warning')
    
    # Check if in a git repo
    if os.path.exists('.git'):
        print_status("Git repository - Initialized", 'ok')
        
        # Check remote
        remote = os.popen('git remote get-url origin 2>/dev/null').read().strip()
        if remote:
            print_status(f"Remote origin: {remote}", 'info')
        else:
            print_status("No remote origin configured", 'warning')
    else:
        print_status("Not a git repository", 'warning')
    
    return all_ok


def test_kaggle_cli():
    """Test Kaggle CLI"""
    print("\n" + "="*70)
    print("🏆 Testing Kaggle CLI")
    print("="*70)
    
    if os.system('kaggle --version > /dev/null 2>&1') == 0:
        version = os.popen('kaggle --version').read().strip()
        print_status(f"Kaggle CLI - Installed ({version})", 'ok')
        
        # Try to list datasets (test authentication)
        result = os.system('kaggle datasets list --max-size 1 > /dev/null 2>&1')
        if result == 0:
            print_status("Kaggle authentication - Working", 'ok')
            return True
        else:
            print_status("Kaggle authentication - Failed", 'error')
            print_status("  └─ Check kaggle.json credentials", 'info')
            return False
    else:
        print_status("Kaggle CLI - Not installed (pip install kaggle)", 'error')
        return False


def test_files():
    """Test required files"""
    print("\n" + "="*70)
    print("📄 Testing Required Files")
    print("="*70)
    
    files = {
        'main_chunk_kaggle.py': 'Main script',
        'Forrest.ipynb': 'ML notebook template',
        'requirements.txt': 'Python dependencies',
        'setup.sh': 'Setup script',
        '.env.example': 'Environment template'
    }
    
    all_ok = True
    for filename, description in files.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print_status(f"{filename} - Found ({description}, {size} bytes)", 'ok')
        else:
            print_status(f"{filename} - Missing ({description})", 'warning')
            all_ok = False
    
    return all_ok


def test_github_actions():
    """Test GitHub Actions workflow"""
    print("\n" + "="*70)
    print("⚙️  Testing GitHub Actions")
    print("="*70)
    
    workflow_path = '.github/workflows/daily_data_pipeline.yml'
    
    if os.path.exists(workflow_path):
        print_status(f"{workflow_path} - Found", 'ok')
        
        with open(workflow_path, 'r') as f:
            content = f.read()
            if 'schedule' in content and 'cron' in content:
                print_status("  └─ Scheduled workflow configured", 'info')
            if 'workflow_dispatch' in content:
                print_status("  └─ Manual trigger enabled", 'info')
        
        return True
    else:
        print_status(f"{workflow_path} - Missing", 'warning')
        return False


def print_summary(results):
    """Print test summary"""
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    total = len(results)
    passed = sum(results.values())
    
    for test_name, result in results.items():
        status = 'ok' if result else 'error'
        print_status(f"{test_name}: {'PASS' if result else 'FAIL'}", status)
    
    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print_status("\n🎉 All tests passed! System ready.", 'ok')
    else:
        print_status(f"\n⚠️  {total - passed} test(s) failed. Check errors above.", 'warning')
    
    print("="*70 + "\n")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 SYSTEM CONFIGURATION TEST")
    print("="*70)
    
    results = {
        'Python Version': test_python_version(),
        'Python Packages': test_imports(),
        'Credentials': test_credentials(),
        'GitHub Config': test_github_config(),
        'Kaggle CLI': test_kaggle_cli(),
        'Required Files': test_files(),
        'GitHub Actions': test_github_actions()
    }
    
    print_summary(results)
    
    # Exit with error if any test failed
    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
