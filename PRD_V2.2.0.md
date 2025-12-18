<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# OM Analyzer – Product Requirements Document

**Version:** 2.2.0
**Date:** December 18, 2025
**Scope:** Incremental update to PRD_V2.1.0 focusing on UI responsiveness, image import workflow, and analysis results export.

***

## 1. Overview

This version enhances the OM Analyzer application to support different screen sizes and window configurations, simplifies image import through folder selection, and standardizes how analyzed images and numeric results are saved for downstream processing and analysis.

***

## 2. Goals and Non‑Goals

### Goals

- Provide a responsive UI that adapts to different screen resolutions and user-adjusted window sizes
- Replace drag‑and‑drop upload with a folder selection workflow that automatically loads all images in the chosen folder
- Ensure each analyzed image is saved with appropriate overlay visualization
- Maintain all analysis metrics in a unified, Excel-compatible text results file


### Non‑Goals

- No changes to core analysis algorithms, layer identification logic, or coverage calculation formulas
- No changes to supported operating systems or installation procedures
- No batch processing or "analyze all" functionality in this version

***

## 3. Functional Requirements

### 3.1 Responsive UI and Window Resizing

#### 3.1.1 Initial window sizing

- The application window must automatically adapt its layout to the user's current screen resolution on launch
- Minimum supported window size: **1280 × 720 pixels**
- If the user's screen is smaller than the minimum, the window opens at maximum available size with scrolling if necessary


#### 3.1.2 Dynamic resizing behavior

- When the user resizes the application window (maximize, restore, manual drag), the UI must automatically reflow and scale to fit the new window size
- Critical UI elements must remain visible and functional at all supported window sizes:
    - Image viewing area
    - Layer identification controls
    - Submit button
    - Navigation controls for loaded images


#### 3.1.3 Layout scaling rules

- **Image viewing area**: Expands to fill available space as window grows
- **Control panels** (side or bottom panels containing settings):
    - Grow in height with the window
    - Maximum width: 400–500 pixels
    - On very wide screens, extra horizontal space becomes margins rather than stretching controls excessively
- **Text and icons**: Maintain readable sizes; do not scale fonts or icons excessively on large displays
- **Spacing**: Margins and padding may increase slightly on larger displays to avoid cramped appearance


#### 3.1.4 Constraints

- Window cannot be resized below 1280 × 720 pixels
- All interactive controls must remain accessible (not clipped or hidden) at any valid window size

***

### 3.2 Image Import via Folder Selection

#### 3.2.1 Remove drag-and-drop

- The existing drag‑and‑drop upload interaction for images must be removed from the UI


#### 3.2.2 Folder selection control

- Add a **"Select Folder"** button (or menu item) that opens a standard system folder picker dialog
- The control must be clearly labeled and easily discoverable in the main UI


#### 3.2.3 Automatic image loading

After the user selects a folder:

- The application must automatically scan **only the selected folder** (no subfolders or recursive search)
- Load all supported image files found in the folder
- Supported image formats must include at minimum:
    - PNG (.png)
    - JPEG (.jpg, .jpeg)
    - TIFF (.tif, .tiff)
    - BMP (.bmp)
    - Any additional formats currently supported in V2.1.0


#### 3.2.4 Exclusions

- Ignore files with `_analyzed` suffix (e.g., `sample1_analyzed.png`) to avoid loading previously processed images
- Ignore non-image files without error messages


#### 3.2.5 Progress indicator

- Display a **progress indicator** while loading images from the folder
- Progress display format: **"Loading images: [current] / [total]"** (e.g., "Loading images: 35 / 220")
- Include a visual progress bar
- Allow user to cancel the loading operation if desired


#### 3.2.6 Image list display

- All loaded images must be listed or displayed in the UI (e.g., thumbnail view, list view, or navigation dropdown)
- User must be able to navigate between loaded images
- Preserve or improve the current image navigation behavior from V2.1.0


#### 3.2.7 File preservation

- The application must not modify, move, or delete any original images in the selected folder
- All processing output is written as new files (see Section 3.3)

***

### 3.3 Saving Analyzed Images and Results

#### 3.3.1 Submit button

- Add or retain a **"Submit"** button in the analysis UI for the currently displayed image
- The Submit button must be:
    - Disabled (grayed out) or hidden if layer identification settings are incomplete or invalid
    - Enabled only when all required analysis parameters for the current image are valid


#### 3.3.2 Analyzed image output

When the user clicks **Submit** for an image:

- Generate a processed version of the image containing the overlay colors representing the analyzed layers
- Save the processed image to **the same folder** as the original image
- Filename format: `[original_name]_analyzed.[ext]`
    - Example: `sample1.png` → `sample1_analyzed.png`
- The output image format must match the original image format


#### 3.3.3 Results file format

For each submitted/analyzed image, write one row of results to a tab-delimited text file containing exactly five columns:


| Column | Description |
| :-- | :-- |
| filename | Original image filename (including extension) |
| coverage | Total coverage percentage or value |
| monolayer_coverage | Monolayer coverage percentage or value |
| bilayer_coverage | Bilayer coverage percentage or value |
| trilayer_coverage | Trilayer coverage percentage or value |

#### 3.3.4 Results file naming and location

- **Filename**: `[FolderName]_Analyzed.txt`
    - `[FolderName]` is the name of the folder selected in Section 3.2
    - Example: If folder is `Experiment_A`, results file is `Experiment_A_Analyzed.txt`
- **Location**: The same folder selected by the user
- **Encoding**: UTF-8


#### 3.3.5 Results file creation and appending

- **Header row**: The first line must contain column headers:

```
filename	coverage	monolayer_coverage	bilayer_coverage	trilayer_coverage
```

(Tab characters between each field)
- **If file does not exist**: Create a new file with the header row, then append the first data row
- **If file already exists**: Append the new data row at the end of the file without modifying existing content or adding a new header


#### 3.3.6 Re-submitting the same image

If the user clicks Submit on an image that already has a result row in the `[FolderName]_Analyzed.txt` file:

- Display a dialog with the message:
**"Results for this image already exist. What would you like to do?"**
- Provide three buttons:
    - **Overwrite**: Replace the existing row with new values
    - **Append new row**: Add a new row with the current timestamp or analysis iteration
    - **Cancel**: Close dialog and do not save


#### 3.3.7 Visual feedback

- After a successful Submit operation, provide clear feedback to the user:
    - Toast notification, status bar message, or check icon
    - Indicate that the analyzed image was saved and results were written to the text file
    - Display the filename of the saved analyzed image


#### 3.3.8 Error handling

- **If saving the processed image fails**:
    - Show a clear error message to the user
    - Do not write the corresponding results row to the text file
- **If appending to the results file fails**:
    - Show an error message
    - The processed image file remains saved (if it was successfully written)
- Error messages must include actionable information (e.g., "Check folder permissions" or "Disk may be full")

***

## 4. Acceptance Criteria

### 4.1 Responsive UI

- [ ] Application launches at appropriate size on screens with resolutions from 1280×720 to 4K and higher
- [ ] Window can be resized manually; all critical controls remain visible and functional
- [ ] On ultra-wide displays, control panels do not stretch excessively (max width enforced)
- [ ] Image viewing area expands appropriately as window size increases


### 4.2 Folder loading

- [ ] "Select Folder" button opens system folder picker
- [ ] All supported image types in the selected folder are loaded
- [ ] Images with `_analyzed` suffix are ignored
- [ ] Progress indicator displays accurate count during loading (e.g., "Loading images: 15 / 50")
- [ ] Non-image files are ignored without causing errors or crashes


### 4.3 Analysis and output

- [ ] Submit button is disabled when layer settings are incomplete
- [ ] Clicking Submit generates an `[original]_analyzed.[ext]` image file in the same folder
- [ ] Results are written to `[FolderName]_Analyzed.txt` in tab-delimited format
- [ ] First analysis creates the file with header row; subsequent analyses append data rows
- [ ] Re-submitting an existing image triggers the overwrite/append/cancel dialog
- [ ] Results file can be opened in Excel with correct column separation


### 4.4 Example test case

**Scenario**: User selects folder `TestBatch` containing 3 images: `image1.png`, `image2.jpg`, `image3.tif`

**Expected results**:

- All three images load successfully
- After analyzing all three images:
    - `image1_analyzed.png`, `image2_analyzed.jpg`, `image3_analyzed.tif` exist in `TestBatch` folder
    - `TestBatch_Analyzed.txt` exists with:
        - 1 header row
        - 3 data rows with correct filenames and coverage values
    - File opens correctly in Excel with five distinct columns

***

## 5. Open Questions and Future Considerations

- **Batch processing**: Not included in V2.2.0; consider for future versions if users frequently analyze many images with identical settings
- **Subfolder support**: Current version only scans the selected folder; recursive scanning may be added in future versions
- **Image format conversion**: Current version preserves original format; consider standardized output format (e.g., always PNG) if needed
- **Results file format options**: Current version uses tab-delimited text; consider CSV or Excel (.xlsx) export in future versions

***

**End of PRD V2.2.0**

