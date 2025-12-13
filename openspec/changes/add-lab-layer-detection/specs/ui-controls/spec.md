# UI Controls and Panels Specification

## ADDED Requirements

### Requirement: V2 Layer Classification Panel

The system SHALL provide a dedicated V2 panel in the main window for layer classification controls and results.

#### Scenario: V2 panel layout and organization

- **WHEN** main window loads
- **THEN** V2 "Layer Classification" panel is visible below V1 "Processing" panel
- **AND** panel contains (in order):
  - Algorithm dropdown (K-means, Percentile, Histogram, Otsu)
  - "Auto-Detect Thresholds" button
  - T1 slider with label "Mono/Bi Boundary (T1)"
  - T2 slider with label "Bi/Tri Boundary (T2)"
  - "Lock Thresholds" toggle button (🔓/🔒)
  - Results section showing: Total Coverage, Monolayer, Bilayer, Trilayer

#### Scenario: Algorithm dropdown selection

- **WHEN** user opens algorithm dropdown
- **THEN** dropdown shows four options:
  - "K-means Clustering" (default)
  - "Percentile-Based"
  - "Histogram Peak Detection"
  - "Otsu Multi-Threshold"
- **AND** selected algorithm is highlighted
- **AND** tooltip explains "Algorithm for auto-detecting T1, T2 thresholds"

#### Scenario: Auto-detect button triggers threshold calculation

- **WHEN** user clicks "Auto-Detect Thresholds" button
- **THEN** system runs selected algorithm on current image
- **AND** updates T1, T2 slider values with calculated thresholds
- **AND** immediately reprocesses image with new thresholds
- **AND** updates layer statistics display
- **AND** button disabled during processing to prevent double-click

#### Scenario: T1 and T2 slider controls

- **WHEN** user adjusts T1 slider
- **THEN** slider value updates in real-time (range 0-255)
- **AND** slider label shows current value: "Mono/Bi Boundary (T1): 85"
- **AND** image reprocesses immediately with new T1
- **AND** layer statistics update
- **WHEN** user adjusts T2 slider
- **THEN** slider value updates in real-time (range 0-255)
- **AND** slider label shows current value: "Bi/Tri Boundary (T2): 170"
- **AND** image reprocesses immediately with new T2

#### Scenario: T1 must be less than T2 validation

- **WHEN** user adjusts T1 to value ≥ T2
- **THEN** system automatically adjusts T2 to T1 + 1
- **OR** prevents T1 from exceeding T2 - 1
- **AND** displays tooltip warning "T1 must be less than T2"

#### Scenario: Layer statistics display

- **WHEN** image processing completes
- **THEN** V2 panel results section shows:
  - "Total Coverage: XX.XX%" (from V1 binary mask)
  - "Monolayer: XX.XX%" (from V2 classification)
  - "Bilayer: XX.XX%" (from V2 classification)
  - "Trilayer: XX.XX%" (from V2 classification)
- **AND** percentages have 2 decimal precision
- **AND** results update in real-time as parameters change

---

### Requirement: V1 Panel Adaptive Bias Control

The system SHALL add adaptive bias spinbox to V1 processing panel for fine-tuning threshold sensitivity.

#### Scenario: Adaptive bias spinbox in V1 panel

- **WHEN** main window loads
- **THEN** V1 "Processing" panel contains "Adaptive Bias" spinbox
- **AND** spinbox located below "Adaptive C" control
- **AND** spinbox range is -10 to +10
- **AND** spinbox default value is 0
- **AND** spinbox step size is 1

#### Scenario: Adaptive bias tooltip guidance

- **WHEN** user hovers over "Adaptive Bias" spinbox
- **THEN** tooltip displays:
  ```
  Fine-tune adaptive threshold sensitivity:
  • Negative values (-5 to -1): Detect MORE film (weaker signal)
  • Zero (0): Default behavior
  • Positive values (+1 to +5): Detect LESS film (stronger signal required)
  ```

#### Scenario: Adaptive bias updates V1 detection

- **WHEN** user changes adaptive bias value
- **THEN** image reprocesses immediately with new effective threshold
- **AND** effective_c = adaptive_c + adaptive_bias
- **AND** V1 binary mask updates
- **AND** V2 layer classification updates (uses new binary mask)
- **AND** all statistics update

---

### Requirement: Batch Menu and Actions

The system SHALL provide a "Batch" menu with actions for batch processing and export.

#### Scenario: Batch menu structure

- **WHEN** main window loads
- **THEN** menu bar contains "Batch" menu
- **AND** Batch menu contains:
  - "Process All Images" action (Ctrl+P)
  - Separator
  - "Export Results to CSV" action (Ctrl+E)
  - "Export Overlay Images" action

#### Scenario: Process All Images action

- **WHEN** user selects "Process All Images" or presses Ctrl+P
- **THEN** system processes all loaded images in batch
- **AND** displays progress dialog
- **AND** action disabled if no images loaded
- **AND** action disabled during processing

#### Scenario: Export Results to CSV action

- **WHEN** user selects "Export Results to CSV" or presses Ctrl+E
- **THEN** system prompts for CSV save location
- **AND** exports all processed results to CSV
- **AND** action disabled if no processed results available

#### Scenario: Export Overlay Images action

- **WHEN** user selects "Export Overlay Images"
- **THEN** system prompts for output directory
- **AND** exports color-coded overlay images for all processed images
- **AND** action disabled if no processed results available

---

### Requirement: Processing Feedback and Wait Cursor

The system SHALL provide visual feedback during image processing operations.

#### Scenario: Wait cursor during single image processing

- **WHEN** system processes individual image (parameter change, navigation)
- **THEN** cursor changes to wait cursor (hourglass or spinner)
- **AND** status bar shows "Processing..." message
- **AND** cursor restored to normal when processing completes
- **AND** cursor restored even on processing error (try/finally pattern)

#### Scenario: Progress dialog during batch processing

- **WHEN** system processes batch of images
- **THEN** modal progress dialog displays showing:
  - Title: "Processing Batch"
  - Message: "Processing image X of N"
  - Progress bar (0-100%)
  - "Cancel" button
- **AND** dialog updates after each image completes
- **AND** dialog closes when batch completes or user cancels

#### Scenario: Cancel batch processing

- **WHEN** user clicks "Cancel" in progress dialog
- **THEN** system stops processing remaining images
- **AND** images processed so far are retained
- **AND** partial results can still be exported
- **AND** progress dialog closes

---

### Requirement: Real-Time Parameter Updates

The system SHALL update all image processing and visualization in real-time as parameters change.

#### Scenario: V1 parameter real-time updates

- **WHEN** user adjusts any V1 parameter (threshold, adaptive C, bias, blur, morphology)
- **THEN** image reprocesses within <200ms
- **AND** binary mask overlay updates
- **AND** coverage statistics update
- **AND** V2 layer classification updates (uses new binary mask)

#### Scenario: V2 parameter real-time updates

- **WHEN** user adjusts T1 or T2 slider
- **THEN** layer classification reprocesses within <200ms
- **AND** color-coded overlay updates
- **AND** layer statistics (mono/bi/tri coverage) update
- **AND** overlay blends with original image at current opacity

#### Scenario: Overlay controls real-time updates

- **WHEN** user toggles "Show Overlay" checkbox
- **THEN** overlay visibility changes immediately (<50ms)
- **AND** no reprocessing triggered
- **WHEN** user adjusts overlay opacity slider
- **THEN** overlay transparency updates immediately
- **AND** no reprocessing triggered

---

## MODIFIED Requirements

### Requirement: Overlay Visibility Toggle Fix

The overlay visibility toggle SHALL properly hide overlay when unchecked.

**Modified behavior**: Add explicit `else` clause to hide overlay when checkbox is unchecked.

#### Scenario: Show overlay when checked

- **WHEN** "Show Overlay" checkbox is checked
- **THEN** system displays color-coded overlay
- **AND** blends overlay with original image at current opacity
- **AND** overlay updates when parameters change

#### Scenario: Hide overlay when unchecked

- **WHEN** "Show Overlay" checkbox is unchecked
- **THEN** system explicitly calls `image_viewer.set_overlay(None, 0)`
- **AND** only original image is visible
- **AND** no overlay is rendered
- **AND** overlay remains hidden when parameters change

#### Scenario: Toggle preserves overlay state

- **WHEN** user unchecks then rechecks "Show Overlay"
- **THEN** overlay reappears with current layer classification
- **AND** uses current opacity setting
- **AND** no reprocessing required
