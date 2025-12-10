# Thin Film Analyzer - User Guide

## Overview

The Thin Film Analyzer is a desktop application that automatically detects and quantifies thin film flakes in optical microscopy images. It uses advanced adaptive threshold algorithms to handle uneven illumination (vignetting) and provides real-time parameter tuning.

## Installation (One-Time Setup)

### Step 1: Install Python

1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **⚠️ CRITICAL:** Check the box "Add Python to PATH"
4. Click "Install Now"
5. Wait for installation to complete

**Time required:** ~5 minutes

### Step 2: Install Application Dependencies

1. Navigate to the application folder
2. Double-click `install.bat`
3. Wait for all packages to install
4. Press any key when you see "Installation complete!"

**Time required:** ~5 minutes (downloads from internet)

### Step 3: Launch Application

1. Double-click `run_app.bat`
2. The application window will open

**Time required:** ~5 seconds

---

## Daily Usage

Every time you need to use the application:

1. Double-click `run_app.bat`
2. Load your images and analyze

## Main Window

The application window has three main sections:

### Left Side: Image Display
- Shows your microscopy image
- Red overlay indicates detected flakes
- Zoom and pan available (scroll wheel to zoom)

### Right Side: Controls
- Load Image button
- Previous/Next navigation buttons
- Parameter adjustment sliders
- Processing settings checkboxes

### Top: Results
- **Coverage:** Percentage of image covered by flakes
- **Processing Time:** How long detection took

## Loading and Analyzing Images

### Single Image Analysis

1. Click **"Load Image"** button
2. Browse to your image file (TIFF, PNG, JPG, or BMP)
3. Click "Open"
4. Image is automatically processed and results displayed

### Batch Processing

1. Load first image from a folder
2. Click **"Next"** to process next image in folder
3. Click **"Previous"** to go back
4. All images processed with current parameter settings

## Understanding Parameters

### Default Settings (Work for 90% of Cases)

The application opens with optimized defaults:
- ✓ Use Adaptive Threshold: **ENABLED**
- Adaptive Block Size: **200**
- Adaptive C: **5**
- Blur Kernel: **3**
- Morphological Close: **2**
- Morphological Open: **2**

**Most users should not need to change these!**

### When to Adjust Parameters

#### Missing Thin Flakes

**Problem:** Small or thin flakes are not detected (not highlighted in red)

**Solution:**
- Lower **Adaptive C** from 5 to 3 or 4
- Makes detection more sensitive

#### Detecting Too Much (False Positives)

**Problem:** Areas without flakes are highlighted in red

**Solution:**
- Raise **Adaptive C** from 5 to 10 or 15
- Makes detection less sensitive (only thick flakes)

#### Noisy Detection

**Problem:** Lots of small red dots everywhere

**Solution:**
- Increase **Blur Kernel** from 3 to 5 or 7
- Increase **Morphological Open** from 2 to 3 or 4

#### Small Holes in Detected Flakes

**Problem:** Flakes are detected but have holes in them

**Solution:**
- Increase **Morphological Close** from 2 to 3 or 4

#### Bright Circle in Center or Missing Corners

**Problem:** False detection in center OR missing flakes in corners

**Solution:**
- Make sure **"Use Adaptive Threshold"** is CHECKED
- This enables vignetting correction

## Parameter Reference

### Adaptive Threshold Settings

| Parameter | Range | Default | What It Does |
|-----------|-------|---------|--------------|
| **Use Adaptive Threshold** | Checkbox | ✓ ON | Enables vignetting correction - KEEP ON |
| **Adaptive Block Size** | 3-301 | 200 | Size of local region for background estimation<br>Should be larger than your largest flake |
| **Adaptive C** | 1-50 | 5 | Minimum brightness difference to detect flakes<br>Lower = more sensitive (thin flakes)<br>Higher = less sensitive (thick flakes only) |

### Pre-Processing Settings

| Parameter | Range | Default | What It Does |
|-----------|-------|---------|--------------|
| **Noise Reduction** | Checkbox | ✓ ON | Apply Gaussian blur before detection |
| **Blur Kernel** | 1-15 | 3 | Amount of blur<br>Higher = more noise reduction |

### Post-Processing Settings

| Parameter | Range | Default | What It Does |
|-----------|-------|---------|--------------|
| **Morphological Close** | 1-15 | 2 | Fill small holes in detected regions |
| **Morphological Open** | 1-15 | 2 | Remove small noise spots |

### Alternative Threshold Methods

| Parameter | Range | Default | What It Does |
|-----------|-------|---------|--------------|
| **Threshold** | 0-255 | 128 | Manual threshold value<br>Only works if Adaptive is OFF |
| **Auto-threshold Button** | - | - | Calculate optimal threshold automatically<br>Only works if Adaptive is OFF |

## Interpreting Results

### Coverage Percentage

**What it means:**
- Percentage of total image area covered by detected flakes
- Example: "Coverage: 15.23%" means 15.23% of image is flakes

**Typical ranges:**
- 1-5%: Low coverage, few small flakes
- 5-20%: Moderate coverage
- 20-50%: High coverage
- >50%: Very high coverage (check for over-detection)

### Red Overlay

**What it shows:**
- Red areas = Detected as thin film flakes
- Non-red areas = Substrate/background

**How to verify:**
- Compare red overlay to visible flakes in original image
- Red should match flake locations
- Adjust parameters if mismatch

### Processing Time

**What it means:**
- How long detection took in seconds
- Example: "Processing Time: 0.85 s"

**Typical times:**
- Small images (1024×1024): <0.5 seconds
- Medium images (2048×2048): <1.5 seconds
- Large images (4096×4096): <3 seconds

## Best Practices

### Imaging Consistency

1. **Use same microscope settings** for all images in a batch
   - Same magnification
   - Same illumination intensity
   - Same exposure time

2. **Focus carefully** before capturing
   - Out-of-focus images may not detect correctly

3. **Avoid overexposure** (too bright)
   - Flakes should be visible but not saturated

### Parameter Workflow

1. **Start with defaults** - Don't change anything initially
2. **Load representative image** - Choose typical sample
3. **Check detection quality** - Does red overlay match flakes?
4. **Adjust ONLY if needed** - Usually only Adaptive C
5. **Use same settings for batch** - Process all similar images with same parameters

### Recording Results

Currently, results are displayed only (not saved automatically).

**To record results:**

**Option 1: Screenshot**
1. Press `Windows Key + Shift + S`
2. Select area to capture
3. Paste into Word/PowerPoint/Email

**Option 2: Manual Recording**
1. Create Excel spreadsheet
2. Record: Filename, Coverage %, Processing Time, Parameters used

**Option 3: Future Version**
- CSV export feature planned for v2.1.0

## Troubleshooting

### Application Won't Start

**Symptom:** Double-clicking `run_app.bat` shows error

**Solutions:**
1. Check Python installed: Open Command Prompt, type `python --version`
2. If "not recognized": Reinstall Python with "Add to PATH" checked
3. Run `install.bat` again
4. Contact support if still failing

### Detection Not Working

**Symptom:** Everything is red OR nothing is red

**Solutions:**
1. Make sure "Use Adaptive Threshold" is CHECKED
2. Reset to defaults:
   - Adaptive Block Size: 200
   - Adaptive C: 5
   - Blur Kernel: 3
3. Check image quality (focus, exposure)
4. Try different image to rule out sample-specific issue

### Parameters Not Changing Anything

**Symptom:** Moving sliders doesn't update detection

**Solutions:**
1. Make sure an image is loaded
2. Check "Use Adaptive Threshold" is checked
3. Close and restart application
4. Reload image

### Can't Load TIFF Files

**Symptom:** "Unable to load image" for TIFF files

**Solutions:**
1. Verify file is not corrupted (open in ImageJ or other software)
2. Check file extension is .tif or .tiff
3. Try converting to PNG as test
4. Run `install.bat` again (may be missing Pillow)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open image |
| `Ctrl+Q` | Exit application |

## Advanced Topics

### Understanding the Algorithm

The application uses **adaptive threshold with local background subtraction**:

1. **Vignetting Problem:** Microscope images often have darker edges and brighter center
2. **Why Global Threshold Fails:** Single threshold either creates false circle in center OR misses corners
3. **Adaptive Solution:** Each pixel is compared to its local neighborhood, not global average
4. **Background Subtraction:** Calculates local background, subtracts it, detects anything brighter

**Technical Details:**
- Gaussian blur estimates local background (kernel = Adaptive Block Size)
- Difference image = Original - Background
- Threshold = Detect where difference > Adaptive C
- Morphological operations clean up noise

### Diagnostic Scripts

For advanced troubleshooting, run diagnostic scripts:

**Vignetting Analysis:**
```
python diagnose_threshold.py
```
Shows brightness distribution across image and threshold problems.

**Image Statistics:**
```
python analyze_images.py
```
Shows detailed histogram and statistics for your images.

### File Format Details

**Supported formats:**
- TIFF (.tif, .tiff): Recommended for microscopy, 16-bit support
- PNG (.png): Lossless, good for processed images
- JPEG (.jpg, .jpeg): Lossy compression, may affect detection
- BMP (.bmp): Uncompressed, large file size

**Recommendations:**
- Use TIFF when possible (best quality)
- Avoid JPEG for quantitative analysis (compression artifacts)

## Getting Help

### In This Package

1. **SETUP_GUIDE.md** - Detailed setup and installation troubleshooting
2. **QUICK_REFERENCE.md** - One-page reference card
3. **README.md** - Complete technical documentation
4. This **USER_GUIDE.md**

### Contact Support

If you've checked the troubleshooting section and still have issues:

**Include in your support request:**
1. What you were trying to do
2. What happened (error message or unexpected behavior)
3. Screenshot if applicable
4. Sample image (if detection problem)
5. Python version: Run `python --version` and include output

---

**Version:** 2.0.0
**Last Updated:** December 2025

**Remember:** The default settings work for most cases. Only adjust parameters if you see clear detection problems!
