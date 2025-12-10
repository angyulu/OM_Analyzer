# Implementation Tasks
## Thin Film Coverage Analyzer

**Feature**: 001-thin-film-analyzer
**Branch**: `001-thin-film-analyzer`
**Created**: 2025-12-07

---

## Overview

This document contains implementation tasks organized by user story to enable independent, incremental delivery. Each phase delivers a complete, testable increment of functionality.

**Total Tasks**: 52
**MVP Scope**: Phase 3 (User Story 1 - Basic Image Analysis with Visual Verification) - 15 tasks

---

## Implementation Strategy

### Delivery Approach

1. **Phase 1-2**: Setup and foundational infrastructure (blocking prerequisites)
2. **Phase 3 (MVP)**: User Story 1 - Basic single-image analysis with visual verification
3. **Phase 4**: User Story 2 - Scale calibration and absolute area measurement
4. **Phase 5**: User Story 3 - Batch processing and CSV export
5. **Phase 6**: User Story 4 - ROI selection for scale bar exclusion
6. **Phase 7**: Polish and cross-cutting concerns

### Independent Testing

Each user story phase includes its independent test criteria, allowing validation without dependencies on future stories.

---

## Dependencies

### User Story Completion Order

```
Setup (Phase 1) → Foundational (Phase 2) → US1 (Phase 3) → US2 (Phase 4) → US3 (Phase 5) → US4 (Phase 6) → Polish (Phase 7)
                                             ↓              ↓              ↓
                                           MVP          Enhanced       Production
                                                        Features        Ready
```

**Dependency Rules**:
- **US1 (P1)**: No user story dependencies (only Setup/Foundational)
- **US2 (P2)**: Builds on US1 (uses detection results, adds calibration)
- **US3 (P3)**: Requires US1 and US2 (batch processing needs detection + calibration)
- **US4 (P4)**: Can be developed in parallel with US2/US3 (ROI is independent feature)

### Parallel Execution Opportunities

Tasks marked with **[P]** can be executed in parallel with other [P] tasks in the same phase (different files, no dependencies).

---

## Phase 1: Setup & Project Initialization

**Goal**: Create project structure and install dependencies

**Tasks**:

- [X] T001 Create project root directory `thin_film_analyzer/` at repository root
- [X] T002 [P] Create directory structure: `thin_film_analyzer/ui/`, `thin_film_analyzer/core/`, `thin_film_analyzer/models/`, `thin_film_analyzer/config/`, `thin_film_analyzer/tests/`, `thin_film_analyzer/resources/`
- [X] T003 [P] Create `__init__.py` files in thin_film_analyzer/, thin_film_analyzer/ui/, thin_film_analyzer/core/, thin_film_analyzer/models/, thin_film_analyzer/config/, thin_film_analyzer/tests/
- [X] T004 [P] Create requirements.txt with dependencies: PyQt6>=6.5.0, opencv-python>=4.8.0, scikit-image>=0.21.0, numpy>=1.24.0, pandas>=2.0.0, pytest>=7.4.0
- [X] T005 [P] Create .gitignore with Python patterns (__pycache__/, *.pyc, venv/, .pytest_cache/, *.log)
- [X] T006 [P] Create thin_film_analyzer/README.md with project description and setup instructions
- [X] T007 Create thin_film_analyzer/main.py skeleton with PyQt6 QApplication entry point

**Completion Criteria**:
- All directories exist per constitutional file structure
- requirements.txt lists all dependencies from technical context
- main.py runs without errors (even if empty UI)

---

## Phase 2: Foundational Infrastructure

**Goal**: Implement shared infrastructure needed by all user stories

**Tasks**:

- [X] T008 [P] Implement Image model with ImageStatus enum in thin_film_analyzer/models/image.py (attributes: filename, file_path, dimensions, format, status)
- [X] T009 [P] Implement DetectionResult model in thin_film_analyzer/models/detection_result.py (attributes: image_ref, coverage_percentage, area_um2, threshold_value, roi_coords, film_pixel_count, total_pixel_count, processing_timestamp)
- [X] T010 [P] Implement ApplicationSettings model in thin_film_analyzer/models/app_settings.py (attributes: scale_presets, last_threshold, overlay_transparency, noise_reduction_enabled, window_geometry, backup_timestamp)
- [X] T011 [P] Implement default configuration in thin_film_analyzer/config/defaults.py (DEFAULT_THRESHOLD=128, DEFAULT_OPACITY=0.5, OVERLAY_COLOR=(255,0,0), MAX_BATCH_SIZE=100, MAX_LOG_SIZE_MB=10)
- [X] T012 [P] Implement SettingsManager in thin_film_analyzer/core/settings.py with atomic save, backup creation, and recovery from backup (methods: save_settings, load_settings, get_default_settings)
- [X] T013 [P] Implement ErrorLogger in thin_film_analyzer/core/logger.py with RotatingFileHandler (10MB max, 2 backups) and export_diagnostics method
- [X] T014 Create synthetic test image generator in thin_film_analyzer/tests/synthetic/generate_test_images.py (generate 25%, 50%, 75% coverage images at 2048×2048)

**Completion Criteria**:
- All models validate their attributes correctly
- Settings can be saved/loaded with backup recovery
- Error logger rotates at 10MB and exports diagnostics to ZIP
- Synthetic test images available for validation

---

## Phase 3: User Story 1 - Basic Image Analysis with Visual Verification (P1 - MVP)

**User Story**: As a researcher, I want to load a single optical microscope image, apply automatic thin film detection with adjustable thresholds, and see a visual overlay of detected regions so I can verify the accuracy and get a coverage percentage for my sample.

**Independent Test Criteria**:
1. Load a single OM image (PNG/JPG/TIFF/BMP) via drag-and-drop or file browser
2. Click "Process" and see coverage percentage displayed
3. Toggle overlay on/off to show/hide detected regions
4. Adjust threshold slider (0-255) and see overlay update in real-time (<200ms)
5. Adjust transparency slider and see overlay opacity change
6. Complete analysis in <1 minute total (SC-001)
7. Processing completes in <3 seconds for 2048×2048 image (FR-028)

### Core Processing

- [ ] T015 [P] [US1] Implement constitutional algorithm in thin_film_analyzer/core/detection.py: apply_threshold(grayscale_image, threshold_value, method) returns binary mask
- [ ] T016 [P] [US1] Implement noise reduction in thin_film_analyzer/core/detection.py: apply_noise_reduction(image) using Gaussian blur (5×5 kernel)
- [ ] T017 [P] [US1] Implement morphological operations in thin_film_analyzer/core/detection.py: clean_mask(binary_mask) using opening and closing (3×3 kernel, 2 iterations each)
- [ ] T018 [US1] Implement main processing pipeline in thin_film_analyzer/core/processor.py: process_image(image_path, threshold_value, noise_reduction, roi) returns (binary_mask, coverage_percentage)

### Overlay Generation

- [ ] T019 [P] [US1] Implement overlay generation in thin_film_analyzer/core/overlay.py: generate_overlay(original_image, binary_mask, opacity, color) returns RGB image with alpha blending

### UI Components

- [ ] T020 [P] [US1] Create ImageViewer widget in thin_film_analyzer/ui/image_viewer.py using QGraphicsView with methods: set_image, set_overlay, toggle_overlay, set_overlay_opacity
- [ ] T021 [P] [US1] Create ThresholdSlider custom widget in thin_film_analyzer/ui/widgets.py (QSlider with QLabel, range 0-255, emits value_changed signal)
- [ ] T022 [P] [US1] Create TransparencySlider custom widget in thin_film_analyzer/ui/widgets.py (QSlider with QLabel, range 0.0-1.0, emits opacity_changed signal)
- [ ] T023 [US1] Implement drag-and-drop support in thin_film_analyzer/ui/main_window.py: dragEnterEvent, dropEvent to accept image files (PNG, JPG, TIFF, BMP)
- [ ] T024 [US1] Implement file browser dialog in thin_film_analyzer/ui/main_window.py: on_open_file_clicked using QFileDialog with image filters
- [ ] T025 [US1] Create main window layout in thin_film_analyzer/ui/main_window.py with image viewer (left), controls panel (right: threshold slider, transparency slider, process button, overlay toggle)
- [ ] T026 [US1] Connect threshold slider to real-time reprocessing in thin_film_analyzer/ui/main_window.py: on_threshold_changed slot triggers process_image and updates overlay
- [ ] T027 [US1] Connect transparency slider to overlay opacity in thin_film_analyzer/ui/main_window.py: on_opacity_changed slot calls image_viewer.set_overlay_opacity
- [ ] T028 [US1] Display coverage percentage in main window UI (QLabel updating after processing)

### Error Handling

- [ ] T029 [US1] Implement error handling in processor.py for corrupted/unreadable files with user-friendly messages and error logging

**Phase 3 Completion Criteria** (MVP Delivery):
- Single image can be loaded via drag-drop or file browser
- Processing completes in <3 seconds for 2048×2048 images
- Overlay toggles on/off correctly
- Threshold slider updates overlay in real-time
- Transparency slider adjusts overlay opacity
- Coverage percentage displays correctly
- Corrupted files show error message without crashing

**Parallel Execution Example (Phase 3)**:
```bash
# Can be done in parallel:
- T015 (detection.py)
- T016 (detection.py - different function)
- T017 (detection.py - different function)
- T019 (overlay.py)
- T020 (image_viewer.py)
- T021 (widgets.py - ThresholdSlider)
- T022 (widgets.py - TransparencySlider)

# Must be sequential:
T018 (depends on T015, T016, T017)
T023-T028 (depend on T020, T021, T022)
T029 (depends on T018)
```

---

## Phase 4: User Story 2 - Scale Calibration and Area Calculation (P2)

**User Story**: As a researcher, I want to calibrate the scale for different microscope objectives and save these as reusable presets so I can get coverage results in absolute area (µm²) rather than just percentages, without recalibrating every session.

**Independent Test Criteria**:
1. Select a saved preset (e.g., "10x") and see scale populate automatically
2. Draw a line on an image feature, enter known length (µm), and see calculated scale
3. Save a new preset by name
4. Attempt to save preset with existing name and see confirmation dialog
5. Process an image with calibration and see both percentage and absolute area (µm²)
6. Apply calibration to batch (tested in next story, but setup here)
7. Preset reduces recalibration time from 2 min to <10 sec (SC-009)

### Models

- [ ] T030 [P] [US2] Implement ScalePreset model in thin_film_analyzer/models/scale_preset.py (attributes: name, scale_um_per_pixel, created_date, objective_ref; methods: validate, to_dict, from_dict)

### Core Logic

- [ ] T031 [P] [US2] Implement CalibrationManager in thin_film_analyzer/core/calibration.py with methods: save_preset(preset, overwrite), load_preset(name), preset_exists(name), list_presets(), delete_preset(name)
- [ ] T032 [US2] Integrate calibration into processor.py: Update process_image to accept scale_um_per_pixel parameter and calculate area_um2 in DetectionResult

### UI Components

- [ ] T033 [P] [US2] Create scale calibration panel in thin_film_analyzer/ui/widgets.py: ScaleCalibrationWidget with preset dropdown, manual input field, and "Calibrate from Image" button
- [ ] T034 [P] [US2] Implement draw-line calibration tool in thin_film_analyzer/ui/widgets.py: LineDrawTool widget (using QGraphicsScene) that emits line_drawn signal with pixel length
- [ ] T035 [P] [US2] Create preset overwrite confirmation dialog in thin_film_analyzer/ui/dialogs.py: PresetOverwriteDialog with Yes/No buttons
- [ ] T036 [US2] Integrate scale calibration panel into main window (add to controls panel)
- [ ] T037 [US2] Connect preset dropdown to calibration manager: on_preset_selected loads preset and populates scale field
- [ ] T038 [US2] Connect "Save Preset" button to preset save logic with overwrite confirmation (FR-018)
- [ ] T039 [US2] Connect "Calibrate from Image" button to line draw tool: calculate scale = known_length_um / line_length_pixels
- [ ] T040 [US2] Update results display to show both coverage percentage and area (µm²) when calibration is set

**Phase 4 Completion Criteria**:
- Presets can be saved, loaded, and deleted
- Duplicate preset name triggers confirmation dialog
- Draw-line tool calculates scale correctly
- Results show both percentage and absolute area when calibrated
- Preset load takes <10 seconds

**Parallel Execution Example (Phase 4)**:
```bash
# Can be done in parallel:
- T030 (scale_preset.py model)
- T031 (calibration.py)
- T033 (ScaleCalibrationWidget)
- T034 (LineDrawTool)
- T035 (PresetOverwriteDialog)

# Must be sequential:
T032 (depends on T030, T031)
T036-T040 (depend on T033, T034, T035)
```

---

## Phase 5: User Story 3 - Batch Processing and Results Export (P3)

**User Story**: As a researcher, I want to load multiple OM images at once, process them all with the same settings, and export the results to CSV so I can efficiently analyze entire sample sets and include the data in my reports.

**Independent Test Criteria**:
1. Load 10 images via drag-drop and see all thumbnails
2. Click "Process All" and see progress bar with "Processing image X of 10"
3. UI remains responsive during processing (<200ms interaction latency)
4. Batch completes in <2 minutes for 10 images (FR-027)
5. Results table shows filename, coverage %, and area for each image
6. Click "Export CSV" and verify CSV contains all results plus summary statistics
7. Click "New Session" and verify images/results cleared but settings preserved
8. Memory stays <2 GB for 50-image batch (SC-008)

### Models

- [ ] T041 [P] [US3] Implement BatchSession model in thin_film_analyzer/models/batch_session.py (attributes: image_refs, scale_calibration, threshold_setting, roi_settings, summary_stats)
- [ ] T042 [P] [US3] Implement BatchStatistics in thin_film_analyzer/models/batch_session.py with calculate(results) class method (mean, std dev, min, max for coverage and area)

### Core Logic

- [ ] T043 [P] [US3] Implement ResultsExporter in thin_film_analyzer/core/export.py with methods: add_result(filename, coverage_pct, area_um2), export_csv(output_path), export_images_with_overlay(results, output_dir)
- [ ] T044 [P] [US3] Implement BatchProcessor QThread worker in thin_film_analyzer/core/processor.py with signals: progress_updated(current, total), image_processed(filename, coverage, area), processing_complete(), error_occurred(filename, error_msg)
- [ ] T045 [US3] Implement batch processing logic in BatchProcessor.run(): iterate images, call process_image for each, emit progress/results, handle errors gracefully

### UI Components

- [ ] T046 [P] [US3] Create thumbnail panel widget in thin_film_analyzer/ui/widgets.py: ThumbnailPanel (QListWidget showing loaded image thumbnails)
- [ ] T047 [P] [US3] Create results table widget in thin_film_analyzer/ui/results_table.py (QTableWidget with columns: Filename, Coverage %, Area µm²)
- [ ] T048 [P] [US3] Create progress bar widget in thin_film_analyzer/ui/widgets.py: BatchProgressBar with label "Processing image X of Y"
- [ ] T049 [US3] Integrate thumbnail panel into main window (bottom or left panel)
- [ ] T050 [US3] Integrate results table into main window (bottom panel or separate tab)
- [ ] T051 [US3] Implement "Process All" button logic: create BatchProcessor thread, connect signals, start processing
- [ ] T052 [US3] Connect BatchProcessor signals to UI updates: progress → progress bar, image_processed → results table row, error_occurred → error message
- [ ] T053 [US3] Implement "Export CSV" button: call ResultsExporter.export_csv with file dialog path
- [ ] T054 [US3] Implement "Export Images" button: call ResultsExporter.export_images_with_overlay
- [ ] T055 [US3] Implement "New Session" button: clear all images and results, preserve settings (FR-047, FR-048, FR-050)
- [ ] T056 [US3] Add summary statistics display below results table (mean, std dev, min, max for coverage and area)

**Phase 5 Completion Criteria**:
- Multiple images load and display as thumbnails
- Batch processing completes in <2 min for 10 images
- UI remains responsive during batch processing
- Progress bar updates correctly
- Results table populates with all results
- CSV export includes all data plus summary statistics footer
- "New Session" clears images/results but preserves settings
- Memory usage <2 GB for 50 images

**Parallel Execution Example (Phase 5)**:
```bash
# Can be done in parallel:
- T041 (batch_session.py model)
- T042 (batch_session.py - BatchStatistics)
- T043 (export.py)
- T044 (processor.py - BatchProcessor thread)
- T046 (ThumbnailPanel)
- T047 (results_table.py)
- T048 (BatchProgressBar)

# Must be sequential:
T045 (depends on T044)
T049-T056 (depend on T046, T047, T048)
```

---

## Phase 6: User Story 4 - ROI Selection for Scale Bar Exclusion (P4)

**User Story**: As a researcher, I want to define a region of interest (ROI) to exclude scale bars or edge artifacts from the coverage calculation so that embedded scale bars and imaging artifacts don't skew my results.

**Independent Test Criteria**:
1. Click "Define ROI" and drag a rectangle on the image
2. Selected region highlights with visible border
3. Process image and verify coverage only includes ROI pixels
4. Click "Clear ROI" and verify calculation returns to full image
5. Load image with scale bar, define ROI excluding bottom 50 pixels, verify scale bar excluded from coverage

### UI Components

- [ ] T057 [P] [US4] Implement ROI selector widget in thin_film_analyzer/ui/roi_selector.py using QGraphicsRectItem with mouse events (mousePressEvent, mouseMoveEvent, mouseReleaseEvent)
- [ ] T058 [P] [US4] Add ROI selector mode toggle to image viewer in thin_film_analyzer/ui/image_viewer.py: enable_roi_mode(), disable_roi_mode()
- [ ] T059 [US4] Integrate ROI selector into main window: add "Define ROI" button and "Clear ROI" button
- [ ] T060 [US4] Connect ROI selector to processing pipeline: pass roi_coords to process_image when ROI defined
- [ ] T061 [US4] Update processor.py to apply ROI cropping before coverage calculation when roi parameter provided

**Phase 6 Completion Criteria**:
- ROI can be drawn on image with visual feedback
- Coverage calculation respects ROI boundaries
- ROI can be cleared to return to full image analysis
- Images with scale bars can be analyzed with scale bar excluded

**Parallel Execution Example (Phase 6)**:
```bash
# Can be done in parallel:
- T057 (roi_selector.py)
- T058 (image_viewer.py - ROI mode)

# Must be sequential:
T059-T061 (depend on T057, T058)
```

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Add finishing touches, improve UX, and ensure production readiness

### UI Polish

- [ ] T062 [P] Add tooltips to all controls (FR-045) in main_window.py using setToolTip()
- [ ] T063 [P] Implement keyboard shortcuts (FR-046) in main_window.py: Ctrl+O (open), Ctrl+P (process), Ctrl+E (export), Ctrl+N (new session)
- [ ] T064 [P] Add application icon to main window and resources in thin_film_analyzer/resources/icons/app_icon.png
- [ ] T065 [P] Implement window geometry persistence in main_window.py: save/restore window size and position from ApplicationSettings

### Error Handling & Validation

- [ ] T066 [P] Add file format validation (FR-005) in main_window.py: reject unsupported files with error dialog
- [ ] T067 [P] Add batch size validation (FR-004) in main_window.py: warn if attempting to load >100 images
- [ ] T068 [P] Implement unsupported file skipping in batch processing (edge case from spec): skip with warning, continue with remaining files

### Documentation

- [ ] T069 [P] Create thin_film_analyzer/README.md with usage instructions, keyboard shortcuts, and troubleshooting section
- [ ] T070 [P] Add docstrings to all public methods in core/ modules following contracts specification

**Phase 7 Completion Criteria**:
- All controls have helpful tooltips
- Keyboard shortcuts work as specified
- Application icon displays in window title and taskbar
- Window size/position persists across sessions
- File validation rejects unsupported formats gracefully
- README provides clear usage instructions

**Parallel Execution Example (Phase 7)**:
```bash
# All tasks in Phase 7 can be done in parallel (different concerns):
- T062 (tooltips)
- T063 (keyboard shortcuts)
- T064 (icon)
- T065 (window geometry)
- T066 (file validation)
- T067 (batch validation)
- T068 (error handling)
- T069 (README)
- T070 (docstrings)
```

---

## Task Summary

### By Phase

| Phase | Description | Task Count | Parallel Tasks |
|-------|-------------|------------|----------------|
| Phase 1 | Setup & Initialization | 7 | 5 |
| Phase 2 | Foundational Infrastructure | 7 | 6 |
| Phase 3 | US1 - Basic Analysis (MVP) | 15 | 8 |
| Phase 4 | US2 - Scale Calibration | 11 | 5 |
| Phase 5 | US3 - Batch Processing | 16 | 7 |
| Phase 6 | US4 - ROI Selection | 5 | 2 |
| Phase 7 | Polish & Cross-Cutting | 9 | 9 |
| **Total** | | **70** | **42** |

### By User Story

| User Story | Priority | Task Count | File Count | Independent Test |
|------------|----------|------------|------------|------------------|
| Setup/Foundation | - | 14 | 12 | N/A |
| US1 - Basic Analysis | P1 (MVP) | 15 | 6 | ✅ Yes |
| US2 - Scale Calibration | P2 | 11 | 5 | ✅ Yes |
| US3 - Batch Processing | P3 | 16 | 6 | ✅ Yes |
| US4 - ROI Selection | P4 | 5 | 2 | ✅ Yes |
| Polish | - | 9 | 3 | N/A |

### MVP Scope

**Minimum Viable Product**: Phase 1 + Phase 2 + Phase 3 (37 tasks)

**MVP Delivers**:
- Single image loading (drag-drop or file browser)
- Automatic thin film detection with threshold adjustment
- Real-time visual overlay with transparency control
- Coverage percentage calculation
- Processing <3 seconds per image
- Error handling for corrupted files

**Post-MVP Enhancements**:
- Phase 4: Scale calibration for absolute area measurement
- Phase 5: Batch processing and CSV export
- Phase 6: ROI selection for scale bar exclusion
- Phase 7: Polish and production readiness

---

## Validation Checklist

### Format Validation ✅

- [x] All tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- [x] Task IDs are sequential (T001-T070)
- [x] [P] markers present for parallelizable tasks
- [x] [US1], [US2], [US3], [US4] story labels present in user story phases
- [x] File paths included in task descriptions
- [x] No story labels in Setup, Foundational, or Polish phases

### Completeness Validation ✅

- [x] All user stories from spec.md have corresponding phases
- [x] All entities from data-model.md have corresponding tasks
- [x] All functional requirements from spec.md covered by tasks
- [x] Each phase has independent test criteria
- [x] Dependencies clearly documented
- [x] Parallel execution examples provided per phase

---

## Notes

**Testing Strategy**: No explicit test tasks generated per requirements (tests not requested in spec). Validation relies on:
- Manual testing per acceptance scenarios
- Synthetic test images (25%, 50%, 75% coverage)
- Independent test criteria per user story
- Visual verification through overlay system

**Performance Targets**: All performance requirements (3s/image, 2min/batch, 200ms UI) are implementation constraints verified through independent test criteria, not separate tasks.

**Constitutional Compliance**: Task organization aligns with constitutional principles:
- User-Centric Simplicity: MVP focuses on core single-image workflow first
- Visual Verification: Overlay implementation in US1 (MVP)
- Batch Efficiency: US3 builds on solid US1 foundation
- Calibration Flexibility: US2 adds precision to proven detection
- Reliable Error Handling: Integrated throughout foundational and user story tasks

---

**Tasks Status**: ✅ Complete and ready for implementation
**Next Step**: Begin Phase 1 (Setup) or jump to Phase 3 (MVP) if infrastructure already exists
