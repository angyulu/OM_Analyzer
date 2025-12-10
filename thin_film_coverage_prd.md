# Product Requirements Document
## Thin Film Coverage Analyzer

**Version:** 1.0  
**Date:** December 2024  
**Author:** [Your Name]  
**Status:** Draft

---

## 1. Overview

### 1.1 Problem Statement
Measuring thin film coverage from optical microscope (OM) images is currently a manual, time-consuming process prone to inconsistency. Team members need a standardized, efficient way to calculate coverage percentages across multiple images with varying magnification scales.

### 1.2 Solution
A standalone Python desktop application that allows users to batch-process OM images, calibrate for different objective scales, and automatically calculate thin film coverage percentages.

### 1.3 Users
- Internal team of ~5 researchers/engineers
- Assumes basic familiarity with optical microscopy and image analysis concepts

---

## 2. Goals & Success Metrics

| Goal | Metric | Target |
|------|--------|--------|
| Reduce analysis time | Time per image batch | < 2 min for 10 images |
| Improve consistency | Coverage variance between users | < 5% difference |
| Ease of use | Training time for new user | < 15 minutes |
| Reliability | Successful processing rate | > 95% of images |

---

## 3. User Stories

### 3.1 Core Workflow
> As a researcher, I want to drag and drop multiple OM images into the application, set the scale calibration, and get coverage percentages for all images so I can efficiently analyze my samples.

### 3.2 Scale Calibration
> As a user, I want to save and reuse scale presets for different microscope objectives (5x, 10x, 20x, 50x, 100x) so I don't have to recalibrate every session.

### 3.3 Results Export
> As a user, I want to export results to CSV with image filenames and coverage values so I can include the data in my reports and further analysis.

### 3.4 Visual Verification
> As a user, I want to see a preview of the detected thin film regions overlaid on my image so I can verify the detection is accurate before accepting results.

---

## 4. Functional Requirements

### 4.1 Image Input
| ID | Requirement | Priority |
|----|-------------|----------|
| F1.1 | Drag-and-drop multiple images onto application window | Must Have |
| F1.2 | Support common formats: PNG, JPG, TIFF, BMP | Must Have |
| F1.3 | File browser as alternative to drag-and-drop | Should Have |
| F1.4 | Display thumbnail previews of loaded images | Should Have |
| F1.5 | Support for batch sizes up to 100 images | Must Have |

### 4.2 Scale Calibration
| ID | Requirement | Priority |
|----|-------------|----------|
| F2.1 | Manual input of scale (µm/pixel or px/µm) | Must Have |
| F2.2 | Draw-line calibration tool (draw line, enter known length) | Should Have |
| F2.3 | Save/load scale presets by objective name | Must Have |
| F2.4 | Apply same scale to entire batch or per-image | Should Have |

### 4.3 Image Processing & Detection
| ID | Requirement | Priority |
|----|-------------|----------|
| F3.1 | Automatic thin film region detection via thresholding | Must Have |
| F3.2 | Adjustable threshold sensitivity slider | Must Have |
| F3.3 | Option to select detection method (threshold, edge-based, ML) | Could Have |
| F3.4 | Noise reduction / preprocessing toggle | Should Have |
| F3.5 | Manual ROI selection to exclude edges/artifacts | Should Have |

### 4.4 Coverage Calculation
| ID | Requirement | Priority |
|----|-------------|----------|
| F4.1 | Calculate coverage as percentage of total area | Must Have |
| F4.2 | Display coverage in both % and absolute area (µm²) | Should Have |
| F4.3 | Show film vs. substrate pixel counts | Should Have |
| F4.4 | Batch calculation with progress indicator | Must Have |

### 4.5 Visualization
| ID | Requirement | Priority |
|----|-------------|----------|
| F5.1 | Overlay detected regions on original image (color mask) | Must Have |
| F5.2 | Toggle overlay on/off | Must Have |
| F5.3 | Adjustable overlay transparency | Should Have |
| F5.4 | Side-by-side view: original vs. processed | Could Have |

### 4.6 Results & Export
| ID | Requirement | Priority |
|----|-------------|----------|
| F6.1 | Results table showing filename, coverage %, area | Must Have |
| F6.2 | Export to CSV | Must Have |
| F6.3 | Export processed images with overlay | Should Have |
| F6.4 | Summary statistics (mean, std dev, min, max) | Should Have |
| F6.5 | Export to Excel (.xlsx) | Could Have |

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Process a single 2048×2048 image in < 3 seconds
- UI remains responsive during batch processing
- Memory usage < 2 GB for 50-image batch

### 5.2 Usability
- Single-window interface (no complex navigation)
- All primary functions accessible within 2 clicks
- Tooltips for all controls
- Keyboard shortcuts for common actions

### 5.3 Compatibility
- Windows 10/11 (primary)
- macOS support (nice to have)
- Python 3.9+ runtime

### 5.4 Reliability
- Graceful handling of corrupted/unsupported images
- Auto-save settings between sessions
- No data loss on application crash

---

## 6. Technical Architecture

### 6.1 Technology Stack
| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| UI Framework | PyQt6 or Tkinter (simple) |
| Image Processing | OpenCV, scikit-image |
| Data Handling | NumPy, Pandas |
| Packaging | PyInstaller (standalone .exe) |

### 6.2 Core Algorithm (Baseline)
```
1. Load image → Convert to grayscale
2. Apply Gaussian blur (noise reduction)
3. Apply adaptive or Otsu thresholding
   - Film = lighter regions (higher intensity)
   - Substrate = darker regions (lower intensity)
4. Morphological operations (open/close) to clean mask
5. Calculate: coverage = (film_pixels / total_pixels) × 100
6. Optional: Apply scale factor for absolute area
```

### 6.3 Scale Calibration Modes
| Mode | Description |
|------|-------------|
| Manual Input | User enters µm/pixel directly based on known objective |
| Draw Line | User draws line on image, enters known length |
| Scale Bar Detection | Auto-detect scale bar in image (future enhancement) |
| Preset Selection | Load saved calibration for specific objective |

**Note:** When scale bar is present in image, user should define ROI to exclude it from coverage calculation.

### 6.4 File Structure (Proposed)
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

---

## 7. UI Wireframe (Conceptual)

```
┌─────────────────────────────────────────────────────────────────┐
│  Thin Film Coverage Analyzer                            [—][□][×]│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────┐  ┌──────────────────────────┐ │
│  │                              │  │ Scale Settings           │ │
│  │                              │  │ ┌────────────────────┐   │ │
│  │     [Drag & Drop Images]     │  │ │ Preset: [10x ▼]    │   │ │
│  │                              │  │ └────────────────────┘   │ │
│  │         or click to          │  │ Scale: [0.65] µm/px     │ │
│  │         browse files         │  │ [Calibrate from image]  │ │
│  │                              │  ├──────────────────────────┤ │
│  └──────────────────────────────┘  │ Detection Settings       │ │
│                                    │ Threshold: [====●===]    │ │
│  ┌──────────────────────────────┐  │ [x] Noise reduction     │ │
│  │ Loaded Images (0)            │  │ [ ] Show overlay        │ │
│  │ ─────────────────────────    │  ├──────────────────────────┤ │
│  │                              │  │ [  Process All  ]       │ │
│  │                              │  └──────────────────────────┘ │
│  └──────────────────────────────┘                               │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Results                                                    │ │
│  │ ┌──────────────────┬────────────┬────────────────────────┐ │ │
│  │ │ Filename         │ Coverage % │ Area (µm²)             │ │ │
│  │ ├──────────────────┼────────────┼────────────────────────┤ │ │
│  │ │                  │            │                        │ │ │
│  │ └──────────────────┴────────────┴────────────────────────┘ │ │
│  │ Mean: --% | Std Dev: --% | [Export CSV] [Export Images]   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Poor detection on low-contrast images | High | Medium | Provide manual threshold adjustment; add preprocessing options |
| Different thin film types need different algorithms | Medium | Medium | Start with configurable thresholding; plan for plugin architecture |
| Scale bar in image interferes with detection | Medium | High | ROI selection to exclude scale bar region; option to crop bottom N pixels |
| Team members use different monitor calibrations | Low | Low | Rely on numeric output rather than visual judgment |

---

## 9. Future Considerations (Out of Scope for v1.0)

- Machine learning-based segmentation for complex samples
- Automatic scale bar detection from image
- Multi-region analysis (coverage per quadrant)
- Time-series tracking (same sample over time)
- Integration with lab notebook software
- Cloud storage for results

---

## 10. Resolved Questions

1. **What defines "thin film" vs. "substrate" visually?**  
   → Thin film = lighter regions, Substrate = darker regions

2. **Do images contain scale bars?**  
   → Both situations possible. App must support manual scale input AND handle images with embedded scale bars (via ROI exclusion).

3. **Are there reference images with known coverage for validation?**  
   → No ground truth available. Validation approach below.

## 11. Validation Approach (No Ground Truth)

Since no reference images with known coverage exist, validation will rely on:

| Method | Description |
|--------|-------------|
| Visual Verification | Overlay mask on original; user confirms detection accuracy |
| Synthetic Test Images | Create artificial images with known coverage (e.g., 25%, 50%, 75%) |
| Cross-User Consistency | Multiple team members process same images; compare results |
| Manual Spot-Check | Manually count pixels in small ROI; compare to tool output |
| Threshold Sensitivity | Document how coverage changes with ±10% threshold adjustment |

## 12. Remaining Open Questions

1. **What's the typical image resolution** from your microscope?
2. **Are there any edge cases** (partial coverage, multilayer films, defects)?
3. **What objectives are most commonly used?** (for default presets)

---

## 13. Appendix

### A. Glossary
- **Coverage:** Percentage of image area covered by thin film
- **OM:** Optical Microscope
- **ROI:** Region of Interest
- **Threshold:** Pixel intensity cutoff for binary segmentation

### B. References
- OpenCV documentation: https://docs.opencv.org/
- scikit-image: https://scikit-image.org/
- PyQt6: https://www.riverbankcomputing.com/software/pyqt/

---

*End of Document*
