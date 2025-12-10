"""
ApplicationSettings entity for persisted user preferences.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple
from .scale_preset import ScalePreset


@dataclass
class ApplicationSettings:
    """
    Represents persisted user preferences stored in user-specific application data directory.

    Attributes:
        scale_presets: List of saved scale calibration presets
        last_threshold: Last-used threshold value
        overlay_transparency: Last-used overlay opacity (0.0-1.0)
        noise_reduction_enabled: Whether noise reduction is enabled
        window_geometry: Window size and position (x, y, width, height)
        backup_timestamp: When the settings were last backed up
    """
    scale_presets: List[ScalePreset] = field(default_factory=list)
    last_threshold: int = 128
    overlay_transparency: float = 0.5
    noise_reduction_enabled: bool = True
    window_geometry: Optional[Tuple[int, int, int, int]] = None  # (x, y, width, height)
    backup_timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Validate settings data."""
        if not (0 <= self.last_threshold <= 255):
            raise ValueError(f"Threshold must be 0-255, got {self.last_threshold}")

        if not (0.0 <= self.overlay_transparency <= 1.0):
            raise ValueError(f"Transparency must be 0.0-1.0, got {self.overlay_transparency}")

    def to_dict(self) -> dict:
        """Convert settings to dictionary for JSON serialization."""
        return {
            "scale_presets": [preset.to_dict() for preset in self.scale_presets],
            "last_threshold": self.last_threshold,
            "overlay_transparency": self.overlay_transparency,
            "noise_reduction_enabled": self.noise_reduction_enabled,
            "window_geometry": self.window_geometry,
            "backup_timestamp": self.backup_timestamp.isoformat() if self.backup_timestamp else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ApplicationSettings':
        """Create settings from dictionary (JSON deserialization)."""
        presets = [ScalePreset.from_dict(p) for p in data.get("scale_presets", [])]

        backup_ts = data.get("backup_timestamp")
        if backup_ts:
            backup_ts = datetime.fromisoformat(backup_ts)

        return cls(
            scale_presets=presets,
            last_threshold=data.get("last_threshold", 128),
            overlay_transparency=data.get("overlay_transparency", 0.5),
            noise_reduction_enabled=data.get("noise_reduction_enabled", True),
            window_geometry=tuple(data["window_geometry"]) if data.get("window_geometry") else None,
            backup_timestamp=backup_ts
        )

    def add_preset(self, preset: ScalePreset) -> None:
        """Add a new scale preset to the settings."""
        self.scale_presets.append(preset)

    def remove_preset(self, preset_name: str) -> bool:
        """
        Remove a scale preset by name.

        Returns:
            True if preset was found and removed, False otherwise
        """
        original_len = len(self.scale_presets)
        self.scale_presets = [p for p in self.scale_presets if p.name != preset_name]
        return len(self.scale_presets) < original_len

    def get_preset(self, preset_name: str) -> Optional[ScalePreset]:
        """Get a scale preset by name."""
        for preset in self.scale_presets:
            if preset.name == preset_name:
                return preset
        return None

    def preset_exists(self, preset_name: str) -> bool:
        """Check if a preset with the given name exists."""
        return any(p.name == preset_name for p in self.scale_presets)
