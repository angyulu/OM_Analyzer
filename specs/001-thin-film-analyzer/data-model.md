# Data Model
## Thin Film Coverage Analyzer

**Date**: 2025-12-07
**Feature**: 001-thin-film-analyzer

---

## Overview

This document defines the data entities, their attributes, relationships, validation rules, and state transitions for the Thin Film Coverage Analyzer application. All entities are designed for in-memory operation with file-based persistence (JSON for settings/presets, no database required).

---

## Entity Diagram

```
┌─────────────────────┐         ┌────────────────────────┐
│  ApplicationSettings│◄───────►│    ScalePreset         │
│                     │ contains │                        │
│ - scale_presets[]   │─────────►│ - name                 │
│ - last_threshold    │         │ - scale_um_per_pixel   │
│ - overlay_transp    │         │ - created_date         │
│ - noise_reduction   │         │ - objective_ref        │
│ - window_geometry   │         └────────────────────────┘
│ - backup_timestamp  │
└─────────────────────┘

┌─────────────────────┐         ┌────────────────────────┐
│    BatchSession     │◄───────►│        Image           │
│                     │ contains │                        │
│ - image_refs[]      │─────────►│ - filename             │
│ - scale_calibration │         │ - file_path            │
│ - threshold         │         │ - dimensions           │
│ - roi_settings      │         │ - format               │
│ - summary_stats     │         │ - status               │
└──────────┬──────────┘         └───────┬────────────────┘
           │                            │
           │                            │ has
           │ contains                   │
           ▼                            ▼
┌─────────────────────┐         ┌────────────────────────┐
│  DetectionResult    │         │  ROI (optional)        │
│                     │         │                        │
│ - image_ref         │         │ - x, y, width, height  │
│ - coverage_pct      │         └────────────────────────┘
│ - area_um2          │
│ - threshold_value   │
│ - roi_coords        │
│ - film_pixel_count  │
│ - total_pixel_count │
│ - timestamp         │
└─────────────────────┘

┌─────────────────────┐
│     ErrorLog        │
│                     │
│ - error_timestamp   │
│ - error_type        │
│ - error_message     │
│ - context_info      │
│ - stack_trace       │
│ - rotation_status   │
└─────────────────────┘
```

---

## Entity Definitions

### 1. Image

**Purpose**: Represents a single loaded optical microscope image file.

**Attributes**:

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| `filename` | str | Yes | Image filename (e.g., "sample_001.png") | Non-empty string, must include extension |
| `file_path` | Path | Yes | Absolute path to image file | Must exist on filesystem, readable |
| `dimensions` | tuple[int, int] | Yes | Image dimensions (width, height) in pixels | Both > 0, typically 1024-2048 range |
| `format` | str | Yes | File format (PNG, JPG, TIFF, BMP) | Must be one of supported formats (FR-001) |
| `status` | ImageStatus (enum) | Yes | Current processing status | See ImageStatus enum below |

**ImageStatus Enum**:
```python
from enum import Enum

class ImageStatus(Enum):
    UNPROCESSED = "unprocessed"     # Loaded but not yet processed
    PROCESSING = "processing"        # Currently being processed
    COMPLETE = "complete"            # Successfully processed
    ERROR = "error"                  # Processing failed
```

**State Transitions**:
```
UNPROCESSED → PROCESSING → COMPLETE
                        → ERROR
```

**Lifecycle**:
- Created: When user drags/drops file or uses file browser (FR-001, FR-002)
- Updated: Status changes during processing
- Deleted: When user clicks "New Session" (FR-047, FR-048)

**Example**:
```python
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

@dataclass
class Image:
    filename: str
    file_path: Path
    dimensions: tuple[int, int]  # (width, height)
    format: str                   # "PNG", "JPG", "TIFF", "BMP"
    status: ImageStatus

    def validate(self) -> bool:
        """Validate image constraints."""
        if not self.filename:
            return False
        if not self.file_path.exists() or not self.file_path.is_file():
            return False
        if self.dimensions[0] <= 0 or self.dimensions[1] <= 0:
            return False
        if self.format.upper() not in ["PNG", "JPG", "JPEG", "TIFF", "BMP"]:
            return False
        return True
```

---

### 2. ScalePreset

**Purpose**: Saved calibration configuration for different microscope objectives.

**Attributes**:

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| `name` | str | Yes | Preset name (e.g., "10x objective") | Non-empty, unique across presets |
| `scale_um_per_pixel` | float | Yes | Scale calibration in µm/pixel | Must be > 0 |
| `created_date` | datetime | Yes | When preset was created | ISO format, cannot be in future |
| `objective_ref` | str | No | Optional objective magnification (e.g., "10x") | Can be empty |

**Uniqueness Rule**:
- Preset `name` must be unique within `ApplicationSettings.scale_presets` list
- Attempting to save duplicate name triggers confirmation dialog (FR-018)

**Validation Rules**:
```python
@dataclass
class ScalePreset:
    name: str
    scale_um_per_pixel: float
    created_date: datetime
    objective_ref: str = ""

    def validate(self) -> bool:
        """Validate preset constraints."""
        if not self.name or len(self.name.strip()) == 0:
            return False
        if self.scale_um_per_pixel <= 0:
            return False
        if self.created_date > datetime.now():
            return False
        return True

    def to_dict(self) -> dict:
        """Serialize for JSON storage."""
        return {
            "name": self.name,
            "scale_um_per_pixel": self.scale_um_per_pixel,
            "created_date": self.created_date.isoformat(),
            "objective_ref": self.objective_ref
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScalePreset':
        """Deserialize from JSON."""
        return cls(
            name=data["name"],
            scale_um_per_pixel=data["scale_um_per_pixel"],
            created_date=datetime.fromisoformat(data["created_date"]),
            objective_ref=data.get("objective_ref", "")
        )
```

---

### 3. DetectionResult

**Purpose**: Outcome of processing a single image (coverage analysis result).

**Attributes**:

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| `image_ref` | Image | Yes | Reference to source image | Must be valid Image instance |
| `coverage_percentage` | float | Yes | Coverage as percentage (0-100) | 0 ≤ value ≤ 100 |
| `area_um2` | float | No | Absolute area in µm² (if calibrated) | ≥ 0, 0 if no calibration |
| `threshold_value` | int | Yes | Threshold used (0-255 or "auto") | 0 ≤ value ≤ 255 or None for Otsu |
| `roi_coords` | tuple[int,int,int,int] | No | ROI (x, y, width, height) if applied | All ≥ 0, or None |
| `film_pixel_count` | int | Yes | Number of pixels classified as film | ≥ 0 |
| `total_pixel_count` | int | Yes | Total pixels in analyzed region | > 0 |
| `processing_timestamp` | datetime | Yes | When processing completed | ISO format |

**Derived Calculation**:
```python
coverage_percentage = (film_pixel_count / total_pixel_count) * 100

if scale_um_per_pixel and scale_um_per_pixel > 0:
    area_um2 = total_pixel_count * (scale_um_per_pixel ** 2) * (coverage_percentage / 100)
else:
    area_um2 = 0.0
```

**Validation Rules**:
```python
@dataclass
class DetectionResult:
    image_ref: Image
    coverage_percentage: float
    area_um2: float
    threshold_value: Optional[int]
    roi_coords: Optional[tuple[int, int, int, int]]
    film_pixel_count: int
    total_pixel_count: int
    processing_timestamp: datetime

    def validate(self) -> bool:
        """Validate result constraints."""
        if not (0 <= self.coverage_percentage <= 100):
            return False
        if self.area_um2 < 0:
            return False
        if self.threshold_value is not None and not (0 <= self.threshold_value <= 255):
            return False
        if self.film_pixel_count < 0 or self.total_pixel_count <= 0:
            return False
        if self.film_pixel_count > self.total_pixel_count:
            return False
        if self.roi_coords:
            x, y, w, h = self.roi_coords
            if x < 0 or y < 0 or w <= 0 or h <= 0:
                return False
        return True
```

---

### 4. BatchSession

**Purpose**: Collection of images processed together with shared settings.

**Attributes**:

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| `image_refs` | list[Image] | Yes | List of images in this batch | 1 ≤ len ≤ 100 (FR-004) |
| `scale_calibration` | float | No | Shared scale (µm/pixel) or None | > 0 if present |
| `threshold_setting` | int | Yes | Shared threshold value | 0 ≤ value ≤ 255 or None |
| `roi_settings` | tuple[int,int,int,int] | No | Shared ROI or None | Valid ROI coords or None |
| `summary_stats` | BatchStatistics | No | Calculated stats (after processing) | See BatchStatistics below |

**BatchStatistics**:
```python
@dataclass
class BatchStatistics:
    """Summary statistics for a batch session (FR-030, FR-032)."""
    mean_coverage: float      # Mean coverage percentage
    std_dev_coverage: float   # Standard deviation
    min_coverage: float       # Minimum coverage
    max_coverage: float       # Maximum coverage
    mean_area_um2: float      # Mean area (0 if not calibrated)
    std_dev_area_um2: float   # Std dev area (0 if not calibrated)

    @classmethod
    def calculate(cls, results: list[DetectionResult]) -> 'BatchStatistics':
        """Calculate statistics from detection results."""
        if not results:
            return cls(0, 0, 0, 0, 0, 0)

        coverages = [r.coverage_percentage for r in results]
        areas = [r.area_um2 for r in results]

        return cls(
            mean_coverage=np.mean(coverages),
            std_dev_coverage=np.std(coverages),
            min_coverage=np.min(coverages),
            max_coverage=np.max(coverages),
            mean_area_um2=np.mean(areas),
            std_dev_area_um2=np.std(areas)
        )
```

**Lifecycle**:
- Created: When user loads multiple images or starts batch processing
- Updated: As individual images are processed
- Cleared: When user clicks "New Session" (FR-048)

---

### 5. ApplicationSettings

**Purpose**: Persisted user preferences and configuration (stored in user AppData).

**Attributes**:

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| `scale_presets` | list[ScalePreset] | Yes | Saved scale calibrations | Can be empty list |
| `last_threshold` | int | Yes | Last-used threshold value | 0 ≤ value ≤ 255 |
| `overlay_transparency` | float | Yes | Last-used overlay opacity | 0.0 ≤ value ≤ 1.0 |
| `noise_reduction_enabled` | bool | Yes | Noise reduction toggle state | True or False |
| `window_geometry` | dict | No | Window size/position | {x, y, width, height} or None |
| `backup_timestamp` | datetime | No | When backup was last created | ISO format |

**Persistence**:
- **Location**: `%APPDATA%/ThinFilmAnalyzer/settings.json` (Windows) or `~/.config/ThinFilmAnalyzer/settings.json` (macOS)
- **Backup**: `settings.json.bak` created on each save (FR-034)
- **Recovery**: Load from backup if primary file corrupted (FR-036)

**JSON Structure**:
```json
{
  "scale_presets": [
    {
      "name": "10x objective",
      "scale_um_per_pixel": 0.65,
      "created_date": "2025-12-07T10:30:00",
      "objective_ref": "10x"
    }
  ],
  "last_threshold": 128,
  "overlay_transparency": 0.5,
  "noise_reduction_enabled": true,
  "window_geometry": {
    "x": 100,
    "y": 100,
    "width": 1200,
    "height": 800
  },
  "backup_timestamp": "2025-12-07T14:45:23"
}
```

**Default Values** (when no settings file exists):
```python
DEFAULT_SETTINGS = {
    "scale_presets": [],
    "last_threshold": 128,
    "overlay_transparency": 0.5,
    "noise_reduction_enabled": True,
    "window_geometry": None,
    "backup_timestamp": None
}
```

---

### 6. ErrorLog

**Purpose**: Diagnostic information for troubleshooting (not persisted in memory, written to file).

**Attributes**:

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| `error_timestamp` | datetime | Yes | When error occurred | ISO format with milliseconds |
| `error_type` | str | Yes | Error category (e.g., "ImageLoadError") | Non-empty string |
| `error_message` | str | Yes | Human-readable error description | Non-empty string |
| `context_info` | dict | No | Current operation, file being processed | Can be empty dict |
| `stack_trace` | str | No | Full stack trace for debugging | Can be empty |
| `rotation_status` | str | No | Log rotation info (e.g., "rotated at 10MB") | Can be empty |

**File Format** (written by Python logging module):
```
2025-12-07 14:30:15,123 - ERROR - processor.py:45 - Unable to load image: sample_broken.png. File may be corrupted. | Context: {'operation': 'batch_processing', 'image_index': 3}
Traceback (most recent call last):
  File "processor.py", line 42, in process_image
    img = cv2.imread(path)
cv2.error: OpenCV(4.8.0) error: (-215:Assertion failed) !_src.empty()
```

**Rotation Policy** (FR-043):
- Max file size: 10 MB
- Keep last 2 backups: `error.log`, `error.log.1`, `error.log.2`
- Oldest backup automatically deleted when new rotation occurs

---

## Relationships

### One-to-Many

1. **ApplicationSettings → ScalePreset**: One settings object contains many presets
   - Constraint: Preset names must be unique within settings
   - Deletion: Deleting a preset does not affect other presets

2. **BatchSession → Image**: One session contains many images (1-100)
   - Constraint: Maximum 100 images per batch (FR-004)
   - Deletion: Clearing session removes all image references

3. **BatchSession → DetectionResult**: One session produces many results
   - Constraint: One result per image
   - Deletion: Clearing session removes all results

### One-to-One

1. **Image → DetectionResult**: One image has at most one result
   - Created: After successful processing
   - Deleted: When session is cleared or image is removed

2. **BatchSession → BatchStatistics**: One session has one set of summary stats
   - Calculated: After all images in batch are processed
   - Updated: When new images are added/processed

---

## Validation Rules Summary

### Cross-Entity Validation

1. **Preset Name Uniqueness** (FR-018):
   ```python
   def is_preset_name_unique(name: str, existing_presets: list[ScalePreset]) -> bool:
       return not any(p.name == name for p in existing_presets)
   ```

2. **Batch Size Constraint** (FR-004):
   ```python
   def validate_batch_size(images: list[Image]) -> bool:
       return 1 <= len(images) <= 100
   ```

3. **Coverage Calculation Consistency**:
   ```python
   def validate_coverage_calculation(result: DetectionResult) -> bool:
       calculated = (result.film_pixel_count / result.total_pixel_count) * 100
       return abs(calculated - result.coverage_percentage) < 0.01  # Allow small float error
   ```

4. **ROI Bounds Check**:
   ```python
   def validate_roi_bounds(roi: tuple[int,int,int,int], image_dims: tuple[int,int]) -> bool:
       x, y, w, h = roi
       img_w, img_h = image_dims
       return (x >= 0 and y >= 0 and
               x + w <= img_w and y + h <= img_h)
   ```

---

## State Transition Matrix

### Image Status Transitions

| From State | Event | To State | Validation |
|------------|-------|----------|------------|
| UNPROCESSED | User clicks "Process" | PROCESSING | Image file must exist |
| PROCESSING | Processing completes | COMPLETE | Result must be valid |
| PROCESSING | Error occurs | ERROR | Error logged |
| COMPLETE | User adjusts threshold | PROCESSING | Reprocessing allowed |
| ERROR | User retries | PROCESSING | Retry allowed |
| Any State | User clicks "New Session" | Deleted | Session cleared |

### Session Lifecycle

| State | Description | Allowed Operations |
|-------|-------------|-------------------|
| Empty | No images loaded | Load images, exit |
| Loaded | Images loaded, not processed | Process, clear, load more |
| Processing | Batch processing in progress | Cancel, view progress |
| Complete | All images processed | Export CSV, export images, new session |

---

## Data Persistence Strategy

### What Gets Persisted

| Data | Storage Location | Format | Backup |
|------|-----------------|--------|--------|
| Application Settings | `%APPDATA%/ThinFilmAnalyzer/settings.json` | JSON | `.bak` file |
| Scale Presets | Embedded in settings.json | JSON array | Same as settings |
| Error Logs | `%APPDATA%/ThinFilmAnalyzer/error.log` | Plain text | Rotated backups |

### What Does NOT Get Persisted

| Data | Reason | Lifecycle |
|------|--------|-----------|
| Loaded Images | Session-specific, cleared on "New Session" | In-memory only |
| Detection Results | Session-specific, user exports to CSV | In-memory until exported |
| Batch Session | Transient, recreated each session | In-memory only |
| Window state (beyond geometry) | Unnecessary complexity | Recreated on startup |

---

## Performance Considerations

### Memory Footprint Estimates

| Entity | Count | Per-Instance Memory | Total |
|--------|-------|---------------------|-------|
| Image (metadata only) | 100 | ~1 KB | ~100 KB |
| Image (loaded pixel data) | 50 (active batch) | ~16 MB (2048×2048×3 bytes) | ~800 MB |
| DetectionResult | 100 | ~1 KB | ~100 KB |
| ScalePreset | 10 | ~0.5 KB | ~5 KB |

**Total for 50-image batch**: ~900 MB (within <2 GB constraint per SC-008)

### Optimization Strategies

1. **Lazy Loading**: Don't load full pixel data until processing (thumbnails use downsampled versions)
2. **Cleanup**: Clear processed image pixel data after result generated (keep metadata only)
3. **NumPy Array Reuse**: Reuse arrays for batch processing instead of allocating new ones

---

**Data Model Status**: ✅ Complete
**Next Phase**: Generate quickstart.md and module contracts
