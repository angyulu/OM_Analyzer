# Thin Film Coverage Analyzer

Desktop application for automated thin film coverage analysis from optical microscope images.

## Features

**Current Version: 2.0.0**

- ✅ Single image loading via drag-drop or file browser
- ✅ **Adaptive threshold algorithm** for vignetting correction (NEW!)
- ✅ Batch image navigation with Previous/Next buttons (NEW!)
- ✅ Real-time parameter tuning with instant visual feedback (NEW!)
- ✅ Local background subtraction for uniform detection across image (NEW!)
- ✅ Real-time visual overlay with adjustable transparency
- ✅ Coverage percentage and processing time display
- ✅ Multiple threshold methods: Adaptive (default), Otsu, Manual
- ✅ Morphological operations for noise cleanup
- ✅ Noise reduction preprocessing (Gaussian blur)
- ✅ ROI support for focused analysis
- ✅ Multiple file format support (TIFF, PNG, JPG, BMP)

**Planned Features:**

- Scale calibration for absolute area (µm²) measurements
- CSV export of batch results
- Statistics and histogram analysis

## Installation

### For Team Members (Non-Programmers)

If you're receiving this application and need to use it without programming:

1. **Read [SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions for non-programmers
2. **Run `install.bat`** - Installs Python and all required packages
3. **Run `run_app.bat`** - Launches the application

That's it! See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions and troubleshooting.

### For Developers

#### Prerequisites

- Python 3.8 or higher
- Windows 10/11 (primary) or macOS/Linux (secondary)

#### Setup

1. Clone or download this repository:
```bash
cd OM_Analyzer/OM_V0
```

2. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Verify installation:
```bash
python -c "import PyQt6, cv2, numpy, PIL; print('All dependencies installed successfully!')"
```

## Running the Application

### Simple Method (Windows)

```bash
# Double-click run_app.bat
# OR from command line:
run_app.bat
```

### Command Line Method

```bash
python thin_film_analyzer/main.py
```

### First Launch

On first launch, the application will display the main window with:
- Adaptive threshold enabled by default
- Optimal parameters pre-configured (Block Size: 200, C Value: 5)
- Ready to load images

## Usage

### Basic Workflow

1. **Load Image:**
   - Click "Load Image" button or use File > Open Image (Ctrl+O)
   - Supported formats: TIFF, PNG, JPG, BMP
   - The image will be automatically processed with default settings

2. **View Results:**
   - Coverage percentage is displayed at the top
   - Processing time shown below coverage
   - Red overlay shows detected flake regions

3. **Navigate Multiple Images:**
   - Click "Previous" or "Next" to process other images in the same folder
   - Each image is processed with current parameter settings

4. **Tune Detection (if needed):**
   - **Adaptive C (default: 5):** Lower to detect thinner flakes, higher for only thick flakes
   - **Adaptive Block Size (default: 200):** Size of local region for background estimation
   - **Blur Kernel:** Increase for more noise reduction
   - **Morphological Close/Open:** Adjust to clean up small holes or noise
   - All parameters update in real-time

5. **Alternative Threshold Methods:**
   - Uncheck "Use Adaptive Threshold" to use Otsu or Manual threshold
   - Adjust "Threshold" slider for manual control
   - Note: Global threshold may not work well with vignetting

### Keyboard Shortcuts

- `Ctrl+O`: Open image
- `Ctrl+Q`: Exit application

### Understanding the Algorithm

The application uses **adaptive threshold with local background subtraction**:

1. Calculates local background (vignetting removal)
2. Subtracts background from image (flakes become positive values)
3. Detects pixels brighter than local background by at least C value
4. Applies morphological cleanup

This approach handles **vignetting** (darker edges, brighter center) that causes problems with global thresholding.

### Diagnostic Scripts

Run diagnostic scripts to analyze images:

```bash
# Analyze vignetting and threshold issues
python diagnose_threshold.py

# Detailed image statistics and brightness analysis
python analyze_images.py
```

These scripts help understand image characteristics and optimal parameter settings.

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'PyQt6'"

**Solution:** Run `install.bat` to install all dependencies
```bash
# Windows
install.bat

# OR manually
pip install -r requirements.txt
```

### Issue: Application window doesn't open

**Solution:** Check Python version and Qt installation
```bash
python --version  # Should be 3.8+
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

### Issue: "Unable to load image" error

**Solution:** Application uses PIL/Pillow for TIFF fallback. Verify:
- Supported formats: TIFF, TIF, PNG, JPG, JPEG, BMP
- File is not corrupted (try opening in another application)
- File path does not contain special characters

### Issue: Parameters not updating in real-time

**Solution:** Make sure "Use Adaptive Threshold" is checked and an image is loaded. All parameters should update immediately when changed.

### Issue: Detection missing flakes or detecting too much

**Solution:**
- **Missing flakes:** Lower "Adaptive C" value (try 3-5)
- **Over-detection:** Raise "Adaptive C" value (try 10-15)
- **Vignetting problems:** Ensure "Use Adaptive Threshold" is enabled
- Adjust "Adaptive Block Size" to be larger than your largest flake

## Project Structure

```
thin_film_analyzer/
├── main.py                  # Application entry point
├── ui/                      # PyQt6 user interface
│   ├── main_window.py       # Main application window
│   ├── image_viewer.py      # Image display with overlay
│   ├── widgets.py           # Custom UI widgets
│   ├── results_table.py     # Results display
│   └── dialogs.py           # Confirmation dialogs
├── core/                    # Business logic
│   ├── processor.py         # Image processing pipeline
│   ├── detection.py         # Thin film detection algorithms
│   ├── overlay.py           # Overlay generation
│   ├── settings.py          # Settings persistence
│   ├── logger.py            # Error logging
│   ├── calibration.py       # Scale management
│   └── export.py            # CSV export
├── models/                  # Data entities
│   ├── image.py
│   ├── detection_result.py
│   ├── scale_preset.py
│   ├── batch_session.py
│   └── app_settings.py
├── config/                  # Configuration
│   └── defaults.py          # Default settings
├── tests/                   # Test suite
│   ├── unit/
│   ├── integration/
│   └── synthetic/           # Synthetic test images
└── resources/               # Icons and styles
```

## Algorithm Details

### Why Adaptive Threshold?

Optical microscopy images often suffer from **vignetting** - darker edges and brighter center due to optical effects. With a single global threshold:

- **Lower threshold:** Detects corner flakes BUT creates false-positive circle in center
- **Higher threshold:** Eliminates center circle BUT misses corner flakes

**Solution:** Adaptive threshold with local background subtraction removes vignetting effect by normalizing each pixel against its local neighborhood.

### Detection Philosophy

The algorithm detects ALL flakes, from thinnest to thickest:

- **Substrate:** Uniform brightness (after vignetting correction)
- **Thin flakes:** Slightly brighter than substrate (first histogram peak after substrate)
- **Thick flakes:** Much brighter than substrate (subsequent histogram peaks)

The **adaptive_c** parameter represents the minimum brightness difference between substrate and the thinnest detectable flakes.

### Algorithm Steps

1. **Load image** - Support for TIFF, PNG, JPG, BMP (PIL fallback for TIFF)
2. **Convert to grayscale** - Single channel processing
3. **Noise reduction** - Optional Gaussian blur
4. **Local background estimation** - Gaussian blur with large kernel (adaptive_block_size)
5. **Background subtraction** - `diff = image - local_mean` (flakes become positive, substrate ≈ 0)
6. **Threshold** - Detect pixels where `diff > adaptive_c`
7. **Morphological operations** - Clean up noise and small holes
8. **Coverage calculation** - Count detected pixels vs total pixels

## Performance

- **Single Image Processing:** <1 second for 2048×2048 images
- **Real-time Updates:** All parameters update instantly
- **Memory Usage:** Optimized with uint8 data types throughout pipeline

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review error logs in the settings directory
3. Report issues with diagnostic information

## License

Internal research tool - All rights reserved

## Version History

### v2.0.0 - Current
- **Adaptive threshold with local background subtraction** (solves vignetting)
- Real-time parameter tuning
- Batch image navigation (Previous/Next)
- Multiple threshold methods (Adaptive, Otsu, Manual)
- Morphological operations
- Coverage and processing time display
- Multi-format support with PIL fallback

### v1.0.0 (MVP)
- Initial release with basic threshold detection
- Single image analysis
- Manual threshold adjustment

### Planned Releases
- v2.1.0: CSV export for batch results
- v2.2.0: Scale calibration and area measurements
- v2.3.0: Statistics and histogram analysis
