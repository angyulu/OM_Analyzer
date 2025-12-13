# Change: Add LAB Layer Detection with Hybrid V1+V2 Pipeline

## Why

Current v1.0 can only detect "film present" vs "no film" but cannot distinguish between different layer thicknesses (monolayer, bilayer, trilayer). Materials science researchers need to quantify not just total coverage, but coverage by layer type, as optical properties vary significantly between mono/bi/trilayer thin films.

The v1.0 adaptive threshold algorithm successfully handles vignetting and detects film boundaries, but lacks the granularity to classify layer thickness within detected film regions. LAB color space L-channel (lightness) analysis can distinguish between layer thicknesses based on optical contrast differences.

## What Changes

This change adds a mandatory hybrid V1+V2 detection pipeline:

- **V1 (Film Detection)**: Existing adaptive threshold detects film vs substrate boundaries
- **V2 (Layer Classification)**: NEW LAB L-channel analysis classifies detected film pixels into monolayer, bilayer, or trilayer

**Core Features:**
- LAB color space conversion and L-channel extraction
- Vignetting correction for L-channel (similar to V1's approach)
- Two-threshold classification (T1: mono/bi boundary, T2: bi/tri boundary)
- Four auto-detection algorithms for T1/T2 (K-means, Percentile, Histogram, Otsu)
- Color-coded overlay (Red=mono, Blue=bi, Green=tri)
- Per-layer coverage statistics
- Adaptive bias parameter for fine-tuning V1 sensitivity
- Threshold locking for batch consistency
- CSV export with layer statistics

**BREAKING**: None - V1 mode continues to work unchanged. V2 layer detection is additive.

## Impact

**Affected specs:**
- NEW: `layer-detection` - LAB-based layer classification
- NEW: `batch-export` - CSV export with multi-layer statistics
- NEW: `ui-controls` - V2 panel, auto-detect button, threshold locking

**Affected code:**
- NEW: `thin_film_analyzer/core/lab_detection.py` - LAB layer detection functions
- NEW: `thin_film_analyzer/core/detection_algorithms.py` - Auto-threshold detection
- UPDATE: `thin_film_analyzer/core/processor.py` - Add `process_image_hybrid()`
- UPDATE: `thin_film_analyzer/core/overlay.py` - Color-coded layer overlays
- UPDATE: `thin_film_analyzer/models/detection_result.py` - Add layer fields
- UPDATE: `thin_film_analyzer/models/batch_session.py` - Threshold locking
- UPDATE: `thin_film_analyzer/core/export.py` - CSV with layer stats
- UPDATE: `thin_film_analyzer/ui/main_window.py` - V2 panel, auto-detect, adaptive bias
- UPDATE: `thin_film_analyzer/config/defaults.py` - Version to 2.1.0

**Performance impact:**
- Processing time increases from <1s to ~2-5s per image (LAB conversion + classification)
- Memory increase minimal (LAB image same size as grayscale)
- Batch processing linear scaling (no additional overhead)

**User impact:**
- Users gain layer classification capability without losing V1 functionality
- UI adds V2 panel below V1 panel (always visible)
- Learning curve: ~5 minutes to understand T1/T2 thresholds + auto-detect
