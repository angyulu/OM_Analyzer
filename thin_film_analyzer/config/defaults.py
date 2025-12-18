"""
Default configuration values for the Thin Film Analyzer application.
"""

import os
from pathlib import Path

# Application metadata
APP_NAME = "ThinFilmAnalyzer"
APP_VERSION = "2.2.0"

# Image processing defaults
DEFAULT_THRESHOLD = 128  # Mid-range threshold for binary segmentation
DEFAULT_NOISE_REDUCTION = True
DEFAULT_OVERLAY_TRANSPARENCY = 0.5  # 50% opacity
DEFAULT_OVERLAY_COLOR = (255, 0, 0)  # Red (BGR format for OpenCV)

# File format support
SUPPORTED_IMAGE_FORMATS = [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"]
MAX_BATCH_SIZE = 100  # Maximum number of images in a single batch

# Performance constraints
MAX_IMAGE_PROCESSING_TIME_S = 3  # Seconds for single image (2048x2048)
MAX_BATCH_PROCESSING_TIME_S = 120  # Seconds for 10 images
UI_RESPONSIVENESS_MS = 200  # Maximum UI lag during processing
MAX_MEMORY_BATCH_GB = 2  # Maximum memory for 50-image batch

# Settings persistence
def get_settings_dir():
    """Get platform-specific settings directory."""
    if os.name == 'nt':  # Windows
        base_dir = os.environ.get('APPDATA', Path.home())
    else:  # macOS/Linux
        base_dir = Path.home() / '.config'

    settings_dir = Path(base_dir) / APP_NAME
    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir

SETTINGS_FILE = "settings.json"
SETTINGS_BACKUP_FILE = "settings.json.bak"
PRESETS_FILE = "presets.json"

# Error logging
ERROR_LOG_FILE = "error.log"
MAX_LOG_SIZE_MB = 10
LOG_BACKUP_COUNT = 2

# UI defaults
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MINIMUM_WINDOW_WIDTH = 1280  # v2.2.0: Minimum supported window width
MINIMUM_WINDOW_HEIGHT = 720  # v2.2.0: Minimum supported window height
CONTROL_PANEL_MAX_WIDTH = 500  # v2.2.0: Maximum width for control panels
THUMBNAIL_SIZE = 150  # pixels

# Scale calibration
DEFAULT_SCALE_UM_PER_PIXEL = None  # No calibration by default

# ROI defaults
ROI_BORDER_COLOR = (0, 255, 0)  # Green for ROI rectangle
ROI_BORDER_WIDTH = 2  # pixels

# v2.1.0: LAB Layer Detection defaults
DEFAULT_T1 = 85  # Monolayer/Bilayer boundary threshold
DEFAULT_T2 = 170  # Bilayer/Trilayer boundary threshold
DEFAULT_AUTO_ALGORITHM = "kmeans"  # Default auto-detection algorithm
DEFAULT_ADAPTIVE_BIAS = 0  # Adaptive threshold bias (-10 to +10)
DEFAULT_APPLY_VIGNETTING_CORRECTION = True  # Apply L-channel vignetting correction
