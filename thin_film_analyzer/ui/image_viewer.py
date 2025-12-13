"""
Image viewer widget with overlay rendering support.
"""

from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import numpy as np


class ImageViewer(QLabel):
    """
    Custom image viewer widget for displaying images with overlay.
    """
    image_clicked = pyqtSignal(int, int)  # Emit (x, y) coordinates when clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("QLabel { background-color: #2b2b2b; }")
        self.setText("Drag and drop an image here or use File > Open")

        self.current_image = None
        self.original_image = None
        self.overlay_image = None
        self.show_overlay = False

    def display_image(self, image: np.ndarray, is_original: bool = False):
        """
        Display an image in the viewer.

        Args:
            image: Image as numpy array (BGR format from OpenCV)
            is_original: If True, store as original image reference (only on first load)
        """
        if image is None:
            return

        # Only store original image if explicitly marked as original
        if is_original:
            self.original_image = image.copy()

        self.current_image = image

        # Convert BGR to RGB for Qt
        if len(image.shape) == 3:
            rgb_image = image[:, :, ::-1]  # BGR to RGB
        else:
            rgb_image = image

        # Convert to QImage
        height, width = rgb_image.shape[:2]
        if len(rgb_image.shape) == 3:
            bytes_per_line = 3 * width
            q_image = QImage(
                rgb_image.data.tobytes(),
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888
            )
        else:
            bytes_per_line = width
            q_image = QImage(
                rgb_image.data.tobytes(),
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_Grayscale8
            )

        # Create pixmap and scale to fit widget
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

    def set_overlay_image(self, overlay_image: np.ndarray):
        """
        Set the overlay image (processed with overlay applied).

        Args:
            overlay_image: Image with overlay as numpy array
        """
        self.overlay_image = overlay_image

    def toggle_overlay(self, show: bool):
        """
        Toggle overlay visibility.

        Args:
            show: If True, show overlay; if False, show original
        """
        self.show_overlay = show

        if show and self.overlay_image is not None:
            self.display_image(self.overlay_image)
        elif self.original_image is not None:
            self.display_image(self.original_image)

    def clear_image(self):
        """Clear the displayed image."""
        self.clear()
        self.setText("Drag and drop an image here or use File > Open")
        self.current_image = None
        self.original_image = None
        self.overlay_image = None
        self.show_overlay = False

    def mousePressEvent(self, event):
        """Handle mouse click events."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Get click coordinates
            pos = event.pos()
            self.image_clicked.emit(pos.x(), pos.y())
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        """Handle widget resize to rescale image."""
        super().resizeEvent(event)
        if self.current_image is not None:
            self.display_image(self.current_image)
