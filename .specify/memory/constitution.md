<!--
Sync Impact Report:
Version: 0.0.0 → 1.0.0
Modified principles: N/A (initial creation)
Added sections:
  - Core Principles (5 principles)
  - Technical Constraints
  - Quality & Reliability Standards
  - Governance
Templates requiring updates:
  ✅ plan-template.md - reviewed, constitution check section aligns
  ✅ spec-template.md - reviewed, requirements approach aligns
  ✅ tasks-template.md - reviewed, task organization aligns
Follow-up TODOs: None
-->

# Thin Film Coverage Analyzer Constitution

## Core Principles

### I. User-Centric Simplicity

The application serves internal researchers with basic microscopy knowledge, not
software experts. Every feature must prioritize ease of use over technical
sophistication. Training time must not exceed 15 minutes for new users. The
interface shall be single-window with all primary functions accessible within 2
clicks. Tooltips and keyboard shortcuts are required for all controls.

**Rationale**: Small user base (~5 researchers) means usability issues directly
impact productivity. Complex interfaces create friction and reduce adoption.

### II. Visual Verification Required (NON-NEGOTIABLE)

Every detection result MUST provide visual overlay capabilities showing detected
thin film regions on the original image. Users MUST be able to toggle overlays
on/off and adjust transparency. No results shall be accepted without visual
confirmation capability. This applies to single images and batch processing.

**Rationale**: Without ground truth data, visual verification is the only
validation method. Incorrect detection leads to invalid research conclusions.
Users must be able to verify accuracy before trusting numerical results.

### III. Batch Processing Efficiency

The application MUST handle multiple images (up to 100) in a single session.
Processing time target: <2 minutes for 10 images, <3 seconds per 2048×2048
image. UI MUST remain responsive during batch operations with progress
indicators. Memory usage must not exceed 2 GB for 50-image batches.

**Rationale**: Manual per-image processing is the problem being solved. Batch
efficiency directly determines time savings and user satisfaction.

### IV. Scale Calibration Flexibility

Support multiple calibration methods: manual input (µm/pixel), draw-line tool,
and preset management. Users MUST be able to save and reuse scale presets by
objective name (5x, 10x, 20x, 50x, 100x). Calibration can apply per-image or
to entire batch. ROI selection MUST support exclusion of scale bars and edge
artifacts from coverage calculation.

**Rationale**: Different microscope objectives and imaging conditions require
flexible calibration. Preset reuse eliminates repetitive recalibration across
sessions.

### V. Reliable Processing & Error Handling

Target: >95% successful processing rate. The application MUST gracefully handle
corrupted images, unsupported formats, and processing failures without crashing.
Auto-save settings between sessions. Preserve user data and prevent data loss on
unexpected termination. All errors MUST provide clear user-facing messages with
recovery suggestions.

**Rationale**: Research workflows cannot tolerate data loss or cryptic errors.
Reliability builds trust in automated results.

## Technical Constraints

### Stack Requirements

- **Language**: Python 3.10+ for broad library support and team familiarity
- **UI Framework**: PyQt6 (preferred) or Tkinter for rapid desktop development
- **Image Processing**: OpenCV + scikit-image for proven CV algorithms
- **Data Handling**: NumPy for arrays, Pandas for results export
- **Packaging**: PyInstaller for standalone .exe distribution (Windows 10/11 primary)

### Baseline Algorithm

1. Load image → Convert to grayscale
2. Apply Gaussian blur for noise reduction
3. Apply adaptive or Otsu thresholding (film = lighter, substrate = darker)
4. Morphological operations (open/close) to clean binary mask
5. Calculate: coverage = (film_pixels / total_pixels) × 100
6. Apply scale factor for absolute area (µm²) when calibrated

**Future consideration**: ML-based segmentation for complex samples (out of scope v1.0)

### File Structure

```
thin_film_analyzer/
├── main.py              # Entry point
├── ui/
│   ├── main_window.py   # Main application window
│   ├── widgets.py       # Custom UI components
│   └── roi_selector.py  # ROI selection for scale bar exclusion
├── core/
│   ├── processor.py     # Image processing logic
│   ├── calibration.py   # Scale management
│   ├── detection.py     # Film/substrate segmentation
│   └── export.py        # CSV/image export
├── config/
│   └── presets.json     # Saved scale presets
├── tests/
│   └── synthetic/       # Synthetic test images for validation
└── requirements.txt
```

## Quality & Reliability Standards

### Performance Targets

- Single image (2048×2048): Process in <3 seconds
- Batch (10 images): Complete in <2 minutes
- UI responsiveness: No blocking operations on main thread
- Memory: <2 GB for 50-image batch

### Validation Without Ground Truth

Since reference images with known coverage do not exist, validation relies on:

- **Visual Verification**: Overlay mask on original; user confirms accuracy
- **Synthetic Test Images**: Create artificial images with known coverage (25%, 50%, 75%)
- **Cross-User Consistency**: Multiple team members process same images; variance <5%
- **Manual Spot-Check**: Manually count pixels in small ROI; compare to tool output
- **Threshold Sensitivity**: Document how coverage changes with ±10% threshold adjustment

### Export Requirements

- **CSV Export** (MUST HAVE): Filename, coverage %, area (µm²)
- **Summary Statistics** (SHOULD HAVE): Mean, std dev, min, max across batch
- **Processed Images** (SHOULD HAVE): Export overlays for documentation
- **Excel Export** (COULD HAVE): .xlsx format for advanced analysis

## Governance

### Amendment Process

This constitution supersedes all other development practices. Amendments require:

1. Documentation of proposed change with rationale
2. Impact analysis on existing features and workflows
3. User validation (if affecting UX or workflows)
4. Version increment following semantic versioning

### Versioning Policy

**MAJOR**: Backward incompatible changes to core principles or processing algorithms
**MINOR**: New principle added or significant capability expansion
**PATCH**: Clarifications, wording improvements, non-semantic refinements

### Compliance & Reviews

- All feature specifications MUST demonstrate alignment with Core Principles
- Pull requests violating Visual Verification or Reliability standards will be rejected
- Complexity additions (e.g., new dependencies, architectural patterns) MUST be
  justified with "simpler alternative rejected because..." rationale
- Performance regressions against stated targets require constitution amendment or fix

### Future Enhancements (Deferred)

The following are explicitly OUT OF SCOPE for v1.0 and require constitutional
review before adoption:

- Machine learning-based segmentation
- Automatic scale bar detection from images
- Multi-region analysis (coverage per quadrant)
- Time-series tracking (same sample over time)
- Cloud storage or web-based deployment
- Integration with lab notebook software

**Version**: 1.0.0 | **Ratified**: 2025-12-07 | **Last Amended**: 2025-12-07
