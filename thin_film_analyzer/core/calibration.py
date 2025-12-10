"""
Scale calibration management with preset save/load functionality.
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from ..models.scale_preset import ScalePreset
from ..config.defaults import get_settings_dir, PRESETS_FILE


class CalibrationManager:
    """
    Manages scale calibration presets with save/load/delete operations.
    """

    def __init__(self, settings_dir: Optional[Path] = None):
        """
        Initialize calibration manager.

        Args:
            settings_dir: Directory for preset storage (uses default if None)
        """
        self.settings_dir = settings_dir or get_settings_dir()
        self.presets_path = self.settings_dir / PRESETS_FILE
        self.presets: List[ScalePreset] = []
        self._load_presets()

    def _load_presets(self) -> None:
        """Load presets from file."""
        if self.presets_path.exists():
            try:
                with open(self.presets_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.presets = [ScalePreset.from_dict(p) for p in data.get("presets", [])]
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Error loading presets: {e}, starting with empty preset list")
                self.presets = []
        else:
            self.presets = []

    def _save_presets(self) -> None:
        """Save presets to file."""
        data = {
            "presets": [p.to_dict() for p in self.presets]
        }

        # Create directory if it doesn't exist
        self.settings_dir.mkdir(parents=True, exist_ok=True)

        with open(self.presets_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_preset(self, preset: ScalePreset, overwrite: bool = False) -> None:
        """
        Save a scale calibration preset.

        Args:
            preset: ScalePreset object to save
            overwrite: If True, overwrite existing preset with same name

        Raises:
            ValueError: If preset with same name exists and overwrite=False
        """
        existing_idx = self._find_preset_index(preset.name)

        if existing_idx is not None:
            if not overwrite:
                raise ValueError(f"Preset '{preset.name}' already exists")
            # Replace existing preset
            self.presets[existing_idx] = preset
        else:
            # Add new preset
            self.presets.append(preset)

        self._save_presets()

    def load_preset(self, preset_name: str) -> Optional[ScalePreset]:
        """
        Load a scale preset by name.

        Args:
            preset_name: Name of the preset to load

        Returns:
            ScalePreset object if found, None otherwise
        """
        for preset in self.presets:
            if preset.name == preset_name:
                return preset
        return None

    def delete_preset(self, preset_name: str) -> bool:
        """
        Delete a scale preset by name.

        Args:
            preset_name: Name of the preset to delete

        Returns:
            True if preset was found and deleted, False otherwise
        """
        idx = self._find_preset_index(preset_name)
        if idx is not None:
            del self.presets[idx]
            self._save_presets()
            return True
        return False

    def list_presets(self) -> List[str]:
        """
        Get list of all preset names.

        Returns:
            List of preset names
        """
        return [p.name for p in self.presets]

    def preset_exists(self, preset_name: str) -> bool:
        """
        Check if a preset with the given name exists.

        Args:
            preset_name: Name to check

        Returns:
            True if preset exists, False otherwise
        """
        return self._find_preset_index(preset_name) is not None

    def _find_preset_index(self, preset_name: str) -> Optional[int]:
        """Find index of preset by name."""
        for i, preset in enumerate(self.presets):
            if preset.name == preset_name:
                return i
        return None

    def calculate_scale_from_line(
        self,
        line_length_pixels: float,
        known_length_um: float
    ) -> float:
        """
        Calculate scale calibration from a drawn line.

        Args:
            line_length_pixels: Length of line drawn on image (in pixels)
            known_length_um: Known length of the feature (in micrometers)

        Returns:
            Scale value in µm/pixel
        """
        if line_length_pixels <= 0:
            raise ValueError("Line length must be positive")
        if known_length_um <= 0:
            raise ValueError("Known length must be positive")

        return known_length_um / line_length_pixels
