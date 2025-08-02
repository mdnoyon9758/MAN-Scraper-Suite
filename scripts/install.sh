#!/bin/bash
# MAN Scraper Suite Installation Script
# 100% Free Web Scraping & Automation Toolkit

set -e

echo "🔥 MAN Scraper Suite Installation Script"
echo "======================================"
echo "Installing 100% Free Web Scraping & Automation Toolkit"
echo "No limits, no paywalls, all premium features unlocked!"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Python 3.10+ is installed
check_python() {
    print_header "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status "Found Python $PYTHON_VERSION"
        
        # Check if version is 3.10 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
            print_status "Python version is compatible ✓"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.10+ is required. Current version: $PYTHON_VERSION"
            print_status "Please install Python 3.10 or higher from https://python.org"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        print_status "Please install Python 3.10+ from https://python.org"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_header "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        print_status "pip3 found ✓"
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        print_status "pip found ✓"
        PIP_CMD="pip"
    else
        print_error "pip is not installed"
        print_status "Installing pip..."
        $PYTHON_CMD -m ensurepip --upgrade
        PIP_CMD="pip3"
    fi
}

# Install system dependencies
install_system_deps() {
    print_header "Installing system dependencies..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            print_status "Detected Ubuntu/Debian system"
            sudo apt-get update
            sudo apt-get install -y python3-dev python3-pip build-essential libssl-dev libffi-dev
        elif command -v yum &> /dev/null; then
            print_status "Detected CentOS/RHEL system"
            sudo yum install -y python3-devel python3-pip gcc openssl-devel libffi-devel
        elif command -v pacman &> /dev/null; then
            print_status "Detected Arch Linux system"
            sudo pacman -S --noconfirm python-pip base-devel openssl libffi
        else
            print_warning "Unknown Linux distribution. You may need to install dependencies manually."
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_status "Detected macOS system"
        if command -v brew &> /dev/null; then
            brew install python@3.11 || true
        else
            print_warning "Homebrew not found. Consider installing it from https://brew.sh"
        fi
    else
        print_warning "Unknown operating system. Proceeding with Python package installation..."
    fi
}

# Install Playwright browsers
install_playwright() {
    print_header "Installing Playwright browsers..."
    
    print_status "Installing Playwright browser dependencies..."
    $PYTHON_CMD -m playwright install
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Installing Playwright system dependencies..."
        $PYTHON_CMD -m playwright install-deps
    fi
}

# Install MAN Scraper Suite
install_manscrapersuite() {
    print_header "Installing MAN Scraper Suite..."
    
    # Upgrade pip first
    print_status "Upgrading pip..."
    $PIP_CMD install --upgrade pip
    
    # Install from current directory (development mode)
    if [ -f "setup.py" ]; then
        print_status "Installing MAN Scraper Suite in development mode..."
        $PIP_CMD install -e .
    else
        print_status "Installing MAN Scraper Suite from PyPI..."
        $PIP_CMD install manscrapersuite
    fi
    
    # Install optional dependencies for GUI
    print_status "Installing GUI dependencies..."
    $PIP_CMD install "manscrapersuite[gui]" || print_warning "GUI dependencies installation failed (optional)"
    
    # Install Playwright browsers
    install_playwright
}

# Create desktop shortcut (Linux)
create_desktop_shortcut() {
    if [[ "$OSTYPE" == "linux-gnu"* ]] && [ -d "$HOME/Desktop" ]; then
        print_header "Creating desktop shortcut..."
        
        cat > "$HOME/Desktop/MAN_Scraper_Suite.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=MAN Scraper Suite
Comment=100% Free Web Scraping & Automation Toolkit
Exec=$PYTHON_CMD -m manscrapersuite.gui.main
Icon=applications-internet
Terminal=false
Categories=Development;Network;
EOF
        
        chmod +x "$HOME/Desktop/MAN_Scraper_Suite.desktop"
        print_status "Desktop shortcut created ✓"
    fi
}

# Test installation
test_installation() {
    print_header "Testing installation..."
    
    print_status "Testing CLI..."
    if $PYTHON_CMD -c "import manscrapersuite; print('✓ MAN Scraper Suite imported successfully')"; then
        print_status "CLI test passed ✓"
    else
        print_error "CLI test failed"
        exit 1
    fi
    
    print_status "Testing version..."
    if $PYTHON_CMD -c "import manscrapersuite; print(f'Version: {manscrapersuite.__version__}')"; then
        print_status "Version test passed ✓"
    else
        print_warning "Version test failed (non-critical)"
    fi
}

# Main installation process
main() {
    print_header "🔥 Starting MAN Scraper Suite Installation"
    echo ""
    
    check_python
    check_pip
    install_system_deps
    install_manscrapersuite
    create_desktop_shortcut
    test_installation
    
    echo ""
    print_header "🎉 Installation Complete!"
    echo ""
    print_status "MAN Scraper Suite has been successfully installed!"
    print_status "100% Free - No Limits - All Features Unlocked"
    echo ""
    print_status "Quick Start:"
    echo "  CLI: manscrapersuite --help"
    echo "  GUI: manscrapersuite-gui"
    echo "  Python: python3 -c 'import manscrapersuite; manscrapersuite.print_banner()'"
    echo ""
    print_status "Documentation: https://manscrapersuite.readthedocs.io/"
    print_status "Repository: https://github.com/manscrapersuite/manscrapersuite"
    echo ""
    print_status "🚀 Happy Scraping!"
}

# Handle script interruption
trap 'print_error "Installation interrupted"; exit 1' INT TERM

# Run main installation
main
