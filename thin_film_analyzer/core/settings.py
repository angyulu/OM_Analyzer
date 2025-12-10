"""
Settings persistence manager with atomic save, backup, and recovery.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from ..models.app_settings import ApplicationSettings
from ..config.defaults import get_settings_dir, SETTINGS_FILE, SETTINGS_BACKUP_FILE


class SettingsManager:
    """
    Manages application settings persistence with atomic writes and automatic backup.
    """

    def __init__(self, settings_dir: Optional[Path] = None):
        """
        Initialize settings manager.

        Args:
            settings_dir: Directory for settings storage (uses default if None)
        """
        self.settings_dir = settings_dir or get_settings_dir()
        self.settings_path = self.settings_dir / SETTINGS_FILE
        self.backup_path = self.settings_dir / SETTINGS_BACKUP_FILE

    def load_settings(self) -> ApplicationSettings:
        """
        Load settings from file with automatic backup recovery.

        Returns:
            ApplicationSettings object (defaults if file doesn't exist or is corrupted)
        """
        # Try to load primary settings file
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return ApplicationSettings.from_dict(data)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Settings file corrupted: {e}")
                # Attempt backup recovery
                return self._recover_from_backup()
        else:
            # No settings file exists, return defaults
            return ApplicationSettings()

    def _recover_from_backup(self) -> ApplicationSettings:
        """
        Attempt to recover settings from backup file.

        Returns:
            ApplicationSettings from backup, or defaults if backup also fails
        """
        if self.backup_path.exists():
            try:
                with open(self.backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print("Settings recovered from backup")
                return ApplicationSettings.from_dict(data)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Backup file also corrupted: {e}, using defaults")

        return ApplicationSettings()

    def save_settings(self, settings: ApplicationSettings) -> None:
        """
        Save settings to file with automatic backup.

        Uses atomic write pattern:
        1. Create backup of current settings
        2. Write to temporary file
        3. Atomic rename to final location

        Args:
            settings: ApplicationSettings object to save
        """
        # Update backup timestamp
        settings.backup_timestamp = datetime.now()

        # Create backup of current settings file
        if self.settings_path.exists():
            try:
                shutil.copy2(self.settings_path, self.backup_path)
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")

        # Write to temporary file first (atomic operation)
        temp_path = self.settings_path.with_suffix('.tmp')
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)

            # Atomic rename (overwrites existing file)
            temp_path.replace(self.settings_path)

        except Exception as e:
            # Clean up temp file if write failed
            if temp_path.exists():
                temp_path.unlink()
            raise IOError(f"Failed to save settings: {e}") from e

    def settings_exist(self) -> bool:
        """Check if settings file exists."""
        return self.settings_path.exists()

    def backup_exists(self) -> bool:
        """Check if backup file exists."""
        return self.backup_path.exists()
