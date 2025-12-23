# User Guide - Thin Film Analyzer v2.2.1

Complete guide for using the Thin Film Analyzer application to analyze thin film coverage from optical microscope images.

## Table of Contents

- [Quick Start](#quick-start)
- [Basic Features (V1 Mode)](#basic-features-v1-mode)
- [Advanced Features (V2 Mode)](#advanced-features-v2-mode)
- [Batch Processing](#batch-processing)
- [Exporting Results](#exporting-results)
- [Tips & Best Practices](#tips--best-practices)

---

## Quick Start

### 1. Launch the Application

**Windows:** Double-click `run_app.bat`

**macOS/Linux:** Run `./run_app.sh` in Terminal

### 2. Load Images from Folder

- Click the **"📁 Select Folder..."** button at the top of the Processing panel
- Or use `File > Select Folder...` (Ctrl+O)
- All images in the selected folder will be loaded automatically
- Supported formats: TIFF, PNG, JPEG, BMP

### 3. View Results

- Red overlay shows detected thin film
- Total Coverage percentage appears in Results panel
- Adjust threshold slider if needed


## Basic Features (V1 Mode)

V1 mode is the default mode providing fast thin film detection.

### Controls

**Threshold Slider:**
- Lower values = detect thinner films
- Higher values = detect only thicker films
- Auto-calculated when image loads

**Adaptive Threshold:**
- Check for images with uneven lighting
- Better for detecting films in corners/edges

**Noise Reduction:**
- Reduces false positives
- Blur Kernel: 3-15 (odd numbers)

**Overlay:**
- Toggle visibility with checkbox
- Adjust transparency with slider

### Results

- **Total Coverage**: Percentage of film detected
- **Area**: Physical area (requires calibration)

---

## Advanced Features (V2 Mode)

### Enable Layer Detection

1. Check "Enable Layer Detection" in V2 panel
2. Image reprocesses with color-coded overlay:
   - **Red** = Monolayer
   - **Blue** = Bilayer
   - **Green** = Trilayer

### Auto-Detect Thresholds

1. Select algorithm (K-means, Percentile, Histogram, or Otsu Multi)
2. Click "Auto-Detect Thresholds"
3. T1 and T2 sliders update automatically

### Manual Adjustment

- **T1 Slider**: Monolayer/Bilayer boundary (0-255)
- **T2 Slider**: Bilayer/Trilayer boundary (0-255)
- Adjust while viewing color-coded overlay

### Lock Thresholds

- Click lock button to fix T1/T2 for batch processing
- Ensures consistent classification across images

---

## Batch Processing

### Load Multiple Images

- Click **"📁 Select Folder..."** button at the top of the Processing panel
- Or use `File > Select Folder...` menu option
- All images in the selected folder will be loaded automatically

### Navigation

- Use Previous/Next buttons
- Or select from dropdown menu

### Process All

1. Adjust settings on first image
2. Lock thresholds if using V2 mode
3. `Batch > Process All Images` (Ctrl+P)
4. Wait for progress to complete

---

## Exporting Results

### Export to CSV

1. Process images
2. `Batch > Export Results to CSV...` (Ctrl+E)
3. Save file

**CSV includes:**
- Filename
- Total Coverage (%)
- Monolayer/Bilayer/Trilayer Coverage (%)

### Export Overlay Images

1. Process images
2. `Batch > Export Overlay Images...`
3. Select output folder
4. Overlay images saved as PNG

---

## Tips & Best Practices

### Getting Best Results

1. Use high-quality source images
2. Start with V1 mode, then enable V2
3. Use Adaptive Threshold for real-world images
4. Adjust threshold while viewing overlay

### Batch Processing Workflow

1. Load all images
2. Adjust settings on first image
3. Check a few samples
4. Lock settings (V2 mode)
5. Process all
6. Export results

### Troubleshooting

**Overlay shows too much area:**
- Increase threshold
- Enable noise reduction

**Missing thin films:**
- Decrease threshold
- Use adaptive threshold

**Wrong layer colors (V2):**
- Run Auto-Detect again
- Try different algorithm
- Adjust T1/T2 manually

---

## Need Help?

- Installation: See INSTALLATION_GUIDE.md
- Technical issues: See README.md
- Report bugs: https://github.com/angyulu/OM_Analyzer/issues

