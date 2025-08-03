#!/usr/bin/env python3
"""
Termux Installation Script for MAN Suite
Optimized for Android environments
"""

import subprocess
import sys
import os
import platform

def install_termux_packages():
    """Install required Termux packages"""
    print("📱 Installing Termux system packages...")
    termux_packages = [
        "python",
        "python-dev", 
        "clang",
        "make",
        "pkg-config",
        "libxml2-dev",
        "libxslt-dev",
        "libjpeg-turbo-dev",
        "libpng-dev",
        "freetype-dev"
    ]
    
    try:
        for package in termux_packages:
            print(f"Installing {package}...")
            subprocess.run(["pkg", "install", "-y", package], check=True)
        print("✅ Termux packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Termux packages: {e}")
        return False
    except FileNotFoundError:
        print("⚠️  Not running in Termux environment")
        return True  # Continue anyway

def install_python_requirements():
    """Install Python requirements for Termux"""
    try:
        print("📦 Installing Python dependencies (Termux optimized)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-termux.txt"])
        print("✅ Python dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False

def setup_termux_environment():
    """Setup Termux-specific environment"""
    print("🔧 Setting up Termux environment...")
    
    # Create necessary directories
    os.makedirs(os.path.expanduser("~/.config/manscrapersuite"), exist_ok=True)
    
    # Set environment variables for Termux
    termux_env = """
# MAN Suite Termux Environment
export TERMUX_MODE=1
export SCRAPY_SETTINGS_MODULE=manscrapersuite.settings.termux
export PYTHONPATH=$PYTHONPATH:$HOME/MAN-Scraper-Suite
"""
    
    bashrc_path = os.path.expanduser("~/.bashrc")
    try:
        with open(bashrc_path, "a") as f:
            f.write(termux_env)
        print("✅ Environment configured!")
    except Exception as e:
        print(f"⚠️  Could not update .bashrc: {e}")
    
    return True

def main():
    """Main installation function for Termux"""
    print("📱 MAN Suite - Termux Installation")
    print("=" * 50)
    
    # Check if running on Android/Termux
    is_termux = "TERMUX_VERSION" in os.environ or "com.termux" in os.environ.get("PREFIX", "")
    
    if is_termux:
        print("✅ Termux environment detected")
    else:
        print("⚠️  Not detected as Termux, but proceeding...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version} detected")
    
    # Install Termux packages (if in Termux)
    if is_termux:
        if not install_termux_packages():
            print("❌ Failed to install system packages")
            sys.exit(1)
    
    # Install Python requirements
    if not install_python_requirements():
        print("❌ Installation failed")
        sys.exit(1)
    
    # Setup environment
    setup_termux_environment()
    
    print("\n🎉 Termux installation complete!")
    print("\n📱 Termux Quick Start:")
    print("   python man.py --help")
    print("   python -m manscrapersuite.cli --help")
    print("\n💡 Termux Notes:")
    print("   • Lighter functionality (no Selenium/Playwright)")
    print("   • Uses requests + BeautifulSoup for scraping")
    print("   • Google Sheets export supported")
    print("   • Perfect for basic web scraping on mobile")

if __name__ == "__main__":
    main()
