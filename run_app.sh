#!/bin/bash

echo "Starting Thin Film Analyzer v2.1.1..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please run install.sh first or follow INSTALLATION_GUIDE.md"
    exit 1
fi

# Run the application
python3 thin_film_analyzer/main.py

# If the application exits with an error
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "Application exited with an error"
    echo "========================================"
    echo ""
    echo "If you see 'No module named...' errors, run ./install.sh"
    echo ""
fi
