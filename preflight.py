#!/usr/bin/env python3
"""
Quick Pre-flight Check - Verify system before execution
Run this before executing main_chunk_kaggle.py
"""

import os
import sys
import json

def check(condition, message):
    """Print check result"""
    if condition:
        print(f"✅ {message}")
        return True
    else:
        print(f"❌ {message}")
        return False

def main():
    print("\n" + "="*70)
    print("🔍 PRE-FLIGHT CHECK")
    print("="*70 + "\n")
    
    checks = []
    
    # 1. Python version
    print("📋 Python:")
    checks.append(check(
        sys.version_info >= (3, 10),
        f"Python {sys.version_info.major}.{sys.version_info.minor} (need 3.10+)"
    ))
    
    # 2. Required files
    print("\n📄 Required Files:")
    checks.append(check(
        os.path.exists('main_chunk_kaggle.py'),
        "main_chunk_kaggle.py exists"
    ))
    checks.append(check(
        os.path.exists('Forrest.ipynb'),
        "Forrest.ipynb exists"
    ))
    checks.append(check(
        os.path.exists('requirements.txt'),
        "requirements.txt exists"
    ))
    
    # 3. Credentials
    print("\n🔐 Credentials:")
    checks.append(check(
        os.path.exists('credentials.json'),
        "credentials.json exists (Google Drive)"
    ))
    checks.append(check(
        os.path.exists(os.path.expanduser('~/.kaggle/kaggle.json')) or os.path.exists('kaggle.json'),
        "kaggle.json exists (Kaggle API)"
    ))
    
    # Validate JSON files
    if os.path.exists('credentials.json'):
        try:
            with open('credentials.json', 'r') as f:
                data = json.load(f)
            checks.append(check(
                'web' in data or 'installed' in data,
                "credentials.json is valid"
            ))
        except:
            checks.append(check(False, "credentials.json is valid JSON"))
    
    if os.path.exists('kaggle.json'):
        try:
            with open('kaggle.json', 'r') as f:
                data = json.load(f)
            checks.append(check(
                'username' in data and 'key' in data,
                "kaggle.json is valid"
            ))
        except:
            checks.append(check(False, "kaggle.json is valid JSON"))
    
    # 4. Python packages
    print("\n📦 Python Packages:")
    packages = ['pandas', 'yfinance', 'google.auth', 'kaggle']
    for pkg in packages:
        try:
            __import__(pkg)
            checks.append(check(True, f"{pkg} installed"))
        except ImportError:
            checks.append(check(False, f"{pkg} installed (pip install {pkg})"))
    
    # 5. Git
    print("\n🐙 Git:")
    checks.append(check(
        os.system('git --version > /dev/null 2>&1') == 0,
        "git is installed"
    ))
    
    if os.path.exists('.git'):
        checks.append(check(True, "git repository initialized"))
        
        remote = os.popen('git remote get-url origin 2>/dev/null').read().strip()
        checks.append(check(
            bool(remote),
            f"git remote configured"
        ))
    
    # 6. Environment
    print("\n⚙️  Environment:")
    checks.append(check(
        os.path.exists('.env') or os.path.exists('.env.example'),
        ".env or .env.example exists"
    ))
    
    # Summary
    print("\n" + "="*70)
    total = len(checks)
    passed = sum(checks)
    
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("="*70)
        print("\n🚀 You can now run: python3 main_chunk_kaggle.py")
        return 0
    else:
        print(f"⚠️  {total - passed} CHECKS FAILED ({passed}/{total} passed)")
        print("="*70)
        print("\n📝 Fix the issues above before running the main script")
        print("\n💡 Quick fixes:")
        print("   • Missing files: Copy from the project directory")
        print("   • Credentials: Run 'python3 setup_credentials.py'")
        print("   • Packages: Run 'pip install -r requirements.txt'")
        print("   • Git: Run 'git init' and configure remote")
        return 1

if __name__ == "__main__":
    sys.exit(main())
