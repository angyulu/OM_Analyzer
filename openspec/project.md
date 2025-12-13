# Project Context

## Purpose
Desktop application for automated thin film coverage analysis from optical microscope images. The application helps researchers quantify thin film coverage on substrates by detecting flakes using adaptive threshold algorithms and calculating coverage percentages.

**Target Users:** Materials science researchers analyzing thin film deposition quality (non-programmers)

**Key Goals:**
- Accurate thin film detection despite optical vignetting (darker edges, brighter center)
- Real-time parameter tuning for various sample types
- Batch processing for multiple images
- Simple, user-friendly interface for non-technical users

## Tech Stack

### Core Technologies
- **Python 3.8+** - Primary language
- **PyQt6 6.5.0+** - Desktop GUI framework
- **OpenCV 4.8.0+** - Image processing and computer vision
- **NumPy 1.24.0+** - Numerical operations
- **Pillow 10.0.0+** - Image loading (TIFF fallback)

### Supporting Libraries
- **scikit-image 0.21.0+** - Advanced image processing algorithms
- **pandas 2.0.0+** - Data export and tabular results
- **pytest 7.4.0+** - Testing framework

### Platform Support
- **Primary:** Windows 10/11
- **Secondary:** macOS/Linux (cross-platform PyQt6)

## Project Conventions

### Code Style
- **PEP 8** compliance for all Python code
- **Type hints** required for function signatures
- **Docstrings** using Google style format (Args, Returns, Raises)
- **Maximum line length:** 100 characters
- **Naming conventions:**
  - `snake_case` for functions, variables, modules
  - `PascalCase` for classes
  - `UPPER_SNAKE_CASE` for constants
- **Import order:** Standard library → Third-party → Local modules

### Architecture Patterns

**Layered Architecture:**
```
UI Layer (PyQt6)
  ↓
Core Logic (Business)
  ↓
Models (Data Entities)
  ↓
Config (Settings)
```

**Key Patterns:**
- **Model-View separation:** UI components (`ui/`) separate from business logic (`core/`)
- **Data classes:** Immutable data models in `models/` (dataclasses preferred)
- **Settings persistence:** JSON-based with platform-specific directories
- **Functional processing pipeline:** Image → Preprocess → Threshold → Morphology → Coverage
- **Single responsibility:** Each module has one clear purpose

**Constitutional Algorithm:**
The core detection follows a fixed pipeline:
1. Load image (grayscale conversion)
2. Noise reduction (optional Gaussian blur)
3. Adaptive threshold with local background subtraction (vignetting correction)
4. Morphological operations (noise cleanup)
5. Coverage calculation (pixel counting)

### Testing Strategy

**Current State:** Minimal testing (v2.0.0)

**Testing Approach:**
- **Unit tests:** Core algorithms in `core/detection.py`, `core/processor.py`
- **Integration tests:** Full processing pipeline with synthetic images
- **Synthetic test images:** Located in `tests/synthetic/` for regression testing
- **Test framework:** pytest
- **Coverage target:** >80% for core algorithms

**Test Naming:** `test_<function_name>_<scenario>` (e.g., `test_apply_threshold_otsu_bright_flakes`)

### Git Workflow

**Branch Strategy:**
- **Main branch:** `001-thin-film-analyzer` (current development branch)
- **Feature branches:** Not currently used (single developer)
- **Release tags:** `v1.0.0`, `v2.0.0`, etc.

**Commit Conventions:**
- Descriptive commit messages (imperative mood)
- No formal convention (e.g., Conventional Commits) currently enforced

## Domain Context

### Materials Science Background
- **Thin films:** Nanometer to micrometer-scale layers deposited on substrates
- **Coverage analysis:** Measuring what percentage of substrate surface is covered by film
- **Sample types:** Various thin film materials (graphene, transition metal dichalcogenides, etc.)
- **Optical microscopy:** Brightfield imaging causes vignetting (optical effect creating non-uniform illumination)

### Key Terminology
- **Flake:** A discrete region of deposited thin film material
- **Substrate:** Background surface (silicon, glass, etc.)
- **Coverage:** Percentage of total area covered by flakes
- **Vignetting:** Darkening at image edges due to optical path differences
- **Adaptive threshold:** Local thresholding method that corrects for non-uniform illumination

### Algorithm Philosophy
- **Detect ALL flakes:** From thinnest (barely visible) to thickest (very bright)
- **Substrate reference:** After vignetting correction, substrate has uniform brightness
- **Brightness hierarchy:** Substrate < Thin flakes < Thick flakes
- **Parameter meaning:** `adaptive_c` = minimum brightness difference between substrate and thinnest detectable flakes

## Important Constraints

### Performance Requirements
- **Single image processing:** <1 second for 2048×2048 images
- **Batch processing:** <120 seconds for 10 images
- **UI responsiveness:** <200ms lag during parameter updates
- **Real-time updates:** All parameters must update instantly
- **Memory usage:** <2GB for 50-image batch

### User Constraints
- **Target users are non-programmers:** Interface must be extremely simple
- **No command-line experience:** Batch files (`run_app.bat`) for launching
- **Minimal setup:** `install.bat` handles all dependencies
- **Windows-centric:** Primary deployment on Windows lab computers

### Technical Constraints
- **No external services:** Fully offline desktop application
- **No database:** Settings stored as JSON files
- **Platform-specific paths:** Use `Path` from `pathlib` for cross-platform compatibility
- **Image formats:** TIFF (via Pillow fallback), PNG, JPG, BMP
- **Maximum batch size:** 100 images (configurable)

### Scientific Constraints
- **Reproducibility:** Same parameters must give identical results
- **Accuracy:** Algorithm must handle vignetting (global thresholds fail)
- **Flexibility:** Different samples require different parameter tuning

## External Dependencies

### None (Fully Offline)
This is a standalone desktop application with no external services, APIs, or cloud dependencies.

### Python Package Dependencies
All dependencies managed via `requirements.txt`:
- PyQt6 (GUI framework)
- opencv-python (image processing)
- Pillow (TIFF loading)
- scikit-image (advanced algorithms)
- numpy (numerical operations)
- pandas (data export)
- pytest (testing)

### System Dependencies
- **Python 3.8+** (installed via `install.bat` for end users)
- **Operating System:** Windows 10/11, macOS, or Linux with GUI support
