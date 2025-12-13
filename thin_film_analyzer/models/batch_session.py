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
        thresholds_locked: Whether T1/T2 thresholds are locked for batch (v2.1.0+)
        locked_t1: Locked T1 threshold value (v2.1.0+)
        locked_t2: Locked T2 threshold value (v2.1.0+)
    """
    image_refs: List[Image]
    scale_calibration: Optional[float] = None
    threshold_setting: int = 128
    roi_settings: Optional[Tuple[int, int, int, int]] = None
    summary_stats: Optional[BatchStatistics] = None
    # v2.1.0 layer detection threshold locking
    thresholds_locked: bool = False
    locked_t1: Optional[int] = None
    locked_t2: Optional[int] = None

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

    def lock_thresholds(self, t1: int, t2: int) -> None:
        """
        Lock T1 and T2 thresholds for batch processing.

        When locked, all images in the batch will use these threshold values
        for layer classification, ensuring consistency across the batch.

        Args:
            t1: Monolayer/bilayer boundary threshold (0-255)
            t2: Bilayer/trilayer boundary threshold (0-255)

        Raises:
            ValueError: If thresholds are invalid or t1 >= t2
        """
        if not (0 <= t1 <= 255 and 0 <= t2 <= 255):
            raise ValueError(f"Thresholds must be 0-255, got t1={t1}, t2={t2}")
        if t1 >= t2:
            raise ValueError(f"T1 must be < T2, got t1={t1}, t2={t2}")

        self.thresholds_locked = True
        self.locked_t1 = t1
        self.locked_t2 = t2

    def unlock_thresholds(self) -> None:
        """
        Unlock thresholds to allow manual adjustment per image.
        """
        self.thresholds_locked = False
        self.locked_t1 = None
        self.locked_t2 = None

    def are_thresholds_locked(self) -> bool:
        """
        Check if thresholds are currently locked.

        Returns:
            True if thresholds are locked, False otherwise
        """
        return self.thresholds_locked

    def get_locked_thresholds(self) -> Optional[Tuple[int, int]]:
        """
        Get locked threshold values if thresholds are locked.

        Returns:
            Tuple of (t1, t2) if locked, None otherwise
        """
        if self.thresholds_locked and self.locked_t1 is not None and self.locked_t2 is not None:
            return (self.locked_t1, self.locked_t2)
        return None
