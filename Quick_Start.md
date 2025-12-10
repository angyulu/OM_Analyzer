# Quick Start Guide

**Get up and running with the Thin Film Coverage Analyzer in 5 minutes.**

---

## 🚀 Installation (2 minutes)

### Prerequisites
- Python 3.10 or higher
- Windows 10/11 (primary) or macOS 11+ (secondary)

### Setup Steps

```bash
# 1. Navigate to project directory
cd OM_Analyzer/OM_V0

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python -c "import PyQt6, cv2, skimage; print('✓ Installation successful!')"
```

---

## ▶️ Run the Application (30 seconds)

```bash
python thin_film_analyzer/main.py
```

**Expected Output:**
```
Thin Film Analyzer v1.0.0
Settings directory: C:\Users\<username>\AppData\Roaming\ThinFilmAnalyzer
Loading settings from: C:\Users\<username>\AppData\Roaming\ThinFilmAnalyzer\settings.json
Application started successfully.
```

---

## 🎯 First Analysis (2 minutes)

### Step 1: Generate Test Images

```bash
python thin_film_analyzer/tests/synthetic/generate_test_images.py
```

This creates three synthetic test images with known coverage (25%, 50%, 75%).

### Step 2: Analyze an Image

1. **Load Image:**
   - Drag and drop `coverage_50pct.png` onto the application window
   - OR click `File > Open Image` (Ctrl+O)

2. **Process Image:**
   - Click the **"Process Image"** button
   - The coverage percentage appears in the Results panel (~50%)

3. **Verify Detection:**
   - Check the **"Show Overlay"** checkbox
   - Red overlay highlights detected thin film regions
   - Adjust **"Overlay Transparency"** slider to see original image beneath

4. **Fine-Tune (Optional):**
   - Adjust **"Threshold"** slider (0-255) to refine detection
   - Image reprocesses automatically with each adjustment
   - Toggle **"Enable Noise Reduction"** to see the effect

### Step 3: Verify Accuracy

Expected results for synthetic images:
- `coverage_25pct.png` → ~25% coverage
- `coverage_50pct.png` → ~50% coverage
- `coverage_75pct.png` → ~75% coverage

---

## 📂 Project Structure

```
thin_film_analyzer/
├── main.py                  # ← START HERE: Run this file
├── ui/                      # PyQt6 user interface
│   └── main_window.py       # Main application window
├── core/                    # Image processing logic
│   ├── processor.py         # Main processing pipeline
│   ├── detection.py         # Threshold-based detection
│   └── overlay.py           # Overlay generation
├── models/                  # Data models
│   ├── image.py
│   └── detection_result.py
├── config/                  # Configuration
│   └── defaults.py          # Default settings
└── tests/
    └── synthetic/           # Test image generator
```

---

## ⚙️ Current Features (MVP v1.0.0)

✅ **Implemented:**
- Single image loading (drag-drop or file browser)
- Automatic thin film detection (Otsu thresholding)
- Visual verification overlay (red mask, adjustable transparency)
- Manual threshold adjustment (0-255 slider)
- Coverage percentage calculation
- Noise reduction preprocessing
- Settings persistence

🔜 **Coming Soon:**
- Scale calibration for absolute area (µm²) measurements
- Batch processing of multiple images
- CSV export with summary statistics
- ROI selection for scale bar exclusion

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'PyQt6'"
**Solution:** Activate virtual environment and reinstall dependencies
```bash
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Issue: Application window doesn't appear
**Solution:** Check Python version
```bash
python --version  # Should be 3.10+
```

### Issue: "Unable to load image" error
**Solution:** Verify image format is supported (PNG, JPG, JPEG, TIFF, TIF, BMP)

---

## 📚 Next Steps

- **Full Doc/umentation:** See [README.md](README.md) for detailed usage/
- **Developer Guide:** See [specs/001-thin-film-analyzer/quickstart.md](specs/001-thin-film-analyzer/quickstart.md)
- **Architecture:** See [specs/001-thin-film-analyzer/plan.md](specs/001-thin-film-analyzer/plan.md)
- **Tasks:** See [specs/001-thin-film-analyzer/tasks.md](specs/001-thin-film-analyzer/tasks.md)

---

## 🎉 Success!

You're now ready to analyze optical microscope images with automated thin film detection and visual verification!

**Keyboard Shortcuts:**
- `Ctrl+O` - Open image
- `Ctrl+Q` - Exit application

**Settings Location:**
- Windows: `%APPDATA%\ThinFilmAnalyzer\settings.json`
- macOS: `~/.config/ThinFilmAnalyzer/settings.json`
