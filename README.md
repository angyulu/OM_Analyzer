# Thin Film Analyzer v2.1.1

Desktop application for automated thin film coverage analysis from optical microscope images.

![Version](https://img.shields.io/badge/version-2.1.1-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## Overview

Thin Film Analyzer is a powerful desktop application that automatically detects and analyzes thin film coverage from optical microscope images. It features two detection modes:

- **V1 Mode**: Fast, accurate thin film detection using adaptive thresholding
- **V2 Mode**: Advanced layer classification (monolayer, bilayer, trilayer) using LAB color space analysis

### Key Features

✅ **Automated Detection** - No manual tracing required  
✅ **Adaptive Thresholding** - Handles uneven illumination  
✅ **Layer Classification** - Distinguish between mono/bi/trilayer regions  
✅ **Batch Processing** - Process hundreds of images automatically  
✅ **Visual Overlay** - Color-coded visualization of detected regions  
✅ **CSV Export** - Export results to spreadsheet format  
✅ **Cross-Platform** - Works on Windows, macOS, and Linux  

---

## Quick Links

- 📖 [Installation Guide](INSTALLATION_GUIDE.md) - Step-by-step setup instructions
- 📚 [User Guide](USER_GUIDE.md) - Complete usage documentation
- 🐛 [Report Issues](https://github.com/angyulu/OM_Analyzer/issues) - Bug reports and feature requests
- 💾 [Download Latest Release](https://github.com/angyulu/OM_Analyzer/releases/latest)

---

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Display**: 1280x800 minimum resolution

### Supported Image Formats

- TIFF (.tif, .tiff) - Including 16-bit
- PNG (.png)
- JPEG (.jpg, .jpeg)
- BMP (.bmp)

---

## Installation

### Quick Install

**Windows:**
```cmd
install.bat
```

**macOS/Linux:**
```bash
chmod +x install.sh
./install.sh
```

For detailed installation instructions, see [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md).

---

## Usage

### Quick Start

1. Launch the application:
   - **Windows**: Double-click `run_app.bat`
   - **macOS/Linux**: Run `./run_app.sh`

2. Load an image:
   - Drag and drop onto the window
   - Or use `File > Open Image...`

3. View results:
   - Red overlay shows detected film
   - Coverage percentage in Results panel

For complete usage instructions, see [USER_GUIDE.md](USER_GUIDE.md).

---

## Features

### V1 Mode: Basic Film Detection

- **Adaptive Threshold**: Handles uneven illumination and vignetting
- **Noise Reduction**: Gaussian blur and morphological operations
- **Real-time Overlay**: Visual feedback while adjusting parameters
- **Fast Processing**: ~1-2 seconds per image

### V2 Mode: Layer Classification

- **Color-Coded Overlay**:
  - Red = Monolayer
  - Blue = Bilayer
  - Green = Trilayer

- **Auto-Detection**: Four algorithms to automatically find optimal thresholds
  - K-means clustering
  - Percentile-based
  - Histogram peak detection
  - Otsu multi-threshold

- **Vignetting Correction**: Compensate for darker edges in microscope images
- **Manual Fine-Tuning**: Adjust T1/T2 thresholds while viewing results

### Batch Processing

- Load and process hundreds of images
- Navigate between images easily
- Lock settings for consistent processing
- Export all results to CSV
- Save overlay images for documentation

---

## What's New in v2.1.1

🐛 **Bug Fixes:**
- Fixed overlay display issues in layer detection mode
- Fixed binary mask value mismatch causing layer detection failures
- Fixed auto-detect thresholds error
- Fixed wrong overlay color in V1 mode (now correctly shows red)

🔄 **Changes:**
- Layer detection now disabled by default (V1 mode on startup)
- Improved error logging and debugging output

📝 **Documentation:**
- Added comprehensive installation guide
- Added detailed user guide
- Improved troubleshooting documentation

---

## Technology Stack

- **GUI**: PyQt6
- **Image Processing**: OpenCV, scikit-image
- **Scientific Computing**: NumPy, SciPy
- **Data Export**: Pandas
- **Language**: Python 3.10+

---

## Support

### Getting Help

- 📖 Read the [User Guide](USER_GUIDE.md)
- 🔧 Check [Installation Guide](INSTALLATION_GUIDE.md) for setup issues
- 🐛 [Report bugs](https://github.com/angyulu/OM_Analyzer/issues) on GitHub

### Common Issues

**Application won't start:**
- Ensure Python 3.10+ is installed
- Run `install.bat` or `./install.sh` to install dependencies

**Modules not found:**
- Rerun the installer
- Or manually: `pip install -r requirements.txt`

**Display issues:**
- Update graphics drivers
- Check system meets minimum requirements

For more troubleshooting, see [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md#troubleshooting).

---

## Project Structure

```
ThinFilmAnalyzer_v2.1.1/
├── README.md                  # This file
├── INSTALLATION_GUIDE.md      # Setup instructions
├── USER_GUIDE.md              # Usage documentation
├── requirements.txt           # Python dependencies
├── install.bat                # Windows installer
├── install.sh                 # macOS/Linux installer
├── run_app.bat                # Windows launcher
├── run_app.sh                 # macOS/Linux launcher
└── thin_film_analyzer/        # Application source code
    ├── main.py                # Entry point
    ├── config/                # Configuration
    ├── core/                  # Core processing logic
    ├── models/                # Data models
    └── ui/                    # User interface
```

---

## Contributing

We welcome contributions! If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

This project is licensed under the MIT License.

---

## Authors

Research Team  
Version 2.1.1 - December 2025

---

## Acknowledgments

Built with:
- PyQt6 for the user interface
- OpenCV for image processing
- scikit-image for advanced algorithms
- NumPy and SciPy for scientific computing

---

**Repository**: https://github.com/angyulu/OM_Analyzer

