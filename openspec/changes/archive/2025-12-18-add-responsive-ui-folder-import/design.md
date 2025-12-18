# Design: Responsive UI and Folder-Based Import

## Context

The current v2.1.1 application uses a fixed-size window (1200×800) with drag-and-drop image loading. This creates friction for researchers who:
- Work on different display sizes (laptops, lab desktops, high-res monitors)
- Need to analyze entire folders of microscope images (typical workflow)
- Want to track per-image results incrementally rather than batch-processing everything at once

The PRD_V2.2.0 specifies three independent improvements that can be implemented without touching core detection algorithms. This design focuses on UI/UX changes to the PyQt6 application.

**Constraints:**
- Must maintain backward compatibility with v2.1.x analysis workflow
- No changes to core detection algorithms or processing pipeline
- Target users are non-programmers (simplicity is critical)
- Windows-first deployment (though PyQt6 is cross-platform)

## Goals / Non-Goals

**Goals:**
1. Responsive UI that works on displays from 1280×720 to 4K+ without manual intervention
2. Folder-first workflow: select folder → automatically load all images
3. Per-image submit workflow: analyze → submit → save analyzed image + append to results file
4. Maintain all existing functionality (layer detection, batch export, parameter tuning)

**Non-Goals:**
- No changes to detection algorithms or image processing logic
- No new analysis features (layer detection already added in v2.1.0)
- No cloud/server integration
- No automatic batch processing ("analyze all" button) in this version
- No subfolder recursion (only scan selected folder, not subdirectories)

## Decisions

### Decision 1: Remove Drag-and-Drop in Favor of Folder Selection

**Rationale:**
- Microscopy workflows typically involve analyzing entire experiment folders (10-200+ images)
- Drag-and-drop requires manually selecting multiple files, which is tedious for large batches
- Folder selection + auto-load is faster and more intuitive for the target use case
- "File > Open Image" menu item preserved for single-image workflows

**Alternative considered:**
- Keep both drag-and-drop AND folder selection
- **Rejected**: Adds UI complexity, and drag-and-drop provides minimal value when folder selection is available

**Implementation:**
- Remove `setAcceptDrops(True)`, `dragEnterEvent()`, `dropEvent()` from MainWindow
- Add "Select Folder" to File menu
- Use `QFileDialog.getExistingDirectory()` to open system folder picker
- Scan folder non-recursively for supported image formats
- Exclude files with `_analyzed` suffix (avoid loading previously processed images)

### Decision 2: Minimum Window Size of 1280×720

**Rationale:**
- Lowest common resolution for modern displays
- Provides sufficient space for image viewer, control panels, and navigation
- Below this size, UI elements would be cramped and unusable

**Alternative considered:**
- Minimum 1024×768 for older laptops
- **Rejected**: At 1024 width, control panels and image viewer would be too cramped; 1280 is the practical minimum for PyQt6 layout with left sidebar

**Implementation:**
- Use `QMainWindow.setMinimumSize(1280, 720)` in `__init__`
- PyQt6 enforces this automatically (user cannot resize below minimum)

### Decision 3: Dynamic Layout Using Qt Stretch Factors

**Rationale:**
- PyQt6 layout managers (QHBoxLayout, QVBoxLayout) support stretch factors for proportional resizing
- Image viewer should grow more than control panels as window expands
- Control panels should have maximum width constraint to prevent excessive stretching on ultra-wide displays

**Alternative considered:**
- Custom `resizeEvent()` with manual widget sizing calculations
- **Rejected**: More complex, error-prone, and not idiomatic for Qt applications

**Implementation:**
- Left panel (controls): Fixed maximum width 500px, stretch factor 1
- Center panel (image viewer): Stretch factor 3 (grows 3× faster than left panel)
- Use `QWidget.setMaximumWidth(500)` for control panel
- Image viewer expands naturally using layout stretch

**Layout structure:**
```
QHBoxLayout (main_layout)
├── Left Panel (stretch=1, max_width=500)
│   ├── Processing Controls
│   ├── V2 Layer Panel
│   ├── Overlay Controls
│   └── Results Display
└── Center Panel (stretch=3)
    ├── Image Viewer (auto-scales with window)
    └── Navigation Controls (prev/next, dropdown)
```

### Decision 4: Progress Dialog for Folder Loading

**Rationale:**
- Loading 100+ images can take 2-5 seconds (file system scanning, metadata extraction)
- Users need feedback that loading is in progress
- Cancel operation needed in case user selects wrong folder

**Implementation:**
- Use `QProgressDialog` with label "Loading images: X / Y"
- Update progress incrementally as each image is validated and added to batch
- Allow cancel operation (stop loading, preserve already-loaded images)

### Decision 5: Tab-Delimited Text File for Results (Not CSV)

**Rationale:**
- PRD specifies tab-delimited format explicitly
- Excel opens `.txt` files correctly if they're tab-delimited
- Simpler implementation than CSV (no quoting/escaping needed for typical filenames)
- Filename format: `[FolderName]_Analyzed.txt` (folder name embedded in filename)

**Alternative considered:**
- CSV format with proper quoting/escaping
- **Rejected**: PRD specifies tab-delimited; no user request for CSV-specific features

**Format specification:**
```
filename\tcoverage\tmonolayer_coverage\tbilayer_coverage\ttrilayer_coverage
image1.png\t45.23\t12.5\t20.3\t12.43
image2.png\t38.7\t10.2\t18.5\t10.0
```

**Header row:** Always the first line (created when file doesn't exist)
**Data rows:** Appended sequentially as images are submitted

### Decision 6: Duplicate Submission Handling with Dialog

**Rationale:**
- Users may re-analyze the same image with different parameters
- Need to decide whether to replace old result or add new row
- Dialog provides explicit user choice rather than implicit behavior

**Dialog options:**
1. **Overwrite**: Replace existing row with new values (update-in-place)
2. **Append new row**: Add new row (optionally with timestamp) for comparison
3. **Cancel**: Do nothing (user changed their mind)

**Implementation:**
- Before appending to results file, check if filename already exists in file
- If exists, show `QMessageBox` with three buttons
- Overwrite: Read file, replace matching row, write back
- Append: Simply append new row (may add timestamp column in future)
- Cancel: Return without modifying file

**Alternative considered:**
- Always overwrite (implicit)
- Always append (implicit)
- **Rejected**: Users need explicit control for different use cases (parameter tuning vs. repeatability testing)

### Decision 7: Save Analyzed Image With `_analyzed` Suffix

**Rationale:**
- Preserves original images (critical for scientific reproducibility)
- Clear naming convention indicates processed vs. original
- Allows folder to contain both originals and analyzed images
- Folder import automatically excludes `_analyzed` files (avoids loading processed images)

**Naming convention:**
- `sample1.png` → `sample1_analyzed.png`
- `experiment_042.tif` → `experiment_042_analyzed.tif`

**Format preservation:**
- Output format matches input format (PNG → PNG, TIFF → TIFF, etc.)
- Ensures downstream tools can process analyzed images

## Risks / Trade-offs

### Risk: Users expect drag-and-drop
- **Mitigation**: "File > Open Image" menu item preserved for single-image workflows
- **Mitigation**: "Select Folder" button prominently placed in File menu
- **Trade-off**: Slight learning curve for existing users (drag-and-drop users must adapt)

### Risk: Tab-delimited file may break if filenames contain tabs
- **Mitigation**: Unlikely (Windows/macOS/Linux filenames don't typically contain tabs)
- **Mitigation**: If needed in future, can escape tabs or switch to CSV with quoting

### Risk: Large folders (500+ images) may cause loading delays
- **Mitigation**: Progress dialog with cancel option
- **Mitigation**: Non-recursive scan keeps scope limited
- **Mitigation**: `_analyzed` exclusion reduces duplicate file clutter

### Risk: Results file may be corrupted if app crashes during write
- **Mitigation**: Use atomic write pattern (write to temp file, then rename)
- **Note**: Not implemented in v2.2.0 (defer to future version if users report issues)

### Risk: Duplicate detection may be slow for very large results files
- **Mitigation**: Linear search acceptable for <1000 rows (typical use case)
- **Mitigation**: If performance issue arises, can build in-memory index on load

## Migration Plan

**v2.1.1 → v2.2.0:**

1. **No data migration needed**: All existing settings, images, and results remain compatible
2. **User workflow changes:**
   - Old: Drag-and-drop images
   - New: Use "Select Folder" button
3. **Backward compatibility:**
   - Existing CSV batch export still works (v2.1.0 feature preserved)
   - Existing parameter settings preserved
   - Window geometry settings preserved
4. **Rollback:**
   - If issues arise, users can revert to v2.1.1 executable
   - No data loss (original images untouched)

**No breaking changes to analysis output format or detection algorithms.**

## Open Questions

1. **Should "Select Folder" also be a toolbar button (in addition to menu item)?**
   - PRD doesn't specify
   - Recommendation: Add to File menu first, consider toolbar in future if users request it

2. **Should progress dialog show image filenames as they load?**
   - PRD specifies "Loading images: X / Y" format
   - Recommendation: Show count only (simpler, faster); filenames may scroll too fast to be useful

3. **Should Append option include timestamp in filename column?**
   - PRD doesn't specify
   - Recommendation: Add timestamp in separate column if appending (e.g., `image1.png [2025-12-18 14:23]`)
   - Decision deferred to implementation phase

4. **Should results file be created when folder is loaded, or only when first image is submitted?**
   - PRD: "First analysis creates the file with header row"
   - Decision: Create only on first submit (not on folder load)

## Implementation Notes

- **PyQt6 Layout Managers**: Use QHBoxLayout/QVBoxLayout with stretch factors (no manual sizing)
- **File I/O**: Use pathlib.Path for cross-platform compatibility
- **Error Handling**: Show QMessageBox with actionable error messages (not just exceptions)
- **Testing**: Focus on PRD Section 4 acceptance criteria as primary validation
