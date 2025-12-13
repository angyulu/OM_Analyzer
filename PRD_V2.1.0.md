# Product Requirements Document: Thin Film Analyzer v2.1.0

**Document Version**: 1.1 (Corrected Architecture)
**Last Updated**: 2025-12-13
**Product**: Thin Film Coverage Analyzer
**Target Release**: v2.1.0

**CRITICAL CORRECTIONS in v1.1**:
- V2 layer detection is MANDATORY hybrid mode (always uses V1 as mask)
- V2 only needs **2 thresholds** (T1, T2), not 3
- V2 ONLY processes pixels where V1 detected film
- Auto-detection algorithms analyze film pixels only

---

## Executive Summary

The Thin Film Analyzer is a desktop application for automated analysis of thin film coverage from optical microscope images. Version 2.1.0 will build upon the stable v1.0 binary detection system by adding advanced multi-layer detection capabilities through a **mandatory hybrid V1+V2 pipeline**. V1 detects film regions, V2 classifies layer thickness within those regions.

---

## Table of Contents

1. [Current State (v1.0)](#current-state-v10)
2. [Proposed Features (v2.1.0)](#proposed-features-v210)
3. [Technical Architecture](#technical-architecture)
4. [User Interface Changes](#user-interface-changes)
5. [Implementation Priority](#implementation-priority)
6. [Success Metrics](#success-metrics)
7. [Risks and Mitigation](#risks-and-mitigation)

---

## Current State (v1.0)

### Existing Features

#### Core Detection (v1.0)
- ✅ **Binary thin film detection** using adaptive thresholding
- ✅ **Otsu's method** for automatic threshold calculation
- ✅ **Manual threshold override** (0-255 slider)
- ✅ **Adaptive local thresholding** for vignetting correction
- ✅ **Coverage percentage calculation**
- ✅ **Real-time visual overlay** (red mask with adjustable transparency)

#### Image Processing (v1.0)
- ✅ **Noise reduction** (Gaussian blur preprocessing)
- ✅ **Morphological operations** (close/open for noise cleanup)
- ✅ **Multiple format support** (TIFF, PNG, JPG, BMP)
- ✅ **Drag-and-drop** image loading

#### User Interface (v1.0)
- ✅ **Parameter tuning panel**:
  - Threshold slider (0-255)
  - Adaptive threshold toggle
  - Adaptive block size (3-301)
  - Adaptive C constant (1-50)
  - Blur kernel size (1-15)
  - Morphological close kernel (0-10)
  - Morphological open kernel (0-10)
- ✅ **Real-time processing** (parameters update instantly)
- ✅ **Overlay transparency control** (0-100%)
- ✅ **Batch image navigation** (Previous/Next buttons)

#### Settings & Data
- ✅ **Settings persistence** (JSON-based configuration)
- ✅ **Cross-platform settings** (Windows/macOS/Linux)
- ✅ **Processing time display**

### Current Limitations (v1.0)

❌ **No layer thickness differentiation** - Cannot distinguish monolayer, bilayer, trilayer
❌ **No batch CSV export** - Results not exportable for multiple images
❌ **No overlay export** - Cannot save processed images with overlays
❌ **No LAB color space analysis** - Only grayscale thresholding
❌ **No auto-detection algorithms** - Manual threshold selection required
❌ **Single detection mode** - Cannot combine multiple detection methods

---

## Proposed Features (v2.1.0)

### 1. Hybrid V1+V2 Pipeline (MANDATORY Architecture)

#### Problem Statement
Current v1.0 only detects "film present" vs "no film" but cannot distinguish between different layer thicknesses (monolayer, bilayer, trilayer). Optical microscopy shows different contrast levels for different thicknesses, which can be quantified using LAB color space L-channel (lightness) analysis.

#### Solution: Two-Stage Hybrid Pipeline

**CRITICAL**: V2 layer detection **ONLY** processes pixels where V1 detected film. This is NOT optional - it's the core architecture.

**Stage 1 - V1 Film Detection**:
```python
binary_mask = process_v1(image)  # 0 = substrate, 1 = film present
```

**Stage 2 - V2 Layer Classification** (only for film pixels):
```python
# ONLY process pixels where binary_mask == 1
for pixel in film_region:
    L_value = LAB_L_channel[pixel]

    if L_value < T1:
        monolayer (1-2 atomic layers)
    elif T1 <= L_value < T2:
        bilayer (2-3 atomic layers)
    else:  # L_value >= T2
        trilayer (3+ atomic layers)

# Substrate pixels (binary_mask == 0) are NEVER processed by V2
```

**Key Features**:
- ✨ **V1 as mask for V2** - V2 only analyzes V1-detected film regions
- ✨ **Two thresholds (T1, T2)** - Not three! Substrate already excluded by V1
- ✨ **LAB color space conversion** for accurate lightness analysis
- ✨ **Vignetting correction** using local L-channel normalization
- ✨ **Color-coded overlay**:
  - Red = Monolayer
  - Blue = Bilayer
  - Green = Trilayer
- ✨ **Per-layer coverage statistics**:
  - Total coverage %
  - Monolayer coverage %
  - Bilayer coverage %
  - Trilayer coverage %

**Technical Implementation**:
- New file: `thin_film_analyzer/core/detection.py`
- New function: `detect_lab_layers(binary_mask, image, t1, t2, apply_vignetting_correction=True)`
  - **IMPORTANT**: Takes binary_mask as first parameter to restrict analysis
- Integration with existing `processor.py` as `process_image_hybrid()`

**Bug Fixes Required** (from previous development):
- 🐛 **Bug Fix #1**: Must respect V1 manual threshold when "Use Adaptive Threshold" is unchecked
- 🐛 **Bug Fix #2**: Ensure overlay visibility toggle works correctly

---

### 2. Auto-Detection Algorithms for T1 and T2

#### Problem Statement
Manually tuning T1, T2 thresholds for every image is time-consuming. Different images may require different algorithms depending on illumination, contrast, and sample characteristics.

#### Solution: Algorithm Dropdown with Auto-Detect

**Four Algorithms**:

1. **K-means Clustering** (Recommended default)
   - Groups L-channel values into **3 clusters** (mono, bi, tri)
   - Robust to varying illumination
   - Works well for most images

2. **Percentile-Based Thresholding**
   - Uses 33rd, 66th percentiles of film pixels
   - Simple statistical approach
   - Consistent across similar samples

3. **Histogram Peak Detection**
   - Finds peaks in L-channel histogram of film pixels
   - Best for images with distinct intensity modes
   - Good for high-contrast samples

4. **Otsu Multi-Threshold**
   - Extension of Otsu's method to **2 thresholds**
   - Optimal for images with clear intensity peaks
   - Mathematical optimization

**UI Implementation**:
- Dropdown: "Auto-Detection Algorithm"
- Button: "Auto-Detect Thresholds"
- Behavior:
  - Click "Auto-Detect" → Algorithm runs **only on V1 film pixels**
  - T1, T2 sliders auto-update
  - Image reprocesses with new thresholds
  - User can manually fine-tune after auto-detect

**Technical Implementation**:
- New file: `thin_film_analyzer/core/detection_algorithms.py`
- Functions:
  - `detect_thresholds_kmeans(binary_mask, image) → (t1, t2)`
  - `detect_thresholds_percentile(binary_mask, image) → (t1, t2)`
  - `detect_thresholds_histogram(binary_mask, image) → (t1, t2)`
  - `detect_thresholds_otsu_multi(binary_mask, image) → (t1, t2)`
- **CRITICAL**: All functions take binary_mask to only analyze film pixels

---

### 3. Adaptive Bias Parameter

#### Problem Statement
Different samples have different signal-to-noise ratios. The adaptive threshold C constant may be too aggressive or too conservative for some images.

#### Solution: Fine-Tuning Bias Control

**Adaptive Bias**:
```python
effective_threshold = adaptive_c + adaptive_bias
# adaptive_bias range: -10 to +10
```

**UI Implementation**:
- **CRITICAL**: Adaptive Bias must be in **V1 Processing panel** (not V2)
- Spinbox: "Adaptive Bias" (-10 to +10, default 0)
- Tooltip:
  ```
  Fine-tune adaptive threshold sensitivity:
  • Negative values (-5 to -1): Detect MORE film (weaker signal)
  • Zero (0): Default behavior
  • Positive values (+1 to +5): Detect LESS film (stronger signal required)
  ```

**Location Fix** (from previous bug):
- 🐛 **Bug Fix #3**: Move adaptive bias from V2 panel to V1 panel in `main_window.py`

---

### 5. Batch Processing & Export

#### Problem Statement
Researchers often process 10-100 images from the same sample. Current v1.0 requires manual processing and no data export.

#### Solution: Batch Processing with CSV Export

**Batch Processing Workflow**:
1. Load multiple images (multi-select in file dialog)
2. Configure V1 settings (film detection parameters)
3. Configure V2 settings (T1, T2 thresholds for layer classification)
4. **Lock thresholds** (new feature - ensures consistency)
5. Process all images with same settings
6. Export results to CSV

**Threshold Locking**:
- New button: "🔓 Unlock Thresholds" / "🔒 Lock Thresholds"
- When locked:
  - T1, T2 sliders disabled (only 2 thresholds!)
  - All images use same V1 + V2 parameters
  - Ensures consistency across batch

**CSV Export Format**:
```csv
filename,coverage_percentage,mono_coverage,bi_coverage,tri_coverage
image1.png,45.23,15.67,20.45,9.11
image2.png,38.91,12.34,18.22,8.35
image3.png,52.10,18.90,22.34,10.86

SUMMARY STATISTICS
Mean Coverage (%),45.41
Std Dev Coverage (%),6.62
Min Coverage (%),38.91
Max Coverage (%),52.10

Mean Monolayer (%),15.64
Std Dev Monolayer (%),3.29
...
```

**Overlay Image Export**:
- Menu: Batch → Export Overlay Images...
- Saves processed images with color-coded overlays
- Filename format: `original_name_overlay.png`

**Technical Implementation**:
- Update: `thin_film_analyzer/models/batch_session.py` (add threshold locking)
- Update: `thin_film_analyzer/core/export.py` (CSV with layer stats)
- New menu items: "Process All Images" (Ctrl+P), "Export Results to CSV" (Ctrl+E)

---

### 6. UI/UX Improvements

#### Processing Feedback

**Problem**: Users cannot tell when system is processing (2-5 seconds per image)

**Solution**: Processing Indicator
- ✨ **Wait cursor** during processing
- ✨ **Status message**: "Processing..."
- ✨ **Error handling**: Restore normal cursor on error

**Implementation**:
```python
# In main_window.py
QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
try:
    # ... processing ...
finally:
    QApplication.restoreOverrideCursor()
```

#### Overlay Visibility

**Problem**: "Show Overlay" checkbox doesn't hide overlay correctly

**Solution**: Fix overlay visibility logic
- 🐛 **Bug Fix #3**: Add `else` clause to explicitly hide overlay when unchecked

**Implementation**:
```python
if self.show_overlay_checkbox.isChecked():
    # Show overlay
    self.image_viewer.set_overlay(overlay_image, opacity)
else:
    # CRITICAL: Must explicitly hide
    self.image_viewer.set_overlay(None, 0)
```

---

## Technical Architecture

### New Files to Create

```
thin_film_analyzer/
├── core/
│   ├── detection.py              # NEW: LAB layer detection
│   ├── detection_algorithms.py   # NEW: Auto-detection algorithms
│   ├── processor.py              # UPDATE: Add hybrid mode
│   └── overlay.py                # UPDATE: Add color-coded layers
├── models/
│   ├── detection_result.py       # UPDATE: Add layer fields
│   └── batch_session.py          # UPDATE: Add threshold locking
└── ui/
    └── main_window.py            # UPDATE: Add V2 panel, hybrid mode
```

### Key Function Signatures

```python
# detection.py
def detect_lab_layers(
    binary_mask: np.ndarray,  # V1 film detection result
    image: np.ndarray,
    t1: int,  # Mono/Bi boundary
    t2: int,  # Bi/Tri boundary
    apply_vignetting_correction: bool = True
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Detect monolayer, bilayer, trilayer regions using LAB L-channel.

    CRITICAL: Only analyzes pixels where binary_mask == 1 (V1 detected film).

    Args:
        binary_mask: V1 binary detection result (0=substrate, 1=film)
        image: Original image
        t1: Threshold between monolayer and bilayer
        t2: Threshold between bilayer and trilayer

    Returns:
        layer_mask: np.ndarray with values {0: substrate, 1: mono, 2: bi, 3: tri}
                    Substrate pixels (binary_mask==0) remain 0
        stats: {
            'total_coverage': float,      # From V1 binary mask
            'mono_coverage': float,
            'bi_coverage': float,
            'tri_coverage': float
        }
    """
    pass

# processor.py
def process_image_hybrid(
    image_path: str,
    # V1 parameters
    use_adaptive: bool = True,
    threshold_value: Optional[int] = None,
    adaptive_block_size: int = 200,
    adaptive_c: int = 5,
    adaptive_bias: int = 0,
    # V2 parameters (ONLY 2 THRESHOLDS)
    t1: int = 85,  # Mono/Bi boundary
    t2: int = 170,  # Bi/Tri boundary
    # Other parameters
    noise_reduction: bool = True,
    blur_kernel: int = 3,
    morph_close: int = 2,
    morph_open: int = 2
) -> Tuple[np.ndarray, Dict[str, float], np.ndarray]:
    """
    Hybrid V1+V2 processing pipeline.

    Step 1: V1 detects film boundary
    Step 2: V2 classifies layers ONLY within V1 film regions

    Returns:
        binary_mask: V1 film detection mask (0=substrate, 1=film)
        stats: Combined V1+V2 statistics with layer breakdown
        layer_mask: V2 layer classification (0=substrate, 1=mono, 2=bi, 3=tri)
    """
    pass

# detection_algorithms.py
def detect_thresholds_kmeans(
    binary_mask: np.ndarray,  # Only analyze film pixels
    image: np.ndarray
) -> Tuple[int, int]:  # Returns T1, T2 (not T3!)
    """
    Auto-detect T1, T2 using K-means clustering.

    CRITICAL: Only analyzes pixels where binary_mask == 1.
    """
    pass
```

### DetectionResult Model Extension

```python
# models/detection_result.py
@dataclass
class DetectionResult:
    # Existing v1.0 fields
    coverage_percentage: float
    processing_time_ms: float
    threshold_value: int

    # NEW v2.1.0 fields (always populated in hybrid mode)
    mono_coverage: Optional[float] = None
    bi_coverage: Optional[float] = None
    tri_coverage: Optional[float] = None
    thresholds: Optional[Tuple[int, int]] = None  # (T1, T2) - ONLY 2 THRESHOLDS
```

---

## User Interface Changes

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Thin Film Analyzer v2.1.0                        [_ □ X]    │
├─────────────────────────────────────────────────────────────┤
│ File   Edit   View   Batch   Help                           │
├──────────────┬──────────────────────────────────────────────┤
│              │                                               │
│  V1 PROCESS  │           IMAGE VIEWER                        │
│  ┌────────┐  │                                               │
│  │☑ Adapt │  │      [Drag & Drop Image Here]                │
│  │Thresh  │  │                                               │
│  │        │  │      ┌─────────────────────┐                 │
│  │Thresh: │  │      │  [Image Preview]    │                 │
│  │ [===] │  │      │                     │                 │
│  │        │  │      │  Coverage: 45.2%    │                 │
│  │☑ Noise │  │      │  Processing: 1.2s   │                 │
│  │Reduc   │  │      └─────────────────────┘                 │
│  │        │  │                                               │
│  │Blur: 3 │  │      ☑ Show Overlay  Opacity: [======]       │
│  │Close:2 │  │                                               │
│  │Open: 2 │  │      [< Previous]  Image 1 of 5  [Next >]    │
│  │        │  │                                               │
│  │Adap    │  │                                               │
│  │Block:  │  │                                               │
│  │ 200    │  │                                               │
│  │        │  │                                               │
│  │Adap C: │  │                                               │
│  │ 5      │  │                                               │
│  │        │  │                                               │
│  │⭐Adap   │  │                                               │
│  │Bias: 0 │  │                                               │
│  └────────┘  │                                               │
│              │                                               │
│  V2 LAYERS   │                                               │
│  ┌────────┐  │                                               │
│  │Layer   │  │                                               │
│  │Classif │  │                                               │
│  │        │  │                                               │
│  │Algo:   │  │                                               │
│  │[Kmeans]│  │                                               │
│  │        │  │                                               │
│  │[Auto-  │  │                                               │
│  │Detect] │  │                                               │
│  │        │  │                                               │
│  │T1:[==] │  │  ← Mono/Bi boundary                          │
│  │T2:[==] │  │  ← Bi/Tri boundary (ONLY 2!)                 │
│  │        │  │                                               │
│  │[🔓Lock]│  │                                               │
│  │Thresh  │  │                                               │
│  │        │  │                                               │
│  │Results:│  │                                               │
│  │Total:45%│  │  ← From V1                                   │
│  │Mono: 15%│  │  ← From V2 within V1 film                    │
│  │Bi:   20%│  │                                               │
│  │Tri:  10%│  │                                               │
│  └────────┘  │                                               │
└──────────────┴──────────────────────────────────────────────┘
```

### Panel Organization

**V1 Processing Panel** (Always visible):
- ☑ Use Adaptive Threshold
- Threshold slider (0-255)
- ☑ Enable Noise Reduction
- Blur Kernel (1-15)
- Morph Close (0-10)
- Morph Open (0-10)
- Adaptive Block (3-301)
- Adaptive C (1-50)
- ⭐ **Adaptive Bias (-10 to +10)** ← NEW, MUST BE HERE

**V2 Layer Classification Panel** (Always visible):
- Algorithm Dropdown (K-means, Percentile, Histogram, Otsu) ← NEW
- [Auto-Detect Thresholds] Button ← NEW
- T1 Slider (0-255) - Monolayer/Bilayer boundary ← NEW
- T2 Slider (0-255) - Bilayer/Trilayer boundary ← NEW
- [🔓 Unlock Thresholds] Button ← NEW (for batch consistency)
- Results:
  - Total Coverage: XX% (from V1)
  - Monolayer: XX% (from V2 within V1 film) ← NEW
  - Bilayer: XX% ← NEW
  - Trilayer: XX% ← NEW

**Note**: No toggle for hybrid mode - it's ALWAYS hybrid (V1 film detection + V2 layer classification)

---

## Implementation Priority

### Phase 1: Core v2.0 Features (Highest Priority)
**Goal**: Get basic LAB layer detection working

1. ✅ Create `detection.py` with `detect_lab_layers()` function
2. ✅ Update `processor.py` with `process_image_lab()` function
3. ✅ Update `detection_result.py` with layer fields
4. ✅ Update `overlay.py` to generate color-coded overlays
5. ✅ Add V2 panel to `main_window.py` with T1/T2/T3 sliders
6. ✅ Test on sample images

**Success Criteria**:
- Can detect and display mono/bi/tri layers
- Color overlay shows correct layer classification
- Statistics show per-layer coverage percentages

---

### Phase 2: Auto-Detection Algorithms
**Goal**: Reduce manual threshold tuning

1. ✅ Create `detection_algorithms.py`
2. ✅ Implement all 4 algorithms (K-means, Percentile, Histogram, Otsu)
3. ✅ Add algorithm dropdown to V2 panel
4. ✅ Add "Auto-Detect" button functionality
5. ✅ Test algorithms on diverse image types

**Success Criteria**:
- Auto-detect produces reasonable thresholds for 80% of images
- User can still manually fine-tune after auto-detect

---

### Phase 3: Hybrid Mode & Bug Fixes
**Goal**: Combine V1+V2 strengths and fix critical bugs

1. ✅ Implement `process_image_hybrid()` in `processor.py`
2. ✅ Add "Enable Hybrid Mode" checkbox to UI
3. ✅ **Bug Fix #1**: Hybrid respects V1 manual threshold
4. ✅ **Bug Fix #2**: Move adaptive bias to V1 panel
5. ✅ **Bug Fix #3**: Fix overlay visibility toggle
6. ✅ **Bug Fix #4**: Add processing indicator (wait cursor)
7. ✅ Update CHANGELOG.md

**Success Criteria**:
- Hybrid mode correctly masks V2 detection by V1 results
- All bug fixes verified in testing

---

### Phase 4: Batch Processing & Export
**Goal**: Enable multi-image workflows

1. ✅ Add threshold locking to `batch_session.py`
2. ✅ Update CSV export in `export.py` for layer stats
3. ✅ Add "Process All Images" menu item
4. ✅ Add "Export Results to CSV" menu item
5. ✅ Add "Export Overlay Images" menu item
6. ✅ Create batch progress dialog

**Success Criteria**:
- Can process 50+ images with locked thresholds
- CSV export includes all layer statistics
- Overlay images saved correctly

---

### Phase 5: Documentation & Distribution
**Goal**: Prepare for user release

1. ✅ Update README.md with v2.1.0 features
2. ✅ Update SETUP_GUIDE.md with new UI elements
3. ✅ Update QUICK_REFERENCE.md with layer detection parameters
4. ✅ Create user guide for LAB layer detection
5. ✅ Test installation on clean machines (Windows/macOS)
6. ✅ Create distribution package (~5MB ZIP)

**Success Criteria**:
- Documentation covers all new features
- Installation tested on Windows 10/11 and macOS 11+
- Distribution package ready to share

---

## Success Metrics

### Technical Metrics
- **Detection Accuracy**: Layer classification matches manual inspection for >90% of pixels
- **Processing Speed**: <5 seconds per 2000x1500 pixel image (on modern hardware)
- **Auto-Detect Success**: Auto-detection produces acceptable thresholds for >80% of images
- **Batch Performance**: Can process 100 images without crashes or memory issues

### User Experience Metrics
- **Setup Time**: New user can install and run app in <10 minutes
- **Learning Curve**: User can perform basic layer detection in <5 minutes after reading QUICK_START.md
- **Workflow Efficiency**: Batch processing 50 images takes <10 minutes (vs 2+ hours manually)

### Quality Metrics
- **Bug Density**: <2 critical bugs per 1000 lines of code
- **Test Coverage**: >80% code coverage for core detection functions
- **Documentation**: 100% of UI controls documented in QUICK_REFERENCE.md

---

## Risks and Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LAB detection doesn't work well for all samples | High | High | Provide hybrid mode fallback; allow manual threshold override |
| Auto-detection algorithms produce poor thresholds | Medium | Medium | Test on diverse images; default to K-means; allow manual tuning |
| Processing speed too slow for large batches | Low | Medium | Optimize numpy operations; add progress cancellation |
| Memory issues with 100+ images | Low | High | Process in chunks; clear cache after each image |

### User Experience Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| UI too complex with V1+V2 panels | Medium | Medium | Make V2 panel collapsible; provide presets |
| Users confused by hybrid mode | Medium | Low | Add tooltips; create tutorial video |
| Installation fails on some machines | Low | High | Comprehensive installation scripts; detailed troubleshooting docs |

### Project Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Development takes longer than expected | High | Medium | Prioritize Phase 1-3; defer Phase 4 if needed |
| Code lost again due to no git commits | Medium | Critical | **COMMIT FREQUENTLY**; use feature branches |
| Breaking changes affect v1.0 users | Low | High | Maintain backward compatibility; keep v1.0 mode working |

---

## Testing Strategy

### Unit Testing
```python
# test_lab_detection.py
def test_detect_lab_layers_basic():
    """Test LAB layer detection on synthetic image."""
    # Create synthetic image with known layers
    # Run detection
    # Verify correct layer classification

def test_vignetting_correction():
    """Test vignetting correction improves edge detection."""
    # Test with/without correction
    # Verify edge regions classified correctly

def test_auto_detection_kmeans():
    """Test K-means auto-detection produces reasonable thresholds."""
    # Test on multiple sample images
    # Verify T1 < T2 (only 2 thresholds!)
    # Verify thresholds in reasonable range (0-255)
```

### Integration Testing
```python
# test_hybrid_mode.py
def test_hybrid_mode_respects_v1_manual_threshold():
    """Verify Bug Fix #1."""
    # Uncheck "Use Adaptive Threshold"
    # Set manual threshold to 128
    # Enable hybrid mode
    # Verify V1 uses manual threshold, not adaptive

def test_hybrid_mode_v1_masks_v2():
    """Verify hybrid mode only detects layers in V1 film regions."""
    # Process in V1 mode → get mask
    # Process in hybrid mode → get layer mask
    # Verify layer mask only has values where V1 mask is True
```

### User Acceptance Testing
- [ ] Can a non-programmer install and run the app successfully?
- [ ] Can a user process 10 images and export CSV without instructions?
- [ ] Does auto-detect produce acceptable results on user's real data?
- [ ] Is the UI intuitive without reading documentation?

---

## Appendix A: File Modification Checklist

### Files to Create (New in v2.1.0)
- [ ] `thin_film_analyzer/core/detection.py`
- [ ] `thin_film_analyzer/core/detection_algorithms.py`
- [ ] `thin_film_analyzer/tests/test_lab_detection.py`
- [ ] `thin_film_analyzer/tests/test_hybrid_mode.py`
- [ ] `PRD_V2.1.0.md` (this document)

### Files to Modify (Updates from v1.0)
- [ ] `thin_film_analyzer/__init__.py` - Version to 2.1.0
- [ ] `thin_film_analyzer/config/defaults.py` - Version to 2.1.0
- [ ] `thin_film_analyzer/ui/main_window.py` - Add V2 panel, hybrid mode, bug fixes
- [ ] `thin_film_analyzer/core/processor.py` - Add `process_image_hybrid()`, `process_image_lab()`
- [ ] `thin_film_analyzer/core/overlay.py` - Add color-coded layer overlays
- [ ] `thin_film_analyzer/models/detection_result.py` - Add layer fields
- [ ] `thin_film_analyzer/models/batch_session.py` - Add threshold locking
- [ ] `thin_film_analyzer/core/export.py` - Add layer stats to CSV
- [ ] `README.md` - Document v2.1.0 features
- [ ] `CHANGELOG.md` - Add v2.1.0 changelog
- [ ] `SETUP_GUIDE.md` - Add layer detection instructions
- [ ] `QUICK_REFERENCE.md` - Add T1/T2 parameter reference (only 2 thresholds!)

### Files to Keep Unchanged
- ✅ `requirements.txt` - Dependencies already correct
- ✅ `install.bat`, `install.sh`, `run_app.bat`, `run_app.sh` - Already enhanced
- ✅ `create_distribution.bat` - Already updated for source distribution
- ✅ `QUICK_START.md` - Installation guide complete

---

## Appendix B: Key Formulas & Algorithms

### Vignetting Correction (L-channel)
```python
# Local normalization to reduce edge darkening
def apply_vignetting_correction(L_channel):
    # Calculate local mean using large Gaussian blur
    local_mean = cv2.GaussianBlur(L_channel, (101, 101), 30)

    # Normalize: L_corrected = L * (global_mean / local_mean)
    global_mean = np.mean(L_channel)
    L_corrected = L_channel * (global_mean / (local_mean + 1e-6))

    return np.clip(L_corrected, 0, 255).astype(np.uint8)
```

### K-means Threshold Detection (Corrected for 2 Thresholds)
```python
def detect_thresholds_kmeans(binary_mask, image):
    """
    Auto-detect T1, T2 using K-means clustering.
    CRITICAL: Only analyzes pixels where binary_mask == 1 (V1 detected film).
    """
    # Convert to LAB and extract L-channel
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    L = lab[:, :, 0]

    # CRITICAL: Only extract L values from film pixels
    film_pixels = L[binary_mask == 1]

    # Flatten for K-means
    film_L_flat = film_pixels.reshape(-1, 1).astype(np.float32)

    # K-means with 3 clusters (mono, bi, tri) - NOT 4!
    # Substrate already excluded by binary_mask
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(film_L_flat, 3, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

    # Sort centers
    centers_sorted = np.sort(centers.flatten())

    # Thresholds are midpoints between cluster centers
    # ONLY 2 thresholds: mono/bi boundary and bi/tri boundary
    t1 = int((centers_sorted[0] + centers_sorted[1]) / 2)  # Mono/Bi
    t2 = int((centers_sorted[1] + centers_sorted[2]) / 2)  # Bi/Tri

    return t1, t2  # Returns 2 values, not 3
```

### Hybrid Mode Pipeline (Corrected Architecture)
```python
def process_image_hybrid(image_path, v1_params, v2_params):
    """
    Mandatory hybrid pipeline: V1 detects film, V2 classifies layers.
    """
    # Step 1: V1 binary detection (film vs substrate)
    binary_mask, _ = process_image(image_path, **v1_params)
    # binary_mask: 0 = substrate, 1 = film

    # Step 2: V2 layer detection (ONLY on film pixels)
    layer_mask, layer_stats = detect_lab_layers(
        binary_mask,  # Pass binary_mask as first parameter
        image_path,
        **v2_params
    )
    # layer_mask: 0 = substrate (from V1), 1 = mono, 2 = bi, 3 = tri
    # Substrate pixels (binary_mask == 0) are automatically 0 in layer_mask

    # Calculate combined stats
    total_pixels = binary_mask.size
    combined_stats = {
        'total_coverage': np.sum(binary_mask > 0) / total_pixels * 100,  # From V1
        'mono_coverage': np.sum(layer_mask == 1) / total_pixels * 100,   # From V2
        'bi_coverage': np.sum(layer_mask == 2) / total_pixels * 100,
        'tri_coverage': np.sum(layer_mask == 3) / total_pixels * 100
    }

    return binary_mask, combined_stats, layer_mask
```

---

## Appendix C: References

### Previous Development Sessions
- Original v1.0 implementation (git commit: c73cdae)
- v2.0 development session (2025-12-13) - **CODE LOST, not committed**
- Distribution enhancement session (2025-12-13) - Completed

### Related Documentation
- `README.md` - Project overview
- `SETUP_GUIDE.md` - Installation instructions
- `QUICK_REFERENCE.md` - Parameter reference
- `CHANGELOG.md` - Version history

### External Resources
- LAB Color Space: https://en.wikipedia.org/wiki/CIELAB_color_space
- K-means Clustering: https://scikit-learn.org/stable/modules/clustering.html#k-means
- Otsu's Method: https://en.wikipedia.org/wiki/Otsu%27s_method
- PyQt6 Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6/

---

**Document End**

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-13 | Claude + User | Initial PRD based on v1.0 features and v2.0 development session |

---

## Approval

**Technical Lead**: _________________  Date: _________

**Product Owner**: _________________  Date: _________

**QA Lead**: _________________  Date: _________
