@echo off
echo ========================================
echo Thin Film Analyzer - Dependency Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python first:
    echo 1. Go to https://www.python.org/downloads/
    echo 2. Download and install Python
    echo 3. Make sure to check "Add Python to PATH" during installation
    echo 4. Run this script again after installation
    echo.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    echo Please reinstall Python and ensure pip is included
    echo.
    pause
    exit /b 1
)

echo Installing required packages...
echo This may take 2-5 minutes depending on your internet connection
echo.

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies from requirements.txt
echo.
echo Installing required packages from requirements.txt...
pip install -r requirements.txt

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo You can now run the application by double-clicking "run_app.bat"
echo.
pause
