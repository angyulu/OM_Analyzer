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
    """
    image_ref: Image
    coverage_percentage: float
    area_um2: float
    threshold_value: int
    roi_coords: Optional[Tuple[int, int, int, int]]  # (x, y, width, height)
    film_pixel_count: int
    total_pixel_count: int
    processing_timestamp: datetime

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

    def to_dict(self) -> dict:
        """Convert result to dictionary for export."""
        return {
            "filename": self.image_ref.filename,
            "coverage_percentage": round(self.coverage_percentage, 2),
            "area_um2": round(self.area_um2, 2) if self.area_um2 > 0 else None,
            "threshold_value": self.threshold_value,
            "roi_applied": self.roi_coords is not None,
            "film_pixel_count": self.film_pixel_count,
            "total_pixel_count": self.total_pixel_count,
            "processing_timestamp": self.processing_timestamp.isoformat()
        }
