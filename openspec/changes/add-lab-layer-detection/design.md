# Design: LAB Layer Detection System

## Context

The Thin Film Analyzer v1.0 uses adaptive threshold on grayscale images to detect film regions, successfully handling vignetting (darker edges, brighter center). However, grayscale analysis cannot distinguish layer thickness because it treats all "brighter than substrate" pixels equally.

LAB color space separates lightness (L) from color information (A, B), making it ideal for thickness classification based on optical contrast. The v2.1.0 system must integrate LAB analysis while preserving v1.0's robust film boundary detection.

**Stakeholders:**
- Materials science researchers (end users)
- Single developer (implementation + maintenance)

**Constraints:**
- Must maintain v1.0 backward compatibility
- Processing time must remain <5s per image
- Non-programmer users require simple UI
- Fully offline (no external APIs)

## Goals / Non-Goals

**Goals:**
- Classify detected film into mono/bi/trilayer categories
- Provide automatic threshold detection (reduce manual tuning)
- Enable batch processing with consistent parameters
- Export layer statistics to CSV for analysis
- Maintain <5s processing time per 2000×1500 image

**Non-Goals:**
- Detecting more than 3 layer types (mono/bi/tri sufficient for current research)
- Real-time video processing (static images only)
- Cloud-based processing or collaboration features
- Layer thickness in nanometers (optical contrast classification only)

## Decisions

### Decision 1: Mandatory Hybrid V1+V2 Architecture

**What**: V2 layer detection ALWAYS uses V1 binary mask as input. V2 only analyzes pixels where V1 detected film.

**Why**:
- V1 adaptive threshold robustly handles vignetting and substrate detection
- LAB L-channel classification works best on normalized regions (film pixels only)
- Avoids duplicate substrate detection logic
- Simpler mental model: V1 finds "where", V2 classifies "what type"

**Alternatives considered**:
- **Standalone V2 mode**: Would require reimplementing vignetting correction for LAB space, duplicating V1 logic
- **Optional hybrid toggle**: Adds UI complexity; mandatory hybrid is simpler to understand and maintain

**Trade-offs**:
- ✅ Simplicity: Single processing path, less UI clutter
- ✅ Robustness: Leverages proven V1 boundary detection
- ❌ Flexibility: Cannot run V2 without V1 (acceptable - V1 is fast and reliable)

### Decision 2: Two Thresholds (T1, T2), Not Three

**What**: Use exactly 2 thresholds to split film pixels into 3 categories (mono/bi/tri).

**Why**:
- Substrate already excluded by V1 binary mask
- Simpler mental model: T1 = mono/bi boundary, T2 = bi/tri boundary
- Reduces parameter tuning complexity

**Alternatives considered**:
- **Three thresholds (T1, T2, T3)**: Would create 4 categories including substrate, but substrate is already handled by V1
- **Single threshold**: Cannot distinguish 3 layer types

### Decision 3: Four Auto-Detection Algorithms

**What**: Provide K-means, Percentile, Histogram, Otsu multi-threshold algorithms.

**Why**:
- Different images have different characteristics (contrast, noise, layer distribution)
- K-means works well for most cases (default), others provide fallbacks
- User can try different algorithms via dropdown (no coding required)

**Algorithms**:
1. **K-means (default)**: Clusters L-values into 3 groups, robust to noise
2. **Percentile**: Uses 33rd/66th percentiles, simple and fast
3. **Histogram**: Finds peaks in L-distribution, good for high-contrast images
4. **Otsu multi-threshold**: Mathematical optimization, good for distinct modes

**Alternatives considered**:
- **Single algorithm**: May fail on diverse image types
- **Manual only**: Too time-consuming for batch processing

**Trade-offs**:
- ✅ Flexibility: Works across diverse sample types
- ❌ Complexity: 4 algorithms to test/maintain
- Mitigation: Shared interface, well-documented behavior

### Decision 4: Vignetting Correction on L-Channel

**What**: Apply local normalization to L-channel before classification.

**Why**:
- Vignetting affects lightness even within film regions
- Without correction, edge flakes misclassified as thinner layers
- Same principle as V1's adaptive threshold

**Implementation**:
```python
local_mean = cv2.GaussianBlur(L_channel, (101, 101), 30)
global_mean = np.mean(L_channel)
L_corrected = L_channel * (global_mean / (local_mean + 1e-6))
```

**Alternatives considered**:
- **No correction**: Simple but inaccurate for vignetted images
- **Correction on full image**: Wastes computation on substrate pixels

**Decision**: Apply correction only to film pixels (masked by V1 result)

### Decision 5: Color-Coded Overlay (Red/Blue/Green)

**What**: Monolayer=Red, Bilayer=Blue, Trilayer=Green

**Why**:
- Visual distinction helps users verify classification
- RGB colors distinct even for colorblind users
- Existing v1.0 overlay system easily extended

**Alternatives considered**:
- **Grayscale intensity**: Less intuitive, harder to distinguish
- **Heatmap**: Overkill for 3 discrete categories

### Decision 6: Threshold Locking for Batch Consistency

**What**: Lock/unlock button disables T1/T2 sliders. When locked, all images use same thresholds.

**Why**:
- Scientific reproducibility requires consistent parameters across batch
- Prevents accidental threshold changes between images
- Visual indicator (🔒/🔓) makes lock status clear

**Alternatives considered**:
- **No locking**: Users might accidentally change thresholds mid-batch
- **Auto-lock on batch load**: Too aggressive, reduces flexibility

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| LAB detection fails on low-contrast samples | High | Provide manual T1/T2 override; multiple auto-detect algorithms |
| Processing time >5s for large images | Medium | Optimize numpy operations; acceptable given added value |
| UI too complex with V1+V2 panels | Medium | Keep V2 panel compact; provide tooltips; default to K-means |
| Auto-detect produces poor thresholds | Medium | Allow manual tuning post-auto-detect; test on diverse samples |
| Breaking v1.0 functionality | High | Extensive testing; v1.0 code path unchanged when V2 not used |

## Migration Plan

**Backward Compatibility:**
- V1.0 detection remains unchanged (no code modifications to v1.0 pipeline)
- Settings files gain new fields (T1, T2, auto_algorithm) with defaults
- Existing settings load correctly (new fields use defaults)

**Rollout:**
1. Release v2.1.0 with V2 panel visible by default
2. Existing users see new panel with sensible defaults (T1=85, T2=170)
3. Documentation updated to explain layer detection workflow
4. Tutorial video demonstrates V1+V2 usage

**Rollback:**
- If v2.1.0 has critical bugs, users can ignore V2 panel and use V1 results only
- No data loss (CSV export backward-compatible)

## Open Questions

1. **Default T1/T2 values**: PRD suggests T1=85, T2=170. Are these optimal for most samples?
   - Resolution: Test on user's real data during implementation, adjust defaults if needed

2. **Processing indicator**: PRD mentions wait cursor. Should we add a progress bar for batch processing?
   - Resolution: Phase 1 uses wait cursor. If batch processing is slow, add progress bar in Phase 4.

3. **Layer naming**: "Monolayer", "Bilayer", "Trilayer" vs "1L", "2L", "3L"?
   - Resolution: Use full names in UI (clearer for non-experts), abbreviations in CSV headers

4. **CSV decimal precision**: How many decimal places for coverage percentages?
   - Resolution: 2 decimal places (e.g., 45.23%) - sufficient precision without clutter
