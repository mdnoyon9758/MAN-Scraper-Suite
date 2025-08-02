@echo off
REM MAN Scraper Suite Installation Script for Windows
REM 100% Free Web Scraping & Automation Toolkit

echo 🔥 MAN Scraper Suite Installation Script
echo ======================================
echo Installing 100% Free Web Scraping & Automation Toolkit
echo No limits, no paywalls, all premium features unlocked!
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found Python %PYTHON_VERSION%

REM Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available
    echo Installing pip...
    python -m ensurepip --upgrade
)

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo [INFO] Installing MAN Scraper Suite...
if exist setup.py (
    echo [INFO] Installing in development mode...
    python -m pip install -e .
) else (
    echo [INFO] Installing from PyPI...
    python -m pip install manscrapersuite
)

echo [INFO] Installing GUI dependencies...
python -m pip install "manscrapersuite[gui]"

echo [INFO] Installing Playwright browsers...
python -m playwright install

echo [INFO] Testing installation...
python -c "import manscrapersuite; print('✓ MAN Scraper Suite imported successfully')"
if %errorlevel% neq 0 (
    echo [ERROR] Installation test failed
    pause
    exit /b 1
)

echo.
echo 🎉 Installation Complete!
echo.
echo MAN Scraper Suite has been successfully installed!
echo 100%% Free - No Limits - All Features Unlocked
echo.
echo Quick Start:
echo   CLI: manscrapersuite --help
echo   GUI: manscrapersuite-gui
echo   Python: python -c "import manscrapersuite; manscrapersuite.print_banner()"
echo.
echo Documentation: https://manscrapersuite.readthedocs.io/
echo Repository: https://github.com/manscrapersuite/manscrapersuite
echo.
echo 🚀 Happy Scraping!
echo.
pause
