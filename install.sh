#!/bin/bash

echo "========================================"
echo "Thin Film Analyzer v2.2.1 - Installation"
echo "========================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo ""
    echo "Please install Python 3.10 or higher:"
    echo "  macOS: brew install python@3.10"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo ""
    echo "Or download from: https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python found: $PYTHON_VERSION"
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    echo "Please install pip3 for your system"
    exit 1
fi

echo "Installing required packages..."
echo "This may take 2-5 minutes depending on your internet connection"
echo ""

# Upgrade pip first
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies from requirements.txt
echo ""
echo "Installing required packages from requirements.txt..."
pip3 install -r requirements.txt

echo ""
echo "========================================"
echo "Installation complete!"
echo "========================================"
echo ""
echo "To run the application:"
echo "  ./run_app.sh"
echo ""
echo "If you get 'Permission denied', run:"
echo "  chmod +x run_app.sh"
echo ""
