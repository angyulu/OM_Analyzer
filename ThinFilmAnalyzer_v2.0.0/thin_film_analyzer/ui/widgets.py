"""
Custom UI widgets for the Thin Film Analyzer application.
"""

from PyQt6.QtWidgets import (
    QWidget, QSlider, QLabel, QVBoxLayout, QHBoxLayout,
    QListWidget, QProgressBar, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from pathlib import Path


class ThresholdSlider(QWidget):
    """
    Custom threshold slider widget with label showing current value.
    """
    value_changed = pyqtSignal(int)  # Emit new threshold value

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        self.label = QLabel("Threshold: 128")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 255)
        self.slider.setValue(128)
        self.slider.setToolTip("Adjust threshold sensitivity for thin film detection")
        self.slider.valueChanged.connect(self._on_value_changed)

        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def _on_value_changed(self, value: int):
        """Handle slider value change."""
        self.label.setText(f"Threshold: {value}")
        self.value_changed.emit(value)

    def get_value(self) -> int:
        """Get current threshold value."""
        return self.slider.value()

    def set_value(self, value: int):
        """Set threshold value."""
        self.slider.setValue(value)


class TransparencySlider(QWidget):
    """
    Custom transparency slider widget for overlay opacity control.
    """
    value_changed = pyqtSignal(float)  # Emit new opacity value (0.0-1.0)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        self.label = QLabel("Overlay Transparency: 50%")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.setToolTip("Adjust overlay transparency")
        self.slider.valueChanged.connect(self._on_value_changed)

        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def _on_value_changed(self, value: int):
        """Handle slider value change."""
        self.label.setText(f"Overlay Transparency: {value}%")
        opacity = value / 100.0
        self.value_changed.emit(opacity)

    def get_opacity(self) -> float:
        """Get current opacity value (0.0-1.0)."""
        return self.slider.value() / 100.0

    def set_opacity(self, opacity: float):
        """Set opacity value (0.0-1.0)."""
        value = int(opacity * 100)
        self.slider.setValue(value)


class ThumbnailPanel(QListWidget):
    """
    Thumbnail panel widget showing loaded image thumbnails.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setIconSize(Qt.QSize(150, 150))
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setSpacing(10)
        self.setToolTip("Loaded images - click to select")

    def add_thumbnail(self, image_path: Path, filename: str):
        """
        Add a thumbnail to the panel.

        Args:
            image_path: Path to the image file
            filename: Display name for the thumbnail
        """
        item = QListWidgetItem(filename)

        # Create thumbnail pixmap
        pixmap = QPixmap(str(image_path))
        if not pixmap.isNull():
            # Scale to thumbnail size while maintaining aspect ratio
            pixmap = pixmap.scaled(
                150, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            item.setIcon(QIcon(pixmap))

        self.addItem(item)

    def clear_thumbnails(self):
        """Remove all thumbnails from the panel."""
        self.clear()


class BatchProgressBar(QWidget):
    """
    Progress bar widget for batch processing with status label.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        self.label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def set_progress(self, current: int, total: int):
        """
        Update progress bar.

        Args:
            current: Current image number (1-indexed)
            total: Total number of images
        """
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.label.setText(f"Processing image {current} of {total}")
        else:
            self.reset()

    def reset(self):
        """Reset progress bar to initial state."""
        self.progress_bar.setValue(0)
        self.label.setText("Ready")

    def set_complete(self):
        """Set progress bar to complete state."""
        self.progress_bar.setValue(100)
        self.label.setText("Processing complete")
