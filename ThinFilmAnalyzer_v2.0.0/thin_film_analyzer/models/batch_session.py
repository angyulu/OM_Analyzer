"""
BatchSession entity for managing collections of images processed together.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from .image import Image


@dataclass
class BatchStatistics:
    """Summary statistics for a batch of results."""
    mean_coverage: float
    std_dev_coverage: float
    min_coverage: float
    max_coverage: float
    mean_area: Optional[float] = None
    std_dev_area: Optional[float] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None

    @classmethod
    def calculate(cls, results: List['DetectionResult']) -> 'BatchStatistics':
        """
        Calculate summary statistics from a list of detection results.

        Args:
            results: List of DetectionResult objects

        Returns:
            BatchStatistics object with calculated values
        """
        if not results:
            raise ValueError("Cannot calculate statistics for empty results list")

        import numpy as np

        coverages = [r.coverage_percentage for r in results]
        areas = [r.area_um2 for r in results if r.area_um2 > 0]

        stats = cls(
            mean_coverage=float(np.mean(coverages)),
            std_dev_coverage=float(np.std(coverages)),
            min_coverage=float(np.min(coverages)),
            max_coverage=float(np.max(coverages))
        )

        if areas:
            stats.mean_area = float(np.mean(areas))
            stats.std_dev_area = float(np.std(areas))
            stats.min_area = float(np.min(areas))
            stats.max_area = float(np.max(areas))

        return stats

    def to_dict(self) -> dict:
        """Convert statistics to dictionary for export."""
        result = {
            "mean_coverage": round(self.mean_coverage, 2),
            "std_dev_coverage": round(self.std_dev_coverage, 2),
            "min_coverage": round(self.min_coverage, 2),
            "max_coverage": round(self.max_coverage, 2)
        }

        if self.mean_area is not None:
            result.update({
                "mean_area_um2": round(self.mean_area, 2),
                "std_dev_area_um2": round(self.std_dev_area, 2),
                "min_area_um2": round(self.min_area, 2),
                "max_area_um2": round(self.max_area, 2)
            })

        return result


@dataclass
class BatchSession:
    """
    Represents a collection of images processed together with shared settings.

    Attributes:
        image_refs: List of Image objects to process
        scale_calibration: Scale value in µm/pixel (None if uncalibrated)
        threshold_setting: Threshold value to use for all images
        roi_settings: ROI coordinates if applied to all images
        summary_stats: Summary statistics after processing (calculated)
    """
    image_refs: List[Image]
    scale_calibration: Optional[float] = None
    threshold_setting: int = 128
    roi_settings: Optional[Tuple[int, int, int, int]] = None
    summary_stats: Optional[BatchStatistics] = None

    def __post_init__(self):
        """Validate batch session data."""
        if not self.image_refs:
            raise ValueError("Batch session must contain at least one image")

        if len(self.image_refs) > 100:
            raise ValueError(f"Batch size exceeds maximum of 100 images, got {len(self.image_refs)}")

        if not (0 <= self.threshold_setting <= 255):
            raise ValueError(f"Threshold must be 0-255, got {self.threshold_setting}")

        if self.scale_calibration is not None and self.scale_calibration <= 0:
            raise ValueError(f"Scale calibration must be positive, got {self.scale_calibration}")

    @property
    def image_count(self) -> int:
        """Get number of images in the batch."""
        return len(self.image_refs)

    @property
    def is_calibrated(self) -> bool:
        """Check if batch has scale calibration."""
        return self.scale_calibration is not None
