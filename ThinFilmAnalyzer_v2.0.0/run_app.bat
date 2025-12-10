@echo off
echo Starting Thin Film Analyzer...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run install.bat first or follow SETUP_GUIDE.md
    echo.
    pause
    exit /b 1
)

REM Run the application
python thin_film_analyzer/main.py

REM If the application exits with an error, keep the window open
if errorlevel 1 (
    echo.
    echo ========================================
    echo Application exited with an error
    echo ========================================
    echo.
    echo If you see "No module named..." errors, run install.bat
    echo.
    pause
)
