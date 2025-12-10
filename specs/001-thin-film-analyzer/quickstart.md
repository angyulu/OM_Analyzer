# Quickstart Guide
## Thin Film Coverage Analyzer - Developer Onboarding

**Feature**: 001-thin-film-analyzer
**Last Updated**: 2025-12-07
**Audience**: New developers joining the project

---

## Overview

The Thin Film Coverage Analyzer is a Python desktop application built with PyQt6 for analyzing thin film coverage from optical microscope images. This guide will get you from zero to running the application in under 30 minutes.

---

## Prerequisites

- Python 3.10 or higher
- Windows 10/11 (primary), macOS 11+ (secondary)
- Git for version control
- 2 GB RAM minimum, 4 GB recommended

---

## Quick Setup (5 minutes)

### 1. Clone Repository

```bash
git clone <repository-url>
cd OM_Analyzer/OM_V0
git checkout 001-thin-film-analyzer
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**requirements.txt** contents:
```
PyQt6>=6.5.0
opencv-python>=4.8.0
scikit-image>=0.21.0
numpy>=1.24.0
pandas>=2.0.0
pytest>=7.4.0
```

### 4. Verify Installation

```bash
python -c "import PyQt6, cv2, skimage, numpy, pandas; print('All dependencies installed successfully!')"
```

---

## Running the Application (1 minute)

### Development Mode

```bash
python thin_film_analyzer/main.py
```

Expected output:
```
Thin Film Analyzer v1.0.0
Loading settings from: C:\Users\<username>\AppData\Roaming\ThinFilmAnalyzer\settings.json
Application started successfully.
```

### First Launch

On first launch, the application will:
1. Create settings directory in user AppData
2. Initialize default settings (threshold=128, transparency=0.5)
3. Display empty main window ready for image loading

---

## Project Structure Tour (10 minutes)

### Key Directories

```
thin_film_analyzer/
├── main.py              # ← START HERE: Application entry point
├── ui/                  # PyQt6 user interface components
│   ├── main_window.py   # Main application window
│   ├── image_viewer.py  # Image display with overlay
│   └── widgets.py       # Custom UI widgets
├── core/                # Business logic (no UI dependencies)
│   ├── processor.py     # Image processing pipeline
│   ├── detection.py     # Thin film detection algorithms
│   ├── calibration.py   # Scale preset management
│   └── export.py        # CSV/image export
├── models/              # Data entities (see data-model.md)
│   ├── image.py
│   ├── scale_preset.py
│   └── detection_result.py
├── tests/               # pytest test suite
│   ├── unit/            # Unit tests for core/
│   ├── integration/     # Full workflow tests
│   └── synthetic/       # Synthetic test image generation
└── config/              # Configuration and defaults
    └── defaults.py
```

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│           main.py (entry point)             │
└─────────────────┬───────────────────────────┘
                  │
      ┌───────────▼──────────┐
      │  ui/main_window.py   │ ◄─── User interactions
      │  (PyQt6 GUI)         │
      └───────────┬──────────┘
                  │
      ┌───────────▼──────────┐
      │ core/processor.py    │ ◄─── Image processing logic
      │ core/detection.py    │
      │ core/calibration.py  │
      └───────────┬──────────┘
                  │
      ┌───────────▼──────────┐
      │ models/              │ ◄─── Data entities
      │ (Image, Result, etc) │
      └──────────────────────┘
```

---

## Core Workflows (10 minutes)

### Workflow 1: Single Image Analysis (P1 - MVP)

```python
# User Story 1: Load image → Process → Verify with overlay → Get coverage

# Step 1: Load image
from models.image import Image, ImageStatus
from pathlib import Path

image_path = Path("test_data/sample.png")
image = Image(
    filename=image_path.name,
    file_path=image_path,
    dimensions=(2048, 2048),
    format="PNG",
    status=ImageStatus.UNPROCESSED
)

# Step 2: Process image
from core.processor import process_image

binary_mask, coverage_pct = process_image(
    image_path=str(image_path),
    threshold_value=128,  # or None for auto (Otsu)
    noise_reduction=True
)

# Step 3: Generate overlay for visual verification
from core.overlay import generate_overlay

overlay_image = generate_overlay(
    original_image=cv2.imread(str(image_path)),
    binary_mask=binary_mask,
    opacity=0.5,
    color=(255, 0, 0)  # Red overlay
)

# Step 4: Display result
print(f"Coverage: {coverage_pct:.2f}%")

# Step 5: Create detection result
from models.detection_result import DetectionResult
from datetime import datetime

result = DetectionResult(
    image_ref=image,
    coverage_percentage=coverage_pct,
    area_um2=0.0,  # No calibration yet
    threshold_value=128,
    roi_coords=None,
    film_pixel_count=np.count_nonzero(binary_mask),
    total_pixel_count=binary_mask.size,
    processing_timestamp=datetime.now()
)
```

### Workflow 2: Scale Calibration (P2)

```python
# User Story 2: Save/load scale presets for absolute area calculation

from models.scale_preset import ScalePreset
from core.calibration import CalibrationManager
from datetime import datetime

# Create calibration manager
calib_mgr = CalibrationManager(settings_dir=Path("..."))

# Option A: Manual input
preset = ScalePreset(
    name="10x objective",
    scale_um_per_pixel=0.65,  # measured value
    created_date=datetime.now(),
    objective_ref="10x"
)

# Save preset (with duplicate check per FR-018)
if calib_mgr.preset_exists(preset.name):
    # Show confirmation dialog in UI: "Preset exists. Overwrite?"
    user_confirmed = True  # From dialog
    if user_confirmed:
        calib_mgr.save_preset(preset, overwrite=True)
else:
    calib_mgr.save_preset(preset)

# Option B: Draw-line calibration (in UI)
# User draws line on known feature (e.g., 100 µm scale bar)
line_length_pixels = 154  # from mouse drag
known_length_um = 100.0   # user input
scale = known_length_um / line_length_pixels  # 0.65 µm/pixel

# Load preset and use for processing
loaded_preset = calib_mgr.load_preset("10x objective")
scale_value = loaded_preset.scale_um_per_pixel

# Recalculate area with calibration
area_um2 = result.total_pixel_count * (scale_value ** 2) * (result.coverage_percentage / 100)
result.area_um2 = area_um2
print(f"Coverage: {result.coverage_percentage:.2f}% ({area_um2:.2f} µm²)")
```

### Workflow 3: Batch Processing (P3)

```python
# User Story 3: Load multiple images → Process all → Export CSV

from models.batch_session import BatchSession, BatchStatistics
from core.export import ResultsExporter

# Create batch session
session = BatchSession(
    image_refs=[image1, image2, image3],  # List of Image objects
    scale_calibration=0.65,  # µm/pixel (or None)
    threshold_setting=128,
    roi_settings=None
)

# Process all images (in background thread via QThread in real app)
results = []
for img in session.image_refs:
    binary_mask, coverage_pct = process_image(img.file_path, session.threshold_setting)

    # Calculate area if calibrated
    if session.scale_calibration:
        area_um2 = binary_mask.size * (session.scale_calibration ** 2) * (coverage_pct / 100)
    else:
        area_um2 = 0.0

    result = DetectionResult(
        image_ref=img,
        coverage_percentage=coverage_pct,
        area_um2=area_um2,
        threshold_value=session.threshold_setting,
        roi_coords=session.roi_settings,
        film_pixel_count=np.count_nonzero(binary_mask),
        total_pixel_count=binary_mask.size,
        processing_timestamp=datetime.now()
    )
    results.append(result)

# Calculate summary statistics (FR-030)
session.summary_stats = BatchStatistics.calculate(results)

# Export to CSV (FR-031, FR-032)
exporter = ResultsExporter()
for result in results:
    exporter.add_result(
        filename=result.image_ref.filename,
        coverage_pct=result.coverage_percentage,
        area_um2=result.area_um2
    )

exporter.export_csv(output_path=Path("results.csv"))
print(f"Exported {len(results)} results with summary statistics")
```

---

## Running Tests (5 minutes)

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test module
pytest tests/unit/test_processor.py -v

# Run with coverage report
pytest tests/unit/ --cov=thin_film_analyzer --cov-report=html
```

### Integration Tests

```bash
# Full workflow tests
pytest tests/integration/ -v
```

### Generate Synthetic Test Images

```bash
# Create test images with known coverage (25%, 50%, 75%)
python tests/synthetic/generate_test_images.py

# This creates:
# tests/synthetic/coverage_25pct.png
# tests/synthetic/coverage_50pct.png
# tests/synthetic/coverage_75pct.png
```

---

## Common Development Tasks

### Task 1: Add a New Image Processing Algorithm

**Example**: Implement Canny edge detection as alternative to thresholding

1. Add function to `core/detection.py`:
   ```python
   def detect_edges_canny(image: np.ndarray, low_threshold: int, high_threshold: int) -> np.ndarray:
       """Alternative detection using Canny edge detection."""
       edges = cv2.Canny(image, low_threshold, high_threshold)
       return edges
   ```

2. Add unit test in `tests/unit/test_detection.py`:
   ```python
   def test_canny_detection():
       test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
       edges = detect_edges_canny(test_image, 50, 150)
       assert edges.shape == test_image.shape
       assert edges.dtype == np.uint8
   ```

3. Run tests:
   ```bash
   pytest tests/unit/test_detection.py::test_canny_detection -v
   ```

### Task 2: Add a New UI Widget

**Example**: Create a custom threshold slider widget

1. Create widget in `ui/widgets.py`:
   ```python
   from PyQt6.QtWidgets import QWidget, QSlider, QLabel, QVBoxLayout
   from PyQt6.QtCore import Qt, pyqtSignal

   class ThresholdSlider(QWidget):
       value_changed = pyqtSignal(int)  # Emit new threshold value

       def __init__(self, parent=None):
           super().__init__(parent)
           layout = QVBoxLayout()

           self.label = QLabel("Threshold: 128")
           self.slider = QSlider(Qt.Orientation.Horizontal)
           self.slider.setRange(0, 255)
           self.slider.setValue(128)
           self.slider.valueChanged.connect(self._on_value_changed)

           layout.addWidget(self.label)
           layout.addWidget(self.slider)
           self.setLayout(layout)

       def _on_value_changed(self, value):
           self.label.setText(f"Threshold: {value}")
           self.value_changed.emit(value)
   ```

2. Use in main window `ui/main_window.py`:
   ```python
   from ui.widgets import ThresholdSlider

   class MainWindow(QMainWindow):
       def __init__(self):
           super().__init__()
           self.threshold_slider = ThresholdSlider()
           self.threshold_slider.value_changed.connect(self.on_threshold_changed)
           # Add to layout...

       def on_threshold_changed(self, new_threshold):
           print(f"Threshold changed to: {new_threshold}")
           # Trigger reprocessing with new threshold
   ```

### Task 3: Debug Image Processing Issues

```bash
# Enable detailed logging
export PYTHONVERBOSE=1  # macOS/Linux
set PYTHONVERBOSE=1     # Windows

# Run with debugger
python -m pdb thin_film_analyzer/main.py

# Or use breakpoint() in code
def process_image(image_path, threshold_value=None, noise_reduction=True):
    img = cv2.imread(image_path)
    breakpoint()  # Debugger stops here
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ...
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'PyQt6'"

**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "cv2.error: OpenCV(4.8.0) error: (-215:Assertion failed) !_src.empty()"

**Solution**: Image file doesn't exist or is corrupted
```python
# Add validation before processing
if not Path(image_path).exists():
    raise FileNotFoundError(f"Image not found: {image_path}")

img = cv2.imread(str(image_path))
if img is None:
    raise ValueError(f"Unable to load image: {image_path}")
```

### Issue: "Settings file corrupted, using defaults"

**Solution**: Settings backup recovery (FR-036)
```bash
# Manually restore from backup
cd %APPDATA%\ThinFilmAnalyzer  # Windows
cd ~/.config/ThinFilmAnalyzer  # macOS

# Check backup exists
ls -la settings.json.bak

# Restore from backup
cp settings.json.bak settings.json
```

---

## Next Steps

1. **Read the spec**: Review `spec.md` for full requirements
2. **Check the constitution**: See `.specify/memory/constitution.md` for design principles
3. **Explore data model**: Read `data-model.md` for entity relationships
4. **Run the app**: Launch and try loading test images from `tests/synthetic/`
5. **Write a test**: Pick a user story and write an integration test
6. **Join standup**: Ask questions in team chat or next sync

---

## Useful Commands Reference

```bash
# Development
python thin_film_analyzer/main.py         # Run app
pytest tests/ -v                          # Run all tests
pytest --cov=thin_film_analyzer           # Coverage report

# Code Quality
black thin_film_analyzer/                 # Auto-format code
pylint thin_film_analyzer/                # Linting
mypy thin_film_analyzer/                  # Type checking

# Build & Package
pyinstaller --onefile --windowed main.py  # Create standalone .exe

# Documentation
python -m pydoc -b                        # Open documentation browser
```

---

## Resources

- **Spec**: `specs/001-thin-film-analyzer/spec.md`
- **Plan**: `specs/001-thin-film-analyzer/plan.md`
- **Research**: `specs/001-thin-film-analyzer/research.md`
- **Data Model**: `specs/001-thin-film-analyzer/data-model.md`
- **Constitution**: `.specify/memory/constitution.md`

- **PyQt6 Docs**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **OpenCV Docs**: https://docs.opencv.org/4.8.0/
- **scikit-image Docs**: https://scikit-image.org/docs/stable/

---

**Quickstart Status**: ✅ Complete
**Estimated Onboarding Time**: ~30 minutes from zero to first contribution
