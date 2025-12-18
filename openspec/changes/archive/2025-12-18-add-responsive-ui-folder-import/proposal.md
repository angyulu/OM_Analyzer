# Change: Add Responsive UI and Folder-Based Image Import

## Why

The current v2.1.1 application has usability limitations:

1. **Window resizing issues**: The application opens at a fixed 1200×800 size and does not adapt well to different screen resolutions or user-adjusted window sizes, limiting usability on smaller laptops or larger 4K displays.

2. **Drag-and-drop friction**: The current drag-and-drop workflow requires users to manually select multiple files, which is cumbersome when working with folders containing dozens or hundreds of microscope images.

3. **Export workflow gaps**: While v2.1.0 added layer detection and CSV export for batch processing, there is no per-image "Submit" functionality that saves analyzed images with overlays and appends results to a folder-specific text file for downstream analysis.

Materials science researchers need:
- A UI that works seamlessly across different screen sizes (lab computers vary widely)
- Quick folder-based image loading for typical microscopy workflows (entire experiment folders)
- Per-image analysis submission with automatic result tracking in a folder-specific file

## What Changes

This change updates the UI/UX and export workflow without touching core detection algorithms:

**1. Responsive UI (Section 3.1 of PRD_V2.2.0)**
- Set minimum window size to 1280×720 pixels
- Implement dynamic layout scaling that adapts to window resize events
- Image viewing area expands to fill available space
- Control panels (left sidebar) maintain maximum width of 400-500px
- Navigation controls and critical UI elements remain accessible at all window sizes

**2. Folder Selection Replaces Drag-and-Drop (Section 3.2 of PRD_V2.2.0)**
- Remove drag-and-drop event handlers (`dragEnterEvent`, `dropEvent`)
- Add "Select Folder" button in menu bar and toolbar
- Automatically load all supported images from selected folder (non-recursive)
- Exclude images with `_analyzed` suffix to avoid loading previously processed images
- Show progress indicator: "Loading images: [current] / [total]" with progress bar
- Preserve existing image navigation (dropdown, prev/next buttons)

**3. Per-Image Submit and Results Export (Section 3.3 of PRD_V2.2.0)**
- Add "Submit" button (enabled only when analysis parameters are valid)
- Save analyzed image with overlay as `[original_name]_analyzed.[ext]` in source folder
- Maintain tab-delimited results file: `[FolderName]_Analyzed.txt` with 5 columns:
  - `filename`, `coverage`, `monolayer_coverage`, `bilayer_coverage`, `trilayer_coverage`
- Create file with header row on first submit
- Append new row on subsequent submits
- Handle duplicate submissions with overwrite/append/cancel dialog
- Provide visual feedback (toast notification or status message)
- Error handling for file write failures

**BREAKING**: Drag-and-drop functionality will be removed. Users must use "Select Folder" or "File > Open Image" instead.

## Impact

**Affected specs:**
- NEW: `responsive-ui` - Window resizing and layout adaptation
- NEW: `folder-import` - Folder selection and batch loading
- NEW: `submit-workflow` - Per-image submission and results export
- MODIFIED (if exists): `image-loading` - Update to reflect folder-first approach
- MODIFIED (if exists): `results-export` - Add per-image submit functionality

**Affected code:**
- UPDATE: `thin_film_analyzer/ui/main_window.py`
  - Remove `dragEnterEvent()` and `dropEvent()` methods
  - Add `select_folder_dialog()` method
  - Add `submit_current_image()` method
  - Implement `setMinimumSize(1280, 720)` and layout scaling
  - Add progress dialog for folder loading
  - Add duplicate result handling dialog
- UPDATE: `thin_film_analyzer/core/export.py`
  - Add `export_single_image_with_overlay()` method
  - Add `append_result_to_text_file()` method for tab-delimited format
  - Add logic to check for existing results and handle duplicates
- UPDATE: `thin_film_analyzer/ui/image_viewer.py`
  - Ensure image viewer properly scales with window resize
- NEW: `thin_film_analyzer/ui/folder_loader.py` (optional)
  - Encapsulate folder scanning and progress tracking logic
- UPDATE: `thin_film_analyzer/config/defaults.py`
  - Add `MINIMUM_WINDOW_WIDTH = 1280`
  - Add `MINIMUM_WINDOW_HEIGHT = 720`
  - Add `CONTROL_PANEL_MAX_WIDTH = 500`

**Performance impact:**
- Folder loading with 100+ images: <5 seconds (file system scanning)
- No impact on analysis performance
- UI responsiveness maintained during folder scan (progress dialog with cancel)

**User impact:**
- Users must adapt from drag-and-drop to "Select Folder" button
- Improved workflow for typical use case (analyze entire experiment folder)
- Better experience on different screen sizes
- Per-image submit workflow enables incremental analysis and result tracking
