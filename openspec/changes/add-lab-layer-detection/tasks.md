# Implementation Tasks

## 1. Core LAB Detection Functions

- [x] 1.1 Create `thin_film_analyzer/core/lab_detection.py`
  - [x] 1.1.1 Implement `detect_lab_layers(binary_mask, image, t1, t2, apply_vignetting_correction)` function
  - [x] 1.1.2 Implement L-channel vignetting correction for film pixels only
  - [x] 1.1.3 Implement three-way classification (mono/bi/tri) based on T1, T2
  - [x] 1.1.4 Calculate per-layer coverage statistics
  - [x] 1.1.5 Add docstrings with type hints (Google style)

- [ ] 1.2 Create unit tests in `thin_film_analyzer/tests/test_lab_detection.py` (DEFERRED)
  - [ ] 1.2.1 Test basic layer classification on synthetic image
  - [ ] 1.2.2 Test vignetting correction improves edge classification
  - [ ] 1.2.3 Test binary_mask properly restricts analysis to film pixels
  - [ ] 1.2.4 Test edge cases (empty mask, single-layer film, etc.)

**Dependencies**: None (new file)
**Validation**: Run `pytest thin_film_analyzer/tests/test_lab_detection.py` (DEFERRED)

---

## 2. Auto-Detection Algorithms

- [x] 2.1 Create `thin_film_analyzer/core/detection_algorithms.py`
  - [x] 2.1.1 Implement `detect_thresholds_kmeans(binary_mask, image)` - K-means clustering (3 clusters)
  - [x] 2.1.2 Implement `detect_thresholds_percentile(binary_mask, image)` - 33rd/66th percentiles
  - [x] 2.1.3 Implement `detect_thresholds_histogram(binary_mask, image)` - Peak detection
  - [x] 2.1.4 Implement `detect_thresholds_otsu_multi(binary_mask, image)` - Multi-threshold Otsu
  - [x] 2.1.5 Add shared helper: `extract_film_l_values(binary_mask, image)` to avoid duplication
  - [x] 2.1.6 Add docstrings with algorithm explanations

- [ ] 2.2 Create unit tests in `thin_film_analyzer/tests/test_detection_algorithms.py` (DEFERRED)
  - [ ] 2.2.1 Test each algorithm produces T1 < T2
  - [ ] 2.2.2 Test algorithms only analyze film pixels (binary_mask)
  - [ ] 2.2.3 Test algorithms on sample images with known layer distributions
  - [ ] 2.2.4 Test edge cases (uniform film, two-layer only, etc.)

**Dependencies**: Task 1.1 complete (uses same LAB conversion logic)
**Validation**: Run `pytest thin_film_analyzer/tests/test_detection_algorithms.py`

---

## 3. Update Image Processor

- [x] 3.1 Update `thin_film_analyzer/core/processor.py`
  - [x] 3.1.1 Add `process_image_hybrid()` function
    - Takes V1 parameters (use_adaptive, threshold_value, adaptive_block_size, adaptive_c, adaptive_bias)
    - Takes V2 parameters (t1, t2, apply_vignetting_correction)
    - Calls existing `process_image()` for V1 binary mask
    - Calls `detect_lab_layers()` for V2 layer classification
    - Returns (original_image, binary_mask, combined_stats, layer_mask)
  - [x] 3.1.2 Add `adaptive_bias` parameter to existing `process_image()` function
    - Modify threshold calculation: `effective_c = adaptive_c + adaptive_bias`
    - Default adaptive_bias=0 (backward compatible)
  - [x] 3.1.3 Update docstrings

- [ ] 3.2 Create integration tests in `thin_film_analyzer/tests/test_hybrid_mode.py` (DEFERRED)
  - [ ] 3.2.1 Test hybrid mode masks V2 by V1 results
  - [ ] 3.2.2 Test adaptive_bias affects V1 detection
  - [ ] 3.2.3 Test manual threshold respected when use_adaptive=False
  - [ ] 3.2.4 Test combined statistics calculation

**Dependencies**: Tasks 1.1, 2.1 complete
**Validation**: Run `pytest thin_film_analyzer/tests/test_hybrid_mode.py`

---

## 4. Update Overlay Generation

- [x] 4.1 Update `thin_film_analyzer/core/overlay.py`
  - [x] 4.1.1 Add `generate_layer_overlay(layer_mask, original_image)` function
    - Mono pixels → Red (BGR: 0, 0, 255)
    - Bi pixels → Blue (BGR: 255, 0, 0)
    - Tri pixels → Green (BGR: 0, 255, 0)
    - Substrate pixels → Transparent
  - [x] 4.1.2 Ensure overlay compatible with existing transparency/opacity controls
  - [x] 4.1.3 Add docstrings

**Dependencies**: Task 1.1 complete (layer_mask format)
**Validation**: Visual inspection + manual test on sample image (PENDING UI)

---

## 5. Update Data Models

- [x] 5.1 Update `thin_film_analyzer/models/detection_result.py`
  - [x] 5.1.1 Add optional fields: `mono_coverage`, `bi_coverage`, `tri_coverage`
  - [x] 5.1.2 Add optional field: `thresholds` (Tuple[int, int] for T1, T2)
  - [x] 5.1.3 Update `to_dict()` method to include new fields
  - [x] 5.1.4 Update `__post_init__` validation for layer coverage fields
  - [x] 5.1.5 Update docstrings

- [x] 5.2 Update `thin_film_analyzer/models/batch_session.py`
  - [x] 5.2.1 Add `thresholds_locked` boolean field
  - [x] 5.2.2 Add `locked_t1` and `locked_t2` fields (optional int)
  - [x] 5.2.3 Add methods: `lock_thresholds(t1, t2)`, `unlock_thresholds()`, `are_thresholds_locked()`, `get_locked_thresholds()`
  - [x] 5.2.4 Update docstrings

**Dependencies**: None (data models)
**Validation**: Unit tests for validation logic (DEFERRED)

---

## 6. Update CSV Export

- [x] 6.1 Update `thin_film_analyzer/core/export.py`
  - [x] 6.1.1 Update CSV headers to include: `mono_coverage`, `bi_coverage`, `tri_coverage`
  - [x] 6.1.2 Add summary statistics section (mean, std dev, min, max for each layer)
  - [x] 6.1.3 Handle optional fields gracefully (NULL if layer detection not used)
  - [x] 6.1.4 `export_overlay_images()` already exists (no changes needed)
    - Saves color-coded overlay images
    - Filename format: `{original_name}_overlay.png`
  - [x] 6.1.5 Update docstrings

**Dependencies**: Task 5.1 complete (DetectionResult fields)
**Validation**: Export test batch, verify CSV format and overlay images (PENDING UI)

---

## 7. Update Main Window UI

- [x] 7.1 Update `thin_film_analyzer/ui/main_window.py` - V1 Panel
  - [x] 7.1.1 Add "Adaptive Bias" spinbox to V1 processing panel
    - Range: -10 to +10, default 0
    - Tooltip: "Fine-tune adaptive threshold sensitivity"
    - Connect to parameter update handler
  - [x] 7.1.2 Ensure adaptive bias passed to `process_image_hybrid()` function

- [x] 7.2 Update `thin_film_analyzer/ui/main_window.py` - V2 Panel
  - [x] 7.2.1 Create V2 "Layer Classification" panel (QGroupBox)
  - [x] 7.2.2 Add algorithm dropdown (K-means, Percentile, Histogram, Otsu)
  - [x] 7.2.3 Add "Auto-Detect Thresholds" button
    - On click: Run selected algorithm, update T1/T2 sliders, reprocess image
  - [x] 7.2.4 Add T1 slider (0-255, default 85, label "Mono/Bi Boundary")
  - [x] 7.2.5 Add T2 slider (0-255, default 170, label "Bi/Tri Boundary")
  - [x] 7.2.6 Add "Lock Thresholds" toggle button (🔓/🔒 icon)
    - When locked: disable T1/T2 sliders, change icon to 🔒
    - When unlocked: enable sliders, change icon to 🔓
  - [x] 7.2.7 Add results labels: "Total Coverage", "Monolayer", "Bilayer", "Trilayer"
  - [x] 7.2.8 Connect all controls to hybrid processing handler

- [x] 7.3 Update `thin_film_analyzer/ui/main_window.py` - Processing
  - [x] 7.3.1 Update image processing handler to call `process_image_hybrid()`
  - [x] 7.3.2 Add wait cursor during processing (QApplication.setOverrideCursor)
  - [x] 7.3.3 Ensure cursor restored on error (try/finally block)
  - [x] 7.3.4 Update overlay display to show layer-colored overlay
  - [x] 7.3.5 Update statistics display with layer breakdown

- [x] 7.4 Update `thin_film_analyzer/ui/main_window.py` - Batch Menu
  - [x] 7.4.1 Add "Batch" menu to menu bar
  - [x] 7.4.2 Add "Process All Images" action (Ctrl+P)
  - [x] 7.4.3 Add "Export Results to CSV" action (Ctrl+E)
  - [x] 7.4.4 Add "Export Overlay Images" action
  - [x] 7.4.5 Implement batch processing with progress dialog
  - [x] 7.4.6 Respect locked thresholds during batch processing

- [x] 7.5 Bug Fixes
  - [x] 7.5.1 Fix overlay visibility toggle (add explicit `else` clause to hide overlay)
  - [x] 7.5.2 Verify manual threshold respected when use_adaptive=False (handled by process_image_hybrid)
  - [x] 7.5.3 Test all parameters update in real-time (all handlers trigger process_current_image)

**Dependencies**: Tasks 1-6 complete
**Validation**: Application launches successfully, UI elements created ✓

---

## 8. Update Configuration

- [x] 8.1 Update `thin_film_analyzer/config/defaults.py`
  - [x] 8.1.1 Change APP_VERSION to "2.1.0"
  - [x] 8.1.2 Add default V2 parameters:
    - `DEFAULT_T1 = 85`
    - `DEFAULT_T2 = 170`
    - `DEFAULT_AUTO_ALGORITHM = "kmeans"`
    - `DEFAULT_ADAPTIVE_BIAS = 0`
    - `DEFAULT_APPLY_VIGNETTING_CORRECTION = True`
  - [x] 8.1.3 Update docstrings

- [x] 8.2 Update `thin_film_analyzer/__init__.py`
  - [x] 8.2.1 Update version string to "2.1.0"

**Dependencies**: None
**Validation**: Verify version displays correctly in app title (PENDING UI)

---

## 9. Testing & Validation

- [ ] 9.1 Unit Testing
  - [ ] 9.1.1 Run all unit tests: `pytest thin_film_analyzer/tests/`
  - [ ] 9.1.2 Achieve >80% code coverage for core modules
  - [ ] 9.1.3 Fix any failing tests

- [ ] 9.2 Integration Testing
  - [ ] 9.2.1 Test full V1+V2 pipeline on 10 diverse sample images
  - [ ] 9.2.2 Verify layer classification matches manual inspection (>90% accuracy)
  - [ ] 9.2.3 Test all 4 auto-detection algorithms produce reasonable results
  - [ ] 9.2.4 Test batch processing with 50 images

- [ ] 9.3 Performance Testing
  - [ ] 9.3.1 Verify processing time <5s per 2000×1500 image
  - [ ] 9.3.2 Verify memory usage <2GB for 50-image batch
  - [ ] 9.3.3 Verify UI remains responsive during processing

- [ ] 9.4 User Acceptance Testing
  - [ ] 9.4.1 Non-programmer can install and run app
  - [ ] 9.4.2 User can perform layer detection within 5 minutes
  - [ ] 9.4.3 Auto-detect produces acceptable results on user's data (>80% success rate)

**Dependencies**: Tasks 1-8 complete
**Validation**: All tests pass, performance metrics met

---

## 10. Documentation

- [ ] 10.1 Update README.md
  - [ ] 10.1.1 Add v2.1.0 features to feature list
  - [ ] 10.1.2 Update version history section
  - [ ] 10.1.3 Add LAB layer detection to algorithm details

- [ ] 10.2 Update SETUP_GUIDE.md
  - [ ] 10.2.1 Document V2 panel controls
  - [ ] 10.2.2 Explain auto-detect workflow
  - [ ] 10.2.3 Add troubleshooting for layer detection issues

- [ ] 10.3 Update QUICK_REFERENCE.md
  - [ ] 10.3.1 Add T1/T2 parameter reference
  - [ ] 10.3.2 Document auto-detection algorithms
  - [ ] 10.3.3 Add adaptive bias explanation

- [ ] 10.4 Create CHANGELOG.md entry
  - [ ] 10.4.1 Document all v2.1.0 changes
  - [ ] 10.4.2 List new features, bug fixes, breaking changes

- [ ] 10.5 Create user guide
  - [ ] 10.5.1 Write LAB layer detection tutorial
  - [ ] 10.5.2 Include screenshots of V2 panel
  - [ ] 10.5.3 Explain when to use each auto-detect algorithm

**Dependencies**: Tasks 1-9 complete
**Validation**: Documentation reviewed for accuracy and clarity

---

## Implementation Notes

**Parallelizable work:**
- Tasks 1, 2 can be done in parallel (independent core functions)
- Task 4 (overlay) can overlap with tasks 1-2 once layer_mask format is defined
- Task 5 (data models) independent, can be done anytime
- Task 6 (CSV export) depends only on Task 5

**Critical path:**
1. Task 1 (LAB detection) → Task 2 (auto-detect) → Task 3 (processor) → Task 7 (UI)
2. Tasks 5, 6 can proceed in parallel
3. Tasks 8, 9, 10 sequential at end

**Testing checkpoints:**
- After Task 1: Unit tests for LAB detection
- After Task 3: Integration tests for hybrid mode
- After Task 7: Full UI testing
- After Task 9: Performance and UAT

**Estimated effort:**
- Core functions (Tasks 1-3): 8-12 hours
- UI updates (Task 7): 6-10 hours
- Testing (Task 9): 4-6 hours
- Documentation (Task 10): 2-4 hours
- **Total**: 20-32 hours
