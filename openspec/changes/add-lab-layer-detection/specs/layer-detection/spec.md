# Layer Detection Specification

## ADDED Requirements

### Requirement: LAB Color Space Layer Classification

The system SHALL classify detected thin film pixels into monolayer, bilayer, or trilayer categories using LAB color space L-channel (lightness) analysis.

#### Scenario: Three-layer classification from V1 film mask

- **WHEN** V1 adaptive threshold detects film regions (binary_mask == 1)
- **AND** user provides T1 (mono/bi boundary) and T2 (bi/tri boundary) thresholds
- **THEN** system converts image to LAB color space
- **AND** extracts L-channel values only for pixels where binary_mask == 1
- **AND** classifies each film pixel as:
  - Monolayer if L < T1
  - Bilayer if T1 ≤ L < T2
  - Trilayer if L ≥ T2
- **AND** substrate pixels (binary_mask == 0) remain unclassified (value 0)

#### Scenario: Vignetting correction on L-channel

- **WHEN** vignetting correction is enabled
- **THEN** system applies local normalization to L-channel
- **AND** calculates local mean using Gaussian blur (kernel size 101×101, sigma 30)
- **AND** normalizes: L_corrected = L × (global_mean / local_mean)
- **AND** clips corrected values to range [0, 255]
- **AND** uses corrected L-values for classification

#### Scenario: Per-layer coverage statistics

- **WHEN** layer classification completes
- **THEN** system calculates four coverage percentages:
  - total_coverage: (pixels where binary_mask == 1) / total_pixels × 100
  - mono_coverage: (pixels == 1) / total_pixels × 100
  - bi_coverage: (pixels == 2) / total_pixels × 100
  - tri_coverage: (pixels == 3) / total_pixels × 100
- **AND** all percentages are floating-point with 2 decimal precision

#### Scenario: Binary mask restricts analysis to film pixels

- **WHEN** binary_mask contains substrate (0) and film (1) pixels
- **THEN** LAB classification SHALL only process pixels where binary_mask == 1
- **AND** substrate pixels (binary_mask == 0) SHALL remain 0 in output layer_mask
- **AND** processing time is reduced by skipping substrate pixels

---

### Requirement: Auto-Detection of Layer Thresholds

The system SHALL provide four algorithms to automatically detect T1 and T2 thresholds from film pixel L-channel distribution.

#### Scenario: K-means clustering auto-detection

- **WHEN** user selects K-means algorithm and clicks "Auto-Detect Thresholds"
- **THEN** system extracts L-channel values from film pixels (binary_mask == 1)
- **AND** applies K-means clustering with k=3 (mono, bi, tri clusters)
- **AND** sorts cluster centers in ascending order
- **AND** calculates T1 = midpoint between centers[0] and centers[1]
- **AND** calculates T2 = midpoint between centers[1] and centers[2]
- **AND** updates T1, T2 sliders with calculated values
- **AND** reprocesses image with new thresholds

#### Scenario: Percentile-based auto-detection

- **WHEN** user selects Percentile algorithm and clicks "Auto-Detect Thresholds"
- **THEN** system extracts L-channel values from film pixels
- **AND** calculates T1 = 33rd percentile of film L-values
- **AND** calculates T2 = 66th percentile of film L-values
- **AND** updates sliders and reprocesses image

#### Scenario: Histogram peak detection auto-detection

- **WHEN** user selects Histogram algorithm and clicks "Auto-Detect Thresholds"
- **THEN** system computes histogram of film pixel L-values
- **AND** identifies 3 peaks corresponding to mono/bi/tri layers
- **AND** calculates T1 = valley between peaks 1 and 2
- **AND** calculates T2 = valley between peaks 2 and 3
- **AND** updates sliders and reprocesses image

#### Scenario: Otsu multi-threshold auto-detection

- **WHEN** user selects Otsu algorithm and clicks "Auto-Detect Thresholds"
- **THEN** system applies multi-class Otsu's method to film L-values
- **AND** finds T1, T2 that maximize inter-class variance for 3 classes
- **AND** updates sliders and reprocesses image

#### Scenario: Auto-detection only analyzes film pixels

- **WHEN** any auto-detection algorithm runs
- **THEN** algorithm SHALL only analyze L-values where binary_mask == 1
- **AND** substrate pixels (binary_mask == 0) SHALL be excluded from analysis
- **AND** ensures threshold calculation based on film characteristics only

#### Scenario: Manual threshold override after auto-detection

- **WHEN** auto-detection completes and sets T1, T2
- **THEN** user can manually adjust T1, T2 sliders for fine-tuning
- **AND** image reprocesses in real-time with manual threshold values
- **AND** manual values override auto-detected values until next auto-detect

---

### Requirement: Color-Coded Layer Overlay Visualization

The system SHALL generate a color-coded overlay image showing layer classification with distinct colors for each layer type.

#### Scenario: Three-color layer overlay

- **WHEN** layer classification completes
- **THEN** system generates overlay image where:
  - Monolayer pixels are Red (RGB: 255, 0, 0)
  - Bilayer pixels are Blue (RGB: 0, 0, 255)
  - Trilayer pixels are Green (RGB: 0, 255, 0)
  - Substrate pixels are transparent
- **AND** overlay blends with original image using user-specified opacity (0-100%)

#### Scenario: Overlay visibility toggle

- **WHEN** user unchecks "Show Overlay" checkbox
- **THEN** overlay is completely hidden
- **AND** only original image is displayed
- **WHEN** user checks "Show Overlay" checkbox
- **THEN** color-coded overlay is displayed with current opacity setting

#### Scenario: Overlay opacity control

- **WHEN** user adjusts overlay opacity slider (0-100%)
- **THEN** overlay transparency updates in real-time
- **AND** 0% opacity makes overlay invisible
- **AND** 100% opacity makes overlay fully opaque

---

### Requirement: Adaptive Bias for V1 Threshold Fine-Tuning

The system SHALL provide an adaptive bias parameter to fine-tune V1 adaptive threshold sensitivity.

#### Scenario: Negative bias detects more film

- **WHEN** user sets adaptive bias to negative value (e.g., -5)
- **THEN** effective threshold = adaptive_c + adaptive_bias
- **AND** lower effective threshold detects more film (weaker signal accepted)
- **AND** useful for samples with low contrast or thin flakes

#### Scenario: Positive bias detects less film

- **WHEN** user sets adaptive bias to positive value (e.g., +5)
- **THEN** effective threshold = adaptive_c + adaptive_bias
- **AND** higher effective threshold detects less film (stronger signal required)
- **AND** useful for reducing false positives or noisy backgrounds

#### Scenario: Zero bias maintains default behavior

- **WHEN** user sets adaptive bias to 0
- **THEN** effective threshold = adaptive_c (unchanged from v1.0)
- **AND** backward compatible with v1.0 detection behavior

#### Scenario: Bias range limits

- **WHEN** user adjusts adaptive bias
- **THEN** value is constrained to range [-10, +10]
- **AND** UI spinbox prevents out-of-range values
- **AND** provides appropriate sensitivity adjustment without extreme values
