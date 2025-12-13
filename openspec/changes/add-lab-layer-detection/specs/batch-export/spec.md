# Batch Processing and Export Specification

## ADDED Requirements

### Requirement: Threshold Locking for Batch Consistency

The system SHALL provide threshold locking to ensure consistent T1 and T2 values across batch processing.

#### Scenario: Lock thresholds for batch processing

- **WHEN** user clicks "Lock Thresholds" button (icon changes to 🔒)
- **THEN** T1 and T2 sliders are disabled
- **AND** current T1, T2 values are stored in batch session
- **AND** all subsequent image processing uses locked T1, T2 values
- **AND** prevents accidental threshold changes during batch analysis

#### Scenario: Unlock thresholds for manual tuning

- **WHEN** user clicks "Unlock Thresholds" button (icon changes to 🔓)
- **THEN** T1 and T2 sliders are enabled
- **AND** user can adjust thresholds for current image
- **AND** locked values are cleared from batch session

#### Scenario: Locked thresholds persist across image navigation

- **WHEN** thresholds are locked
- **AND** user navigates to next/previous image
- **THEN** new image is processed with locked T1, T2 values
- **AND** sliders remain disabled
- **AND** ensures consistency across batch

#### Scenario: Visual indicator shows lock status

- **WHEN** thresholds are locked
- **THEN** lock button displays 🔒 icon
- **AND** button tooltip shows "Unlock Thresholds"
- **WHEN** thresholds are unlocked
- **THEN** lock button displays 🔓 icon
- **AND** button tooltip shows "Lock Thresholds"

---

### Requirement: CSV Export with Layer Statistics

The system SHALL export batch processing results to CSV format with per-image layer statistics and summary statistics.

#### Scenario: Export layer coverage to CSV

- **WHEN** user selects "Export Results to CSV" (Ctrl+E)
- **THEN** system creates CSV file with columns:
  - filename
  - coverage_percentage (total from V1)
  - mono_coverage
  - bi_coverage
  - tri_coverage
- **AND** each row contains one processed image
- **AND** all percentage values have 2 decimal precision

#### Scenario: CSV includes summary statistics

- **WHEN** CSV export completes
- **THEN** file includes summary section at bottom:
  - SUMMARY STATISTICS header row
  - Mean Coverage (%), Std Dev Coverage (%), Min Coverage (%), Max Coverage (%)
  - Mean Monolayer (%), Std Dev Monolayer (%), Min Monolayer (%), Max Monolayer (%)
  - Mean Bilayer (%), Std Dev Bilayer (%), Min Bilayer (%), Max Bilayer (%)
  - Mean Trilayer (%), Std Dev Trilayer (%), Min Trilayer (%), Max Trilayer (%)
- **AND** summary calculated from all processed images in batch

#### Scenario: CSV handles missing layer data

- **WHEN** some images processed with V1 only (no layer detection)
- **THEN** layer coverage columns contain empty values or "N/A"
- **AND** summary statistics calculated only from images with layer data
- **AND** CSV remains valid format

#### Scenario: CSV filename defaults to timestamp

- **WHEN** user exports CSV
- **THEN** default filename is "results_YYYYMMDD_HHMMSS.csv"
- **AND** user can override with custom filename in save dialog
- **AND** prevents accidental overwrite of previous exports

---

### Requirement: Overlay Image Export for Batch

The system SHALL export color-coded overlay images for all processed images in batch.

#### Scenario: Export overlay images to directory

- **WHEN** user selects "Export Overlay Images"
- **THEN** system prompts for output directory
- **AND** saves overlay image for each processed image
- **AND** filename format: "{original_name}_overlay.png"
- **AND** preserves original image resolution

#### Scenario: Overlay export includes layer colors

- **WHEN** overlay images are exported
- **THEN** each image contains color-coded layer overlay:
  - Red for monolayer
  - Blue for bilayer
  - Green for trilayer
- **AND** overlay blended with original image at current opacity setting
- **AND** produces publication-ready visualization

#### Scenario: Overlay export progress feedback

- **WHEN** exporting large batch of overlay images
- **THEN** system displays progress dialog
- **AND** shows "Processing image X of N"
- **AND** allows user to cancel export mid-process
- **AND** completed images are saved even if user cancels

---

### Requirement: Batch Processing with Consistent Parameters

The system SHALL process multiple images with consistent V1 and V2 parameters.

#### Scenario: Process all loaded images

- **WHEN** user selects "Process All Images" (Ctrl+P)
- **THEN** system processes all images in current batch
- **AND** uses current V1 parameters (adaptive threshold, noise reduction, morphological ops)
- **AND** uses current V2 parameters (T1, T2, auto-detect algorithm if unlocked)
- **AND** respects locked T1, T2 values if thresholds are locked

#### Scenario: Batch processing progress indicator

- **WHEN** batch processing starts
- **THEN** system displays progress dialog with:
  - "Processing image X of N" message
  - Progress bar (0-100%)
  - Estimated time remaining
  - Cancel button
- **AND** updates progress after each image completes
- **AND** allows user to cancel remaining images

#### Scenario: Batch processing wait cursor

- **WHEN** processing individual image (not batch)
- **THEN** system displays wait cursor (hourglass/spinner)
- **AND** status message shows "Processing..."
- **AND** cursor restored to normal when processing completes
- **AND** cursor restored even if processing error occurs (try/finally block)

#### Scenario: Batch processing performance

- **WHEN** processing batch of 50 images (2000×1500 pixels each)
- **THEN** total processing time is <10 minutes (average <12s per image)
- **AND** memory usage remains <2GB
- **AND** UI remains responsive (not frozen)
- **AND** user can cancel batch at any time
