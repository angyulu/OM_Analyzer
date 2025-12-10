"""
ScalePreset entity for saved calibration configurations.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ScalePreset:
    """
    Represents a saved scale calibration configuration.

    Attributes:
        name: Preset name (e.g., "10x objective")
        scale_um_per_pixel: Scale value in micrometers per pixel
        created_date: When the preset was created
        objective_ref: Reference to microscope objective (e.g., "10x", "40x")
    """
    name: str
    scale_um_per_pixel: float
    created_date: datetime
    objective_ref: Optional[str] = None

    def __post_init__(self):
        """Validate preset data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Preset name cannot be empty")

        if self.scale_um_per_pixel <= 0:
            raise ValueError(f"Scale must be positive, got {self.scale_um_per_pixel}")

        if not isinstance(self.created_date, datetime):
            raise TypeError(f"created_date must be datetime, got {type(self.created_date)}")

    def to_dict(self) -> dict:
        """Convert preset to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "scale_um_per_pixel": self.scale_um_per_pixel,
            "created_date": self.created_date.isoformat(),
            "objective_ref": self.objective_ref
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScalePreset':
        """Create preset from dictionary (JSON deserialization)."""
        return cls(
            name=data["name"],
            scale_um_per_pixel=data["scale_um_per_pixel"],
            created_date=datetime.fromisoformat(data["created_date"]),
            objective_ref=data.get("objective_ref")
        )
