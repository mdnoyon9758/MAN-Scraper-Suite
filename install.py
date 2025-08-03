#!/usr/bin/env python3
"""
Simple Installation Script for MAN Suite
"""

import subprocess
import sys
import os

def install_requirements():
    """Install requirements from requirements.txt"""
    try:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def main():
    """Main installation function"""
    print("🔥 MAN Suite Installation")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version} detected")
    
    # Install requirements
    if install_requirements():
        print("\n🎉 Installation complete!")
        print("\n🚀 Quick start:")
        print("   python man.py --help")
        print("   python -m manscrapersuite.cli --help")
    else:
        print("\n❌ Installation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
