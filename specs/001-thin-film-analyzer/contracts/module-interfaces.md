# Module Interfaces & Contracts
## Thin Film Coverage Analyzer

**Feature**: 001-thin-film-analyzer
**Date**: 2025-12-07
**Purpose**: Define contracts between application modules (no REST APIs - desktop app)

---

## Overview

This document defines the interfaces and contracts between core modules in the Thin Film Coverage Analyzer. Since this is a desktop application (not web/API), contracts focus on Python module interfaces, function signatures, and expected behaviors.

---

## Module Dependency Graph

```
┌───────────────┐
│  ui/          │
│  (PyQt6 GUI)  │
└───────┬───────┘
        │ uses
        ▼
┌───────────────┐      ┌──────────────┐
│  core/        │─────►│  models/     │
│  (Business    │ uses │  (Data       │
│   Logic)      │      │   Entities)  │
└───────┬───────┘      └──────────────┘
        │ uses
        ▼
┌───────────────┐
│  config/      │
│  (Settings &  │
│   Defaults)   │
└───────────────┘
```

**Dependency Rules**:
- `ui/` MAY depend on `core/` and `models/`
- `core/` MAY depend on `models/` and `config/`
- `models/` MUST NOT depend on `ui/` or `core/` (pure data)
- `config/` MUST NOT depend on any other modules (pure constants)

---

## 1. Image Processing Module (`core/processor.py`)

### Interface: `process_image()`

**Purpose**: Load and process a single OM image to detect thin film regions.

**Signature**:
```python
def process_image(
    image_path: str | Path,
    threshold_value: Optional[int] = None,
    noise_reduction: bool = True,
    roi: Optional[tuple[int, int, int, int]] = None
) -> tuple[np.ndarray, float]:
    """
    Process optical microscope image to detect thin film coverage.

    Args:
        image_path: Path to image file (PNG, JPG, TIFF, BMP)
        threshold_value: Manual threshold (0-255) or None for auto (Otsu)
        noise_reduction: Apply Gaussian blur preprocessing
        roi: Region of interest (x, y, width, height) or None for full image

    Returns:
        Tuple of (binary_mask, coverage_percentage)
        - binary_mask: NumPy array (height, width) with 0/255 values
        - coverage_percentage: Float 0-100 representing film coverage

    Raises:
        FileNotFoundError: If image_path does not exist
        ValueError: If image cannot be loaded or is corrupted
        ValueError: If threshold_value not in range 0-255
        ValueError: If ROI coordinates invalid

    Examples:
        >>> mask, coverage = process_image("sample.png")
        >>> print(f"Coverage: {coverage:.2f}%")
        Coverage: 42.15%

        >>> mask, coverage = process_image("sample.png", threshold_value=150, roi=(0, 0, 1024, 1024))
        >>> print(f"ROI Coverage: {coverage:.2f}%")
        ROI Coverage: 38.50%
    """
```

**Contract**:
- MUST return binary mask with same dimensions as input (or ROI dimensions if specified)
- Coverage percentage MUST be in range [0, 100]
- MUST handle images up to 4096×4096 pixels
- MUST complete processing in <3 seconds for 2048×2048 images (FR-028)
- MUST NOT modify the original image file
- Binary mask: 255 = film, 0 = substrate (per constitutional algorithm)

**Error Handling**:
```python
# Invalid file path
>>> process_image("nonexistent.png")
FileNotFoundError: Image not found: nonexistent.png

# Corrupted file
>>> process_image("corrupted.png")
ValueError: Unable to load image: corrupted.png. File may be corrupted.

# Invalid threshold
>>> process_image("sample.png", threshold_value=300)
ValueError: Threshold must be in range 0-255, got 300

# Invalid ROI
>>> process_image("sample.png", roi=(-10, 0, 100, 100))
ValueError: ROI coordinates must be non-negative
```

---

## 2. Detection Module (`core/detection.py`)

### Interface: `apply_threshold()`

**Purpose**: Apply thresholding to grayscale image.

**Signature**:
```python
def apply_threshold(
    grayscale_image: np.ndarray,
    threshold_value: Optional[int] = None,
    method: str = "otsu"
) -> np.ndarray:
    """
    Apply thresholding to separate film from substrate.

    Args:
        grayscale_image: Grayscale image array (height, width)
        threshold_value: Manual threshold or None for automatic
        method: "otsu", "adaptive", or "manual" (ignored if threshold_value provided)

    Returns:
        Binary mask (height, width) with 0/255 values

    Raises:
        ValueError: If image is not grayscale (2D array)
        ValueError: If method not recognized

    Examples:
        >>> gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        >>> mask = apply_threshold(gray)  # Auto Otsu
        >>> mask = apply_threshold(gray, threshold_value=128)  # Manual
    """
```

**Contract**:
- MUST preserve image dimensions (output same shape as input)
- MUST return uint8 array with values 0 or 255 only
- MUST use Otsu's method when `threshold_value=None` and `method="otsu"`
- MUST be deterministic (same input → same output)

---

## 3. Overlay Module (`core/overlay.py`)

### Interface: `generate_overlay()`

**Purpose**: Create visual overlay of detection mask on original image.

**Signature**:
```python
def generate_overlay(
    original_image: np.ndarray,
    binary_mask: np.ndarray,
    opacity: float = 0.5,
    color: tuple[int, int, int] = (255, 0, 0)
) -> np.ndarray:
    """
    Generate overlay image with detection mask highlighted.

    Args:
        original_image: Original RGB/BGR image (height, width, 3)
        binary_mask: Binary mask (height, width) from detection
        opacity: Overlay transparency 0.0 (invisible) to 1.0 (opaque)
        color: RGB tuple for overlay color (default: red)

    Returns:
        RGB image (height, width, 3) with overlay blended

    Raises:
        ValueError: If image and mask dimensions don't match
        ValueError: If opacity not in range [0, 1]

    Examples:
        >>> overlay = generate_overlay(img, mask, opacity=0.7, color=(0, 255, 0))
        >>> cv2.imwrite("result_with_overlay.png", overlay)
    """
```

**Contract**:
- MUST blend overlay using alpha compositing: `result = (1-opacity)*original + opacity*colored_mask`
- MUST preserve original image dimensions and color space
- MUST handle opacity edge cases (0.0 → original image, 1.0 → full color mask)
- MUST NOT modify input arrays (return new array)

**Real-time Performance**:
- MUST complete in <50ms for 2048×2048 images (real-time slider requirement FR-014)

---

## 4. Calibration Module (`core/calibration.py`)

### Interface: `CalibrationManager`

**Purpose**: Manage scale presets (save, load, check duplicates).

**Signature**:
```python
class CalibrationManager:
    """Manage scale calibration presets with persistence."""

    def __init__(self, settings_dir: Path):
        """Initialize calibration manager with settings directory."""

    def save_preset(self, preset: ScalePreset, overwrite: bool = False) -> None:
        """
        Save scale preset to settings.

        Args:
            preset: ScalePreset object to save
            overwrite: If True, overwrite existing preset with same name

        Raises:
            ValueError: If preset with same name exists and overwrite=False
            ValueError: If preset validation fails

        Examples:
            >>> mgr = CalibrationManager(Path("~/.config/ThinFilmAnalyzer"))
            >>> preset = ScalePreset("10x", 0.65, datetime.now())
            >>> mgr.save_preset(preset)
        """

    def load_preset(self, name: str) -> ScalePreset:
        """
        Load preset by name.

        Args:
            name: Preset name

        Returns:
            ScalePreset object

        Raises:
            KeyError: If preset with given name not found

        Examples:
            >>> preset = mgr.load_preset("10x objective")
            >>> print(preset.scale_um_per_pixel)
            0.65
        """

    def preset_exists(self, name: str) -> bool:
        """Check if preset with given name exists."""

    def list_presets(self) -> list[str]:
        """Return list of all preset names."""

    def delete_preset(self, name: str) -> None:
        """Delete preset by name."""
```

**Contract**:
- MUST persist presets to JSON file in settings directory
- MUST enforce unique preset names (per clarification FR-018)
- MUST validate preset before saving (scale > 0, name non-empty)
- MUST load presets from backup if primary settings corrupted (FR-036)

---

## 5. Export Module (`core/export.py`)

### Interface: `ResultsExporter`

**Purpose**: Export batch results to CSV with summary statistics.

**Signature**:
```python
class ResultsExporter:
    """Export detection results to CSV format."""

    def __init__(self):
        """Initialize exporter with empty results list."""

    def add_result(self, filename: str, coverage_pct: float, area_um2: float) -> None:
        """
        Add a single result to the export batch.

        Args:
            filename: Image filename
            coverage_pct: Coverage percentage (0-100)
            area_um2: Absolute area in µm² (0 if not calibrated)
        """

    def export_csv(self, output_path: Path) -> None:
        """
        Export results to CSV with summary statistics.

        Args:
            output_path: Path for output CSV file

        Raises:
            ValueError: If no results added
            IOError: If unable to write file

        CSV Format:
            Filename,Coverage (%),Area (µm²)
            sample_001.png,42.15,1250.5
            sample_002.png,38.20,1100.2
            --- Summary Statistics ---
            Mean Coverage (%),40.18
            Std Dev Coverage (%),2.79
            Min Coverage (%),38.20
            Max Coverage (%),42.15

        Examples:
            >>> exporter = ResultsExporter()
            >>> exporter.add_result("img1.png", 42.5, 1200.0)
            >>> exporter.add_result("img2.png", 38.0, 1100.0)
            >>> exporter.export_csv(Path("results.csv"))
        """

    def export_images_with_overlay(
        self,
        results: list[tuple[Image, np.ndarray, np.ndarray]],
        output_dir: Path
    ) -> None:
        """
        Export processed images with overlay (FR-033).

        Args:
            results: List of (Image, original_array, overlay_array) tuples
            output_dir: Directory for output images

        Saves:
            {filename}_overlay.png for each input image
        """
```

**Contract**:
- CSV MUST include header row
- CSV MUST include summary statistics footer (FR-032)
- MUST calculate statistics using Pandas `describe()` method
- MUST handle empty results list gracefully (raise ValueError)
- Exported overlay images MUST preserve original dimensions

---

## 6. Settings Module (`core/settings.py`)

### Interface: `SettingsManager`

**Purpose**: Persist and restore application settings with backup.

**Signature**:
```python
class SettingsManager:
    """Manage application settings with atomic save and backup recovery."""

    def __init__(self, settings_dir: Path):
        """
        Initialize settings manager.

        Args:
            settings_dir: Directory for settings files (e.g., ~/.config/ThinFilmAnalyzer)
        """

    def save_settings(self, settings: ApplicationSettings) -> None:
        """
        Atomically save settings with automatic backup.

        Args:
            settings: ApplicationSettings object

        Contract:
            - MUST write to temp file first
            - MUST create backup (.bak) of existing settings before overwrite
            - MUST atomically rename temp → primary (FR-035)
            - MUST update backup_timestamp in settings

        Examples:
            >>> settings = ApplicationSettings(...)
            >>> mgr = SettingsManager(Path("..."))
            >>> mgr.save_settings(settings)
        """

    def load_settings(self) -> ApplicationSettings:
        """
        Load settings with backup recovery.

        Returns:
            ApplicationSettings object (defaults if no file or both corrupted)

        Contract:
            - TRY primary settings file first
            - IF corrupted, TRY backup (.bak) file (FR-036)
            - IF both corrupted/missing, RETURN defaults
            - MUST NOT raise exception (always return valid settings)

        Examples:
            >>> mgr = SettingsManager(Path("..."))
            >>> settings = mgr.load_settings()
            >>> print(settings.last_threshold)
            128
        """

    def get_default_settings(self) -> ApplicationSettings:
        """Return default settings (used when no settings file exists)."""
```

**Contract**:
- MUST create settings directory if it doesn't exist
- MUST use JSON format for human readability
- MUST preserve manual edits to settings file (don't overwrite unnecessarily)
- MUST handle Windows/macOS path differences (`%APPDATA%` vs `~/.config`)

**File Locations**:
- Windows: `%APPDATA%\ThinFilmAnalyzer\settings.json`
- macOS: `~/.config/ThinFilmAnalyzer/settings.json`
- Backup: Same directory with `.bak` extension

---

## 7. Logger Module (`core/logger.py`)

### Interface: `ErrorLogger`

**Purpose**: Log errors with rotation and diagnostic export.

**Signature**:
```python
class ErrorLogger:
    """Error logging with automatic rotation and diagnostics export."""

    def __init__(self, log_dir: Path):
        """
        Initialize error logger.

        Args:
            log_dir: Directory for error log files
        """

    def log_error(
        self,
        message: str,
        exc_info: Optional[Exception] = None,
        context: Optional[dict] = None
    ) -> None:
        """
        Log error with context information.

        Args:
            message: Human-readable error description
            exc_info: Exception object (for stack trace)
            context: Additional context (current operation, file being processed)

        Contract:
            - MUST include timestamp (ISO format with milliseconds)
            - MUST include filename and line number
            - MUST include stack trace if exc_info provided (FR-041)
            - MUST format context as key-value pairs

        Examples:
            >>> logger = ErrorLogger(Path("..."))
            >>> try:
            ...     img = cv2.imread("broken.png")
            ...     if img is None:
            ...         raise ValueError("Unable to load image")
            ... except ValueError as e:
            ...     logger.log_error(
            ...         "Image load failed",
            ...         exc_info=e,
            ...         context={"operation": "batch_processing", "index": 5}
            ...     )
        """

    def export_diagnostics(self, export_path: Path) -> None:
        """
        Package logs and system info for troubleshooting (FR-042).

        Args:
            export_path: Path for output ZIP file

        ZIP Contents:
            - error.log (current log)
            - error.log.1, error.log.2 (rotated backups)
            - system_info.json (platform, Python version, etc.)

        Examples:
            >>> logger.export_diagnostics(Path("diagnostics.zip"))
            Created: diagnostics.zip (245 KB)
        """
```

**Contract**:
- MUST rotate logs at 10 MB max size (FR-043)
- MUST keep 2 backup files (error.log.1, error.log.2)
- MUST use Python `logging.handlers.RotatingFileHandler`
- Log format: `YYYY-MM-DD HH:MM:SS,mmm - LEVEL - file.py:line - message | Context: {...}`

---

## 8. UI Module Contracts

### Interface: `MainWindow` (ui/main_window.py)

**Signals Emitted**:
```python
class MainWindow(QMainWindow):
    # Signals for communication with core modules
    threshold_changed = pyqtSignal(int)        # New threshold value (0-255)
    overlay_opacity_changed = pyqtSignal(float) # New opacity (0.0-1.0)
    process_requested = pyqtSignal(list)       # List of Image objects to process
    export_csv_requested = pyqtSignal(Path)    # Output path for CSV
    new_session_requested = pyqtSignal()       # Clear all data
```

**Slots (Methods)**:
```python
    def on_images_loaded(self, image_paths: list[Path]) -> None:
        """Handle drag-and-drop or file browser image selection."""

    def on_processing_complete(self, results: list[DetectionResult]) -> None:
        """Update results table with processed results."""

    def on_processing_error(self, filename: str, error_msg: str) -> None:
        """Display error message for failed image."""
```

**Contract**:
- MUST use QThread for all image processing (no blocking on main thread) (FR-026)
- MUST update progress bar during batch processing (FR-025)
- MUST remain responsive (<200ms interaction latency) (SC-007)

---

## 9. Testing Contracts

### Unit Test Requirements

**All `core/` modules MUST have**:
- Unit tests covering >80% code coverage
- Tests for error conditions (invalid inputs, corrupted data)
- Tests for boundary conditions (empty arrays, max size images, 0/100% coverage)

**Example Test Structure**:
```python
# tests/unit/test_processor.py

def test_process_image_valid():
    """Test successful image processing."""
    mask, coverage = process_image("tests/synthetic/coverage_50pct.png")
    assert 48 <= coverage <= 52  # Allow ±2% tolerance

def test_process_image_file_not_found():
    """Test error handling for missing file."""
    with pytest.raises(FileNotFoundError):
        process_image("nonexistent.png")

def test_process_image_corrupted():
    """Test error handling for corrupted file."""
    with pytest.raises(ValueError):
        process_image("tests/data/corrupted.png")

def test_process_image_with_roi():
    """Test ROI restriction."""
    mask_full, cov_full = process_image("sample.png")
    mask_roi, cov_roi = process_image("sample.png", roi=(0, 0, 1024, 1024))
    assert mask_roi.shape == (1024, 1024)
```

### Integration Test Requirements

**Full workflow tests MUST**:
- Test each user story end-to-end (P1-P4)
- Use synthetic test images with known coverage
- Validate results against expected values (±2% tolerance)

---

## Performance Contracts

### Processing Performance

| Operation | Max Time | Measurement Method |
|-----------|----------|-------------------|
| `process_image(2048×2048)` | 3 seconds | `time.perf_counter()` |
| `generate_overlay(2048×2048)` | 50 ms | `time.perf_counter()` |
| Batch (10 images) | 2 minutes | Wall clock time |
| UI interaction | 200 ms | QTimer measurement |

### Memory Contracts

| Operation | Max Memory | Measurement Method |
|-----------|-----------|-------------------|
| Single image loaded | 20 MB | `sys.getsizeof()` |
| 50-image batch | 2 GB | Process monitor |
| Settings file | 100 KB | File size |
| Error log (before rotation) | 10 MB | File size (FR-043) |

---

## Version Compatibility

**Python Version**: 3.10+
**Dependencies**:
- PyQt6 >= 6.5.0
- opencv-python >= 4.8.0
- scikit-image >= 0.21.0
- numpy >= 1.24.0
- pandas >= 2.0.0

**Backward Compatibility**:
- Settings file format MUST remain compatible across versions
- JSON schema changes MUST provide migration path
- Deprecated functions MUST include warnings before removal

---

**Contracts Status**: ✅ Complete
**Coverage**: All core modules and UI interfaces defined
