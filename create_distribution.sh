#!/bin/bash

echo "========================================"
echo "Thin Film Analyzer - Distribution Package Creator"
echo "========================================"
echo ""

# Set version
VERSION="2.2.1"

# Create distribution folder name
DIST_FOLDER="ThinFilmAnalyzer_v${VERSION}"

echo "Creating distribution folder: $DIST_FOLDER"
echo ""

# Check if distribution folder already exists
if [ -d "$DIST_FOLDER" ]; then
    echo "WARNING: Distribution folder already exists."
    read -p "Press Ctrl+C to cancel or Enter to continue..."
    echo "Removing old distribution folder..."
    rm -rf "$DIST_FOLDER"
fi

# Create main distribution folder
mkdir -p "$DIST_FOLDER"

echo "Copying application files..."

# Copy main application folder
cp -R thin_film_analyzer "$DIST_FOLDER/"

# Copy shell scripts
cp install.sh "$DIST_FOLDER/"
cp run_app.sh "$DIST_FOLDER/"

# Make scripts executable
chmod +x "$DIST_FOLDER/install.sh"
chmod +x "$DIST_FOLDER/run_app.sh"

# Copy documentation
cp README.md "$DIST_FOLDER/"
cp INSTALLATION_GUIDE.md "$DIST_FOLDER/"
cp USER_GUIDE.md "$DIST_FOLDER/"
cp requirements.txt "$DIST_FOLDER/"

# Optional: Copy diagnostic scripts
echo ""
read -p "Include diagnostic scripts (diagnose_threshold.py, analyze_images.py)? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f diagnose_threshold.py ]; then
        cp diagnose_threshold.py "$DIST_FOLDER/" 2>/dev/null || echo "diagnose_threshold.py not found"
    fi
    if [ -f analyze_images.py ]; then
        cp analyze_images.py "$DIST_FOLDER/" 2>/dev/null || echo "analyze_images.py not found"
    fi
    echo "Diagnostic scripts included."
else
    echo "Diagnostic scripts skipped."
fi

# Clean up __pycache__ folders
echo ""
echo "Cleaning up Python cache files..."
find "$DIST_FOLDER" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$DIST_FOLDER" -type f -name "*.pyc" -delete 2>/dev/null

echo ""
echo "========================================"
echo "Distribution package created successfully!"
echo "========================================"
echo ""
echo "Folder: $DIST_FOLDER"
echo ""
echo "Next steps:"
echo "1. Review the contents of $DIST_FOLDER"
echo "2. Test on a clean machine if possible"
echo "3. Compress to ZIP or TAR.GZ file:"
echo "   zip -r ${DIST_FOLDER}.zip $DIST_FOLDER"
echo "   or"
echo "   tar -czf ${DIST_FOLDER}.tar.gz $DIST_FOLDER"
echo "4. Share with your team members"
echo ""
