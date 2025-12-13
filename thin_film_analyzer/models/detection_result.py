"""
DetectionResult entity representing the outcome of processing an image.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from .image import Image


@dataclass
class DetectionResult:
    """
    Represents the outcome of processing one image.

    Attributes:
        image_ref: Reference to the source Image
        coverage_percentage: Percentage of image covered by thin film
        area_um2: Absolute area in square micrometers (if calibrated, else 0.0)
        threshold_value: Threshold value used for detection
        roi_coords: ROI coordinates if applied (x, y, width, height), None otherwise
        film_pixel_count: Number of pixels detected as thin film
        total_pixel_count: Total pixels in analyzed region
        processing_timestamp: When the processing completed
        mono_coverage: Monolayer coverage percentage (v2.1.0+, None if layer detection not used)
        bi_coverage: Bilayer coverage percentage (v2.1.0+, None if layer detection not used)
        tri_coverage: Trilayer coverage percentage (v2.1.0+, None if layer detection not used)
        thresholds: Layer classification thresholds (T1, T2) (v2.1.0+, None if layer detection not used)
    """
    image_ref: Image
    coverage_percentage: float
    area_um2: float
    threshold_value: int
    roi_coords: Optional[Tuple[int, int, int, int]]  # (x, y, width, height)
    film_pixel_count: int
    total_pixel_count: int
    processing_timestamp: datetime
    # v2.1.0 layer detection fields
    mono_coverage: Optional[float] = None
    bi_coverage: Optional[float] = None
    tri_coverage: Optional[float] = None
    thresholds: Optional[Tuple[int, int]] = None  # (T1, T2)

    def __post_init__(self):
        """Validate result data after initialization."""
        if not (0.0 <= self.coverage_percentage <= 100.0):
            raise ValueError(f"Coverage percentage must be 0-100, got {self.coverage_percentage}")

        if self.area_um2 < 0.0:
            raise ValueError(f"Area cannot be negative, got {self.area_um2}")

        if not (0 <= self.threshold_value <= 255):
            raise ValueError(f"Threshold must be 0-255, got {self.threshold_value}")

        if self.film_pixel_count < 0 or self.total_pixel_count <= 0:
            raise ValueError("Invalid pixel counts")

        if self.film_pixel_count > self.total_pixel_count:
            raise ValueError("Film pixels cannot exceed total pixels")

        # Validate layer coverage fields (v2.1.0+)
        if self.mono_coverage is not None:
            if not (0.0 <= self.mono_coverage <= 100.0):
                raise ValueError(f"Monolayer coverage must be 0-100, got {self.mono_coverage}")

        if self.bi_coverage is not None:
            if not (0.0 <= self.bi_coverage <= 100.0):
                raise ValueError(f"Bilayer coverage must be 0-100, got {self.bi_coverage}")

        if self.tri_coverage is not None:
            if not (0.0 <= self.tri_coverage <= 100.0):
                raise ValueError(f"Trilayer coverage must be 0-100, got {self.tri_coverage}")

        # Validate thresholds if present
        if self.thresholds is not None:
            if len(self.thresholds) != 2:
                raise ValueError(f"Thresholds must be tuple of 2 values (T1, T2), got {len(self.thresholds)}")
            t1, t2 = self.thresholds
            if not (0 <= t1 <= 255 and 0 <= t2 <= 255):
                raise ValueError(f"Thresholds must be 0-255, got T1={t1}, T2={t2}")
            if t1 >= t2:
                raise ValueError(f"T1 must be < T2, got T1={t1}, T2={t2}")

    def to_dict(self) -> dict:
        """Convert result to dictionary for export."""
        result = {
            "filename": self.image_ref.filename,
            "coverage_percentage": round(self.coverage_percentage, 2),
            "area_um2": round(self.area_um2, 2) if self.area_um2 > 0 else None,
            "threshold_value": self.threshold_value,
            "roi_applied": self.roi_coords is not None,
            "film_pixel_count": self.film_pixel_count,
            "total_pixel_count": self.total_pixel_count,
            "processing_timestamp": self.processing_timestamp.isoformat()
        }

        # Add layer detection fields if available (v2.1.0+)
        if self.mono_coverage is not None:
            result["mono_coverage"] = round(self.mono_coverage, 2)
        if self.bi_coverage is not None:
            result["bi_coverage"] = round(self.bi_coverage, 2)
        if self.tri_coverage is not None:
            result["tri_coverage"] = round(self.tri_coverage, 2)
        if self.thresholds is not None:
            result["t1"] = self.thresholds[0]
            result["t2"] = self.thresholds[1]

        return result
