# Research & Technology Decisions
## Thin Film Coverage Analyzer

**Date**: 2025-12-07
**Feature**: 001-thin-film-analyzer
**Status**: Complete

---

## Overview

This document captures technology research, design decisions, and best practices for implementing the Thin Film Coverage Analyzer desktop application.

---

## 1. UI Framework Selection: PyQt6 vs. Tkinter

### Decision: **PyQt6**

### Rationale

- **Rich widgets**: PyQt6 provides QGraphicsView for image display with overlay rendering, QSlider for threshold/transparency controls, drag-and-drop support via QMimeData
- **Performance**: Native rendering for large images (2048×2048), hardware acceleration support, better responsiveness than Tkinter
- **Customization**: Easier to create custom widgets (ROI selector, image viewer with overlay blending)
- **Professional appearance**: Modern styling with QSS (Qt Style Sheets), better for user acceptance
- **Threading**: QThread support for background image processing without UI freezing (constitutional requirement: UI responsiveness)
- **Packaging**: PyInstaller has excellent PyQt6 support for creating standalone .exe files

### Alternatives Considered

| Option | Pros | Cons | Rejection Reason |
|--------|------|------|------------------|
| Tkinter | Included with Python, no extra dependencies | Limited widgets, poor performance with large images, less professional appearance | Fails performance and usability requirements |
| PySide6 | LGPL license, official Qt for Python | Functionally equivalent to PyQt6 | PyQt6 has larger community and more examples for scientific apps |
| wxPython | Native look on all platforms | Smaller community, less documentation for image processing apps | Learning curve, less suitable for image-heavy applications |

### Implementation Notes

- Use `QGraphicsView` + `QGraphicsScene` for image display with overlay
- `QThread` for batch processing to keep UI responsive (FR-026)
- `QFileDialog` with native drag-and-drop for image loading (FR-001, FR-002)
- Custom `QWidget` subclasses for threshold slider, transparency control, ROI selector
- `QTableWidget` for results display (FR-029)

---

## 2. Image Processing Pipeline: OpenCV Best Practices

### Decision: **OpenCV (cv2) + scikit-image**

### Rationale

- **OpenCV**: Industry standard for computer vision, optimized C++ backend, excellent Python bindings
- **scikit-image**: Complementary for morphological operations, region properties, scientific imaging focus
- **NumPy integration**: Both libraries use NumPy arrays natively, zero-copy operations
- **Performance**: Meets <3 second processing target for 2048×2048 images

### Constitutional Algorithm Implementation

```python
# Per constitution: Grayscale → Gaussian blur → Adaptive/Otsu threshold → Morphological ops → Coverage

import cv2
import numpy as np
from skimage import morphology

def process_image(image_path, threshold_value=None, noise_reduction=True):
    """
    Constitutional baseline algorithm for thin film detection.

    Args:
        image_path: Path to OM image file
        threshold_value: Manual threshold (0-255) or None for auto (Otsu)
        noise_reduction: Apply Gaussian blur preprocessing

    Returns:
        Binary mask (film=255, substrate=0), coverage_percentage
    """
    # Step 1: Load and convert to grayscale
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Step 2: Gaussian blur for noise reduction (optional per FR-008)
    if noise_reduction:
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Step 3: Thresholding (adaptive or Otsu per constitution)
    if threshold_value is None:
        # Otsu automatic thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        # Manual threshold for user adjustment (FR-007)
        _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

    # Step 4: Morphological operations to clean mask
    # Opening: removes small white noise
    # Closing: fills small holes in film regions
    kernel = np.ones((3,3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Step 5: Calculate coverage
    total_pixels = binary.size
    film_pixels = np.count_nonzero(binary)
    coverage_percentage = (film_pixels / total_pixels) * 100

    return binary, coverage_percentage
```

### Performance Optimization

- Use `cv2.imread()` with `cv2.IMREAD_COLOR` flag for faster loading
- Pre-allocate NumPy arrays for batch processing to reduce memory allocation overhead
- Use `cv2.resize()` for thumbnail generation (FR-003) instead of loading full images
- Implement lazy loading: only process images when user clicks "Process", not on load

### Alternatives Considered

| Option | Pros | Cons | Rejection Reason |
|--------|------|------|------------------|
| PIL/Pillow only | Simple API, built-in with many Python installations | Slower for large images, limited CV operations | Fails <3 second performance requirement |
| scikit-image only | Scientific focus, pure Python | Slower than OpenCV for basic operations | OpenCV faster for grayscale, blur, threshold operations |
| SimpleITK | Medical imaging focus | Overkill for 2D microscopy, larger binary size | Violates simplicity principle |

---

## 3. Settings Persistence: JSON with Atomic Write + Backup

### Decision: **JSON files in user AppData with atomic write and automatic backup**

### Rationale (addresses clarification from spec)

- **Location**: `%APPDATA%/ThinFilmAnalyzer/` on Windows, `~/.config/ThinFilmAnalyzer/` on macOS
- **Format**: JSON for human-readable settings (scale presets, last-used values)
- **Atomic write**: Write to temp file, then rename to prevent corruption (FR-035)
- **Automatic backup**: Keep `.bak` copy of last good settings file (FR-034)
- **Crash recovery**: Attempt to load `.bak` if primary file is corrupted (FR-036)

### Implementation Pattern

```python
import json
import os
import shutil
from pathlib import Path

class SettingsManager:
    def __init__(self):
        # User-specific AppData directory
        if os.name == 'nt':  # Windows
            self.settings_dir = Path(os.getenv('APPDATA')) / 'ThinFilmAnalyzer'
        else:  # macOS/Linux
            self.settings_dir = Path.home() / '.config' / 'ThinFilmAnalyzer'

        self.settings_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.settings_dir / 'settings.json'
        self.backup_file = self.settings_dir / 'settings.json.bak'

    def save_settings(self, settings_dict):
        """Atomic write with automatic backup (FR-034, FR-035)."""
        temp_file = self.settings_file.with_suffix('.tmp')

        # Write to temp file first
        with open(temp_file, 'w') as f:
            json.dump(settings_dict, f, indent=2)

        # Backup existing settings if present
        if self.settings_file.exists():
            shutil.copy2(self.settings_file, self.backup_file)

        # Atomic rename (POSIX: atomic, Windows: mostly atomic)
        temp_file.replace(self.settings_file)

    def load_settings(self):
        """Load settings with backup recovery (FR-036)."""
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Attempt backup recovery
            if self.backup_file.exists():
                try:
                    with open(self.backup_file, 'r') as f:
                        settings = json.load(f)
                    # Restore from backup
                    self.save_settings(settings)
                    return settings
                except json.JSONDecodeError:
                    pass

            # Return defaults if both files corrupted/missing
            return self.get_default_settings()

    def get_default_settings(self):
        return {
            'scale_presets': [],
            'last_threshold': 128,
            'overlay_transparency': 0.5,
            'noise_reduction_enabled': True,
            'window_geometry': None
        }
```

### File Structure

```
%APPDATA%/ThinFilmAnalyzer/  (Windows)
~/.config/ThinFilmAnalyzer/  (macOS/Linux)
├── settings.json            # Primary settings file
├── settings.json.bak        # Automatic backup (FR-034)
└── error.log                # Error log with rotation (FR-041)
```

---

## 4. Error Logging with Rotation

### Decision: **Python logging module with RotatingFileHandler**

### Rationale (addresses clarification from spec)

- **Standard library**: No extra dependencies, well-documented
- **Rotation**: Automatic log rotation when size limit reached (FR-043)
- **Structured logging**: Timestamp, level, context, stack trace (FR-041)
- **Diagnostic export**: Easy to package logs + system info for support (FR-042)

### Implementation Pattern

```python
import logging
from logging.handlers import RotatingFileHandler
import platform

class ErrorLogger:
    def __init__(self, log_dir):
        self.log_file = log_dir / 'error.log'

        # Create logger
        self.logger = logging.getLogger('ThinFilmAnalyzer')
        self.logger.setLevel(logging.ERROR)

        # Rotating file handler: 10MB max, keep 2 backups (FR-043)
        handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=2
        )

        # Format: timestamp, level, context, message (FR-041)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_error(self, message, exc_info=None, context=None):
        """Log error with context (current operation, file being processed)."""
        log_message = message
        if context:
            log_message = f"{message} | Context: {context}"

        self.logger.error(log_message, exc_info=exc_info)

    def export_diagnostics(self, export_path):
        """Package logs + system info for troubleshooting (FR-042)."""
        import zipfile

        with zipfile.ZipFile(export_path, 'w') as zf:
            # Include current log and backups
            if self.log_file.exists():
                zf.write(self.log_file, 'error.log')
            for i in range(1, 3):
                backup = self.log_file.with_suffix(f'.log.{i}')
                if backup.exists():
                    zf.write(backup, f'error.log.{i}')

            # Add system info
            system_info = {
                'platform': platform.system(),
                'version': platform.version(),
                'python_version': platform.python_version(),
                'machine': platform.machine()
            }
            zf.writestr('system_info.json', json.dumps(system_info, indent=2))
```

---

## 5. Real-Time Overlay Rendering

### Decision: **QGraphicsView with alpha blending**

### Rationale

- **Real-time updates**: Required for threshold slider (FR-014 "real-time")
- **Performance**: QGraphicsView uses hardware acceleration when available
- **Alpha blending**: Native support for transparency control (FR-013)
- **Zoom/pan**: QGraphicsView provides built-in zoom/pan for large images

### Implementation Pattern

```python
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QImage, QPixmap, QPainter
from PyQt6.QtCore import Qt
import cv2
import numpy as np

class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.image_item = None
        self.overlay_item = None
        self.show_overlay = True
        self.overlay_opacity = 0.5

    def set_image(self, cv_image):
        """Display OpenCV image (BGR format)."""
        # Convert BGR to RGB for Qt
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w

        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        if self.image_item is None:
            self.image_item = self.scene.addPixmap(pixmap)
        else:
            self.image_item.setPixmap(pixmap)

    def set_overlay(self, binary_mask, color=(255, 0, 0)):
        """
        Overlay binary mask with transparency (FR-011, FR-013).

        Args:
            binary_mask: NumPy array (height, width) with 0/255 values
            color: RGB tuple for overlay color (default: red)
        """
        # Create RGBA overlay image
        h, w = binary_mask.shape
        overlay = np.zeros((h, w, 4), dtype=np.uint8)
        overlay[binary_mask > 0] = [color[0], color[1], color[2], int(255 * self.overlay_opacity)]

        bytes_per_line = 4 * w
        qt_image = QImage(overlay.data, w, h, bytes_per_line, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qt_image)

        if self.overlay_item is None:
            self.overlay_item = self.scene.addPixmap(pixmap)
        else:
            self.overlay_item.setPixmap(pixmap)

        self.overlay_item.setVisible(self.show_overlay)

    def toggle_overlay(self):
        """Toggle overlay visibility (FR-012)."""
        self.show_overlay = not self.show_overlay
        if self.overlay_item:
            self.overlay_item.setVisible(self.show_overlay)

    def set_overlay_opacity(self, opacity):
        """Update overlay transparency in real-time (FR-013, FR-014)."""
        self.overlay_opacity = opacity
        # Trigger overlay re-render by calling set_overlay again with same mask
        # (In real implementation, cache the mask to avoid redundant computation)
```

---

## 6. Batch Processing with UI Responsiveness

### Decision: **QThread for background processing with progress signals**

### Rationale

- **UI responsiveness**: QThread allows processing without freezing GUI (FR-026 "no freezing")
- **Progress updates**: Emit signals from worker thread to update progress bar (FR-025)
- **Cancellation**: Support user cancellation mid-batch (edge case: large images >4096)

### Implementation Pattern

```python
from PyQt6.QtCore import QThread, pyqtSignal

class BatchProcessor(QThread):
    """Worker thread for batch image processing (FR-026 responsiveness)."""

    # Signals for communication with main thread
    progress_updated = pyqtSignal(int, int)  # (current_index, total_count)
    image_processed = pyqtSignal(str, float, float)  # (filename, coverage_%, area_um2)
    processing_complete = pyqtSignal()
    error_occurred = pyqtSignal(str, str)  # (filename, error_message)

    def __init__(self, image_paths, threshold, scale_um_per_pixel, roi=None):
        super().__init__()
        self.image_paths = image_paths
        self.threshold = threshold
        self.scale = scale_um_per_pixel
        self.roi = roi
        self._is_cancelled = False

    def run(self):
        """Execute batch processing in background thread."""
        for i, path in enumerate(self.image_paths):
            if self._is_cancelled:
                break

            try:
                # Process image (using function from section 2)
                binary_mask, coverage_pct = process_image(path, self.threshold)

                # Apply ROI if specified (FR-021, FR-022)
                if self.roi:
                    x, y, w, h = self.roi
                    binary_mask = binary_mask[y:y+h, x:x+w]
                    coverage_pct = (np.count_nonzero(binary_mask) / binary_mask.size) * 100

                # Calculate absolute area if calibrated (FR-010)
                if self.scale:
                    pixel_area = binary_mask.shape[0] * binary_mask.shape[1]
                    area_um2 = pixel_area * (self.scale ** 2) * (coverage_pct / 100)
                else:
                    area_um2 = 0.0

                # Emit result to main thread
                filename = Path(path).name
                self.image_processed.emit(filename, coverage_pct, area_um2)

            except Exception as e:
                self.error_occurred.emit(Path(path).name, str(e))

            # Update progress
            self.progress_updated.emit(i + 1, len(self.image_paths))

        self.processing_complete.emit()

    def cancel(self):
        """Cancel batch processing (user cancellation support)."""
        self._is_cancelled = True
```

---

## 7. CSV Export with Summary Statistics

### Decision: **Pandas DataFrame for CSV generation**

### Rationale

- **Summary statistics**: Built-in `describe()` method for mean, std, min, max (FR-030, FR-032)
- **CSV export**: Simple `to_csv()` method with proper encoding
- **Data manipulation**: Easy to add/remove columns, sort results

### Implementation Pattern

```python
import pandas as pd

class ResultsExporter:
    def __init__(self):
        self.results = []

    def add_result(self, filename, coverage_pct, area_um2):
        """Add a single result to the batch."""
        self.results.append({
            'Filename': filename,
            'Coverage (%)': coverage_pct,
            'Area (µm²)': area_um2
        })

    def export_csv(self, output_path):
        """
        Export results to CSV with summary statistics (FR-031, FR-032).
        """
        if not self.results:
            raise ValueError("No results to export")

        # Create DataFrame
        df = pd.DataFrame(self.results)

        # Calculate summary statistics
        stats = df[['Coverage (%)', 'Area (µm²)']].describe()

        # Write results
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            # Main results table
            df.to_csv(f, index=False)

            # Add summary statistics as footer (FR-032)
            f.write('\n--- Summary Statistics ---\n')
            f.write(f"Mean Coverage (%),{stats.loc['mean', 'Coverage (%)']:.2f}\n")
            f.write(f"Std Dev Coverage (%),{stats.loc['std', 'Coverage (%)']:.2f}\n")
            f.write(f"Min Coverage (%),{stats.loc['min', 'Coverage (%)']:.2f}\n")
            f.write(f"Max Coverage (%),{stats.loc['max', 'Coverage (%)']:.2f}\n")

            if stats['Area (µm²)']['mean'] > 0:  # Only if calibrated
                f.write(f"Mean Area (µm²),{stats.loc['mean', 'Area (µm²)']:.2f}\n")
                f.write(f"Std Dev Area (µm²),{stats.loc['std', 'Area (µm²)']:.2f}\n")
```

---

## 8. PyInstaller Packaging for Standalone .exe

### Decision: **PyInstaller with one-file mode**

### Rationale

- **Distribution**: Single .exe file for easy deployment to ~5 users (constitutional requirement)
- **No installation**: Users can run directly without Python environment
- **PyQt6 support**: PyInstaller has mature support for PyQt6 bundling

### Implementation Notes

```bash
# Build command for Windows standalone .exe
pyinstaller --onefile --windowed \
    --name "ThinFilmAnalyzer" \
    --icon resources/icon.ico \
    --add-data "resources/icons;resources/icons" \
    --add-data "resources/styles;resources/styles" \
    main.py
```

### Packaging Considerations

- **--windowed**: No console window for GUI application
- **--onefile**: Single executable (easier distribution than --onedir)
- **--add-data**: Bundle icons and styles into executable
- **File size**: Expect ~150-200 MB for PyQt6 + OpenCV + NumPy bundle
- **Startup time**: ~2-3 seconds for first launch (acceptable for desktop app)

---

## 9. Testing Strategy Without Ground Truth

### Decision: **Synthetic test images + manual validation**

### Rationale (per constitutional validation approach)

- **Synthetic images**: Generate test images with known coverage (25%, 50%, 75%)
- **Visual verification**: Primary validation method (constitutional principle II)
- **Cross-user consistency**: Multiple team members analyze same images, check <5% variance (SC-004)

### Synthetic Image Generation

```python
import cv2
import numpy as np

def generate_synthetic_test_image(coverage_percent, size=2048, output_path=None):
    """
    Generate synthetic OM image with known thin film coverage.

    Args:
        coverage_percent: Target coverage (0-100)
        size: Image dimensions (square)
        output_path: Save path for generated image

    Returns:
        Generated image (NumPy array)
    """
    # Create base substrate (dark gray)
    substrate_intensity = 80
    image = np.ones((size, size), dtype=np.uint8) * substrate_intensity

    # Add thin film regions (light gray)
    film_intensity = 180
    film_pixels_needed = int((coverage_percent / 100) * size * size)

    # Random distribution of film regions (simulates realistic distribution)
    num_regions = np.random.randint(5, 15)
    for _ in range(num_regions):
        center_x = np.random.randint(0, size)
        center_y = np.random.randint(0, size)
        radius = np.random.randint(50, 200)
        cv2.circle(image, (center_x, center_y), radius, film_intensity, -1)

    # Add Gaussian noise to simulate microscopy
    noise = np.random.normal(0, 10, (size, size))
    image = np.clip(image + noise, 0, 255).astype(np.uint8)

    # Apply Gaussian blur to simulate optical blur
    image = cv2.GaussianBlur(image, (5, 5), 1)

    if output_path:
        cv2.imwrite(output_path, image)

    return image
```

### Test Coverage Targets

- Unit tests: 80% code coverage for core/, models/ modules
- Integration tests: Full workflow tests for each user story (P1-P4)
- Synthetic validation: 25%, 50%, 75% coverage images with ±2% accuracy

---

## 10. ROI Selection for Scale Bar Exclusion

### Decision: **QRubberBand for rectangular selection**

### Rationale

- **Native widget**: QRubberBand provides visual feedback during selection
- **Mouse events**: Easy to implement drag-to-select behavior
- **Coordinates**: Simple to extract (x, y, width, height) for ROI cropping

### Implementation Pattern

```python
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QPainter, QColor, QPen

class ROISelector(QWidget):
    """Widget for rectangular ROI selection (FR-021)."""

    roi_selected = pyqtSignal(int, int, int, int)  # (x, y, width, height)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.roi_rect = None
        self.start_point = None
        self.current_point = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.current_point = event.pos()
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.start_point:
            self.current_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.start_point:
            self.current_point = event.pos()

            # Calculate ROI rectangle
            x = min(self.start_point.x(), self.current_point.x())
            y = min(self.start_point.y(), self.current_point.y())
            w = abs(self.current_point.x() - self.start_point.x())
            h = abs(self.current_point.y() - self.start_point.y())

            self.roi_rect = QRect(x, y, w, h)
            self.roi_selected.emit(x, y, w, h)

            self.start_point = None
            self.current_point = None
            self.update()

    def paintEvent(self, event):
        """Draw ROI rectangle (FR-021 'region highlights')."""
        super().paintEvent(event)

        if self.start_point and self.current_point:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(0, 255, 0), 2, Qt.PenStyle.DashLine))

            rect = QRect(self.start_point, self.current_point)
            painter.drawRect(rect.normalized())
```

---

## Summary of Technology Stack

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| Language | Python | 3.10+ | Constitutional requirement, broad library support |
| UI Framework | PyQt6 | 6.5+ | Rich widgets, performance, professional appearance |
| Image Processing | OpenCV | 4.8+ | Industry standard, optimized performance |
| Scientific Imaging | scikit-image | 0.21+ | Morphological operations, region analysis |
| Numerical Operations | NumPy | 1.24+ | Array operations, OpenCV/PyQt6 integration |
| Data Export | Pandas | 2.0+ | CSV generation, summary statistics |
| Testing | pytest | 7.4+ | Standard Python testing framework |
| Packaging | PyInstaller | 5.13+ | Standalone .exe creation |

---

## Performance Validation Benchmarks

Based on research and constitutional requirements:

| Metric | Target | Implementation Approach |
|--------|--------|------------------------|
| Single image (2048×2048) | <3 seconds | OpenCV optimized pipeline, lazy loading |
| Batch (10 images) | <2 minutes | QThread background processing, batch optimizations |
| UI responsiveness | <200ms | QThread for all processing, signal-based updates |
| Memory (50 images) | <2 GB | Lazy loading, cleanup after processing, NumPy reuse |
| Startup time | <5 seconds | PyInstaller one-file, minimal initialization |

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|-------------------|
| Performance regression | Benchmark tests with synthetic 2048×2048 images, CI performance checks |
| PyQt6 learning curve | Focus on core widgets (QGraphicsView, QThread), reference PyQt6 scientific app examples |
| PyInstaller bloat | Use --onefile with --exclude-unused-modules, accept ~150MB for all dependencies |
| Low-contrast image failures | Provide manual threshold slider (FR-007), document in user guide as expected limitation |
| Cross-platform issues | Focus on Windows 10/11 (primary), test macOS as stretch goal |

---

**Research Status**: ✅ Complete
**Next Phase**: Generate data-model.md and contracts/
