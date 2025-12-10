"""
Main application window for the Thin Film Analyzer.
"""

import cv2
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCheckBox, QFileDialog, QLabel, QGroupBox, QMessageBox, QComboBox, QSlider, QSpinBox
)
from PyQt6.QtCore import Qt

from .image_viewer import ImageViewer
from .widgets import ThresholdSlider, TransparencySlider, ThumbnailPanel, BatchProgressBar
from .results_table import ResultsTable
from .dialogs import show_error_dialog, show_info_dialog

from ..models.image import Image, ImageStatus
from ..models.detection_result import DetectionResult
from ..core.processor import process_image, load_image_metadata, load_image_with_fallback
from ..core.overlay import generate_overlay
from ..core.settings import SettingsManager
from ..core.logger import get_logger
from ..core.detection import calculate_otsu_threshold, apply_noise_reduction
from ..config.defaults import SUPPORTED_IMAGE_FORMATS, DEFAULT_THRESHOLD, DEFAULT_OVERLAY_TRANSPARENCY
import cv2
import numpy as np


class MainWindow(QMainWindow):
    """
    Main application window with drag-drop, image processing, and results display.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thin Film Coverage Analyzer v1.0.0")
        self.resize(1200, 800)

        # Initialize managers
        self.settings_manager = SettingsManager()
        self.logger = get_logger()
        self.settings = self.settings_manager.load_settings()

        # State
        self.current_image: Optional[Image] = None
        self.current_result: Optional[DetectionResult] = None
        self.binary_mask: Optional = None
        self.original_cv_image: Optional = None

        # Batch processing state
        self.image_batch: List[str] = []  # List of image file paths
        self.current_image_index: int = 0  # Current image index in batch

        self._init_ui()
        self._load_settings()

        # Enable drag-drop
        self.setAcceptDrops(True)

    def _init_ui(self):
        """Initialize UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()

        # Left panel - Controls
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # Center - Image viewer
        center_panel = self._create_center_panel()
        main_layout.addWidget(center_panel, 3)

        central_widget.setLayout(main_layout)

        # Create menu bar
        self._create_menu_bar()

    def _create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        open_action = file_menu.addAction("Open Image...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image_dialog)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

    def _create_left_panel(self) -> QWidget:
        """Create left control panel."""
        panel = QWidget()
        layout = QVBoxLayout()

        # Processing controls
        process_group = QGroupBox("Processing")
        process_layout = QVBoxLayout()

        # Threshold method checkbox
        self.adaptive_threshold_checkbox = QCheckBox("Use Adaptive Threshold")
        self.adaptive_threshold_checkbox.setChecked(True)  # Default to ON
        self.adaptive_threshold_checkbox.setToolTip(
            "Use local adaptive thresholding for images with uneven illumination.\n"
            "Useful for detecting flakes in corners/edges or when vignetting is present."
        )
        self.adaptive_threshold_checkbox.toggled.connect(self.on_threshold_method_changed)
        process_layout.addWidget(self.adaptive_threshold_checkbox)

        # Threshold slider
        self.threshold_slider = ThresholdSlider()
        self.threshold_slider.value_changed.connect(self.on_threshold_changed)
        process_layout.addWidget(self.threshold_slider)

        # Noise reduction checkbox
        self.noise_reduction_checkbox = QCheckBox("Enable Noise Reduction")
        self.noise_reduction_checkbox.setChecked(True)
        self.noise_reduction_checkbox.setToolTip("Apply Gaussian blur before thresholding")
        self.noise_reduction_checkbox.toggled.connect(self.on_noise_reduction_changed)
        process_layout.addWidget(self.noise_reduction_checkbox)

        # Gaussian blur kernel size
        blur_layout = QHBoxLayout()
        blur_label = QLabel("Blur Kernel:")
        self.blur_kernel_spinbox = QSpinBox()
        self.blur_kernel_spinbox.setRange(1, 15)
        self.blur_kernel_spinbox.setSingleStep(2)
        self.blur_kernel_spinbox.setValue(3)
        self.blur_kernel_spinbox.setToolTip("Gaussian blur kernel size (odd numbers only)")
        self.blur_kernel_spinbox.valueChanged.connect(self.on_blur_kernel_changed)
        blur_layout.addWidget(blur_label)
        blur_layout.addWidget(self.blur_kernel_spinbox)
        process_layout.addLayout(blur_layout)

        # Morphological close kernel size
        morph_close_layout = QHBoxLayout()
        morph_close_label = QLabel("Morph Close:")
        self.morph_close_spinbox = QSpinBox()
        self.morph_close_spinbox.setRange(0, 10)
        self.morph_close_spinbox.setValue(2)
        self.morph_close_spinbox.setToolTip("Morphological close kernel size (0 = disabled)")
        self.morph_close_spinbox.valueChanged.connect(self.on_morph_close_changed)
        morph_close_layout.addWidget(morph_close_label)
        morph_close_layout.addWidget(self.morph_close_spinbox)
        process_layout.addLayout(morph_close_layout)

        # Morphological open kernel size
        morph_open_layout = QHBoxLayout()
        morph_open_label = QLabel("Morph Open:")
        self.morph_open_spinbox = QSpinBox()
        self.morph_open_spinbox.setRange(0, 10)
        self.morph_open_spinbox.setValue(2)
        self.morph_open_spinbox.setToolTip("Morphological open kernel size (0 = disabled)")
        self.morph_open_spinbox.valueChanged.connect(self.on_morph_open_changed)
        morph_open_layout.addWidget(morph_open_label)
        morph_open_layout.addWidget(self.morph_open_spinbox)
        process_layout.addLayout(morph_open_layout)

        # Adaptive threshold block size
        adaptive_block_layout = QHBoxLayout()
        adaptive_block_label = QLabel("Adaptive Block:")
        self.adaptive_block_spinbox = QSpinBox()
        self.adaptive_block_spinbox.setRange(3, 301)
        self.adaptive_block_spinbox.setSingleStep(2)
        self.adaptive_block_spinbox.setValue(200)  # Default block size for local background estimation
        self.adaptive_block_spinbox.setToolTip("Adaptive threshold block size (odd numbers only)")
        self.adaptive_block_spinbox.valueChanged.connect(self.on_adaptive_block_changed)
        adaptive_block_layout.addWidget(adaptive_block_label)
        adaptive_block_layout.addWidget(self.adaptive_block_spinbox)
        process_layout.addLayout(adaptive_block_layout)

        # Adaptive threshold C constant
        adaptive_c_layout = QHBoxLayout()
        adaptive_c_label = QLabel("Adaptive C:")
        self.adaptive_c_spinbox = QSpinBox()
        self.adaptive_c_spinbox.setRange(1, 50)
        self.adaptive_c_spinbox.setValue(5)  # Lower default for thin flake detection
        self.adaptive_c_spinbox.setToolTip(
            "Minimum brightness difference to detect flakes\n"
            "Lower = detect thinner flakes (more sensitive)\n"
            "Higher = only detect thicker flakes (less sensitive)"
        )
        self.adaptive_c_spinbox.valueChanged.connect(self.on_adaptive_c_changed)
        adaptive_c_layout.addWidget(adaptive_c_label)
        adaptive_c_layout.addWidget(self.adaptive_c_spinbox)
        process_layout.addLayout(adaptive_c_layout)

        process_group.setLayout(process_layout)
        layout.addWidget(process_group)

        # Overlay controls
        overlay_group = QGroupBox("Overlay")
        overlay_layout = QVBoxLayout()

        self.overlay_checkbox = QCheckBox("Show Overlay")
        self.overlay_checkbox.setChecked(True)  # Enable overlay by default
        self.overlay_checkbox.setToolTip("Toggle overlay visibility")
        self.overlay_checkbox.toggled.connect(self.on_overlay_toggled)
        overlay_layout.addWidget(self.overlay_checkbox)

        self.transparency_slider = TransparencySlider()
        self.transparency_slider.value_changed.connect(self.on_transparency_changed)
        overlay_layout.addWidget(self.transparency_slider)

        overlay_group.setLayout(overlay_layout)
        layout.addWidget(overlay_group)

        # Results display
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()

        self.coverage_label = QLabel("Coverage: --")
        self.coverage_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        results_layout.addWidget(self.coverage_label)

        self.area_label = QLabel("Area: --")
        results_layout.addWidget(self.area_label)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_center_panel(self) -> QWidget:
        """Create center image display panel."""
        panel = QWidget()
        layout = QVBoxLayout()

        # Image viewer
        self.image_viewer = ImageViewer()
        layout.addWidget(self.image_viewer)

        # Navigation panel for batch images
        nav_panel = self._create_navigation_panel()
        layout.addWidget(nav_panel)

        panel.setLayout(layout)
        return panel

    def _create_navigation_panel(self) -> QWidget:
        """Create navigation panel for batch image browsing."""
        panel = QWidget()
        layout = QHBoxLayout()

        # Previous button
        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.setEnabled(False)
        self.prev_button.clicked.connect(self.load_previous_image)
        layout.addWidget(self.prev_button)

        # Image dropdown selector
        self.image_selector = QComboBox()
        self.image_selector.setMinimumWidth(300)
        self.image_selector.currentIndexChanged.connect(self.on_image_selected)
        layout.addWidget(self.image_selector, 1)

        # Next button
        self.next_button = QPushButton("Next ▶")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.load_next_image)
        layout.addWidget(self.next_button)

        # Image counter label
        self.image_counter_label = QLabel("No images loaded")
        layout.addWidget(self.image_counter_label)

        panel.setLayout(layout)
        return panel

    def _load_settings(self):
        """Load saved settings and apply to UI."""
        self.threshold_slider.set_value(self.settings.last_threshold)
        self.transparency_slider.set_opacity(self.settings.overlay_transparency)
        self.noise_reduction_checkbox.setChecked(self.settings.noise_reduction_enabled)

        # Restore window geometry if available
        if self.settings.window_geometry:
            x, y, w, h = self.settings.window_geometry
            self.setGeometry(x, y, w, h)

    def _save_settings(self):
        """Save current settings."""
        self.settings.last_threshold = self.threshold_slider.get_value()
        self.settings.overlay_transparency = self.transparency_slider.get_opacity()
        self.settings.noise_reduction_enabled = self.noise_reduction_checkbox.isChecked()

        # Save window geometry
        geom = self.geometry()
        self.settings.window_geometry = (geom.x(), geom.y(), geom.width(), geom.height())

        try:
            self.settings_manager.save_settings(self.settings)
        except Exception as e:
            self.logger.log_error("SettingsSaveError", str(e))

    def open_image_dialog(self):
        """Open file dialog to select one or multiple images."""
        file_filter = "Images (" + " ".join([f"*{ext}" for ext in SUPPORTED_IMAGE_FORMATS]) + ")"
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open Image(s)",
            "",
            file_filter
        )

        if file_paths:
            if len(file_paths) == 1:
                self.load_image(file_paths[0])
            else:
                self.load_image_batch(file_paths)

    def load_image(self, file_path: str):
        """
        Load an image file.

        Args:
            file_path: Path to the image file
        """
        try:
            # Validate file format
            path = Path(file_path)
            if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
                show_error_dialog(
                    self,
                    "Unsupported Format",
                    f"File format {path.suffix} is not supported.\n"
                    f"Supported formats: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
                )
                return

            # Load image metadata
            dimensions, format_ext = load_image_metadata(file_path)

            # Create Image model
            self.current_image = Image(
                filename=path.name,
                file_path=path,
                dimensions=dimensions,
                format=format_ext,
                status=ImageStatus.UNPROCESSED
            )

            # Load and display image
            self.original_cv_image = load_image_with_fallback(file_path)
            self.image_viewer.display_image(self.original_cv_image)

            # Calculate optimal threshold using Otsu's method
            gray = cv2.cvtColor(self.original_cv_image, cv2.COLOR_BGR2GRAY)
            if self.noise_reduction_checkbox.isChecked():
                gray = apply_noise_reduction(gray, kernel_size=self.blur_kernel_spinbox.value())
            optimal_threshold = calculate_otsu_threshold(gray)
            self.threshold_slider.set_value(optimal_threshold)

            # Reset results
            self.coverage_label.setText("Coverage: --")
            self.area_label.setText("Area: --")
            self.current_result = None
            self.binary_mask = None

            print(f"Loaded image: {file_path} ({dimensions[0]}x{dimensions[1]})")
            print(f"Auto-calculated threshold: {optimal_threshold}")

            # Update navigation if this image is part of a batch
            if file_path in self.image_batch:
                self.current_image_index = self.image_batch.index(file_path)
                self.image_selector.blockSignals(True)
                self.image_selector.setCurrentIndex(self.current_image_index)
                self.image_selector.blockSignals(False)
            else:
                # Single image load - reset batch
                self.image_batch = [file_path]
                self.current_image_index = 0
                self.image_selector.blockSignals(True)
                self.image_selector.clear()
                self.image_selector.addItem(f"1. {path.name}", file_path)
                self.image_selector.blockSignals(False)

            self._update_navigation_buttons()

            # Auto-process the image
            self.process_current_image()

        except Exception as e:
            self.logger.log_error("ImageLoadError", str(e), context_info=file_path)
            show_error_dialog(
                self,
                "Error Loading Image",
                f"Unable to load image: {str(e)}"
            )

    def process_current_image(self):
        """Process the currently loaded image."""
        if self.current_image is None:
            return

        try:
            self.current_image.status = ImageStatus.PROCESSING

            # Get processing parameters
            threshold = self.threshold_slider.get_value()
            noise_reduction = self.noise_reduction_checkbox.isChecked()
            use_adaptive = self.adaptive_threshold_checkbox.isChecked()
            blur_kernel = self.blur_kernel_spinbox.value()
            morph_close = self.morph_close_spinbox.value()
            morph_open = self.morph_open_spinbox.value()
            adaptive_block = self.adaptive_block_spinbox.value()
            adaptive_c = self.adaptive_c_spinbox.value()

            # Process image
            self.binary_mask, coverage_pct = process_image(
                str(self.current_image.file_path),
                threshold_value=threshold if not use_adaptive else None,
                noise_reduction=noise_reduction,
                roi=None,
                use_adaptive=use_adaptive,
                blur_kernel=blur_kernel,
                morph_close_kernel=morph_close,
                morph_open_kernel=morph_open,
                adaptive_block_size=adaptive_block,
                adaptive_c=adaptive_c
            )

            # Generate overlay
            overlay_img = generate_overlay(
                self.original_cv_image,
                self.binary_mask,
                opacity=self.transparency_slider.get_opacity(),
                color=(0, 0, 255)  # Red in BGR
            )
            self.image_viewer.set_overlay_image(overlay_img)

            # Create detection result
            self.current_result = DetectionResult(
                image_ref=self.current_image,
                coverage_percentage=coverage_pct,
                area_um2=0.0,  # No calibration yet
                threshold_value=threshold,
                roi_coords=None,
                film_pixel_count=int(cv2.countNonZero(self.binary_mask)),
                total_pixel_count=self.binary_mask.size,
                processing_timestamp=datetime.now()
            )

            # Update UI
            self.coverage_label.setText(f"Coverage: {coverage_pct:.2f}%")
            self.area_label.setText("Area: N/A (uncalibrated)")

            self.current_image.status = ImageStatus.COMPLETE

            # Update overlay display if it's enabled
            if self.overlay_checkbox.isChecked():
                self.image_viewer.toggle_overlay(True)

            print(f"Processed image: {coverage_pct:.2f}% coverage")

        except Exception as e:
            self.current_image.status = ImageStatus.ERROR
            self.logger.log_error("ProcessingError", str(e), context_info=str(self.current_image.file_path))
            show_error_dialog(
                self,
                "Processing Error",
                f"Error processing image: {str(e)}"
            )

    def on_threshold_changed(self, new_threshold: int):
        """Handle threshold slider change - real-time processing."""
        # Auto-reprocess if image is loaded
        if self.original_cv_image is not None:
            self.process_current_image()

    def on_noise_reduction_changed(self, checked: bool):
        """Handle noise reduction checkbox change - real-time processing."""
        # Auto-reprocess if image is loaded
        if self.original_cv_image is not None:
            self.process_current_image()

    def on_threshold_method_changed(self, checked: bool):
        """Handle adaptive threshold checkbox change - real-time processing."""
        # Disable threshold slider when using adaptive method
        self.threshold_slider.setEnabled(not checked)
        # Auto-reprocess if image is loaded
        if self.original_cv_image is not None:
            self.process_current_image()

    def on_transparency_changed(self, new_opacity: float):
        """Handle transparency slider change - real-time overlay update."""
        # Update overlay if it exists
        if self.binary_mask is not None and self.original_cv_image is not None:
            overlay_img = generate_overlay(
                self.original_cv_image,
                self.binary_mask,
                opacity=new_opacity,
                color=(0, 0, 255)
            )
            self.image_viewer.set_overlay_image(overlay_img)

            # Refresh display if overlay is shown
            if self.overlay_checkbox.isChecked():
                self.image_viewer.toggle_overlay(True)

    def on_overlay_toggled(self, checked: bool):
        """Handle overlay checkbox toggle - real-time display update."""
        self.image_viewer.toggle_overlay(checked)

    def on_blur_kernel_changed(self, value: int):
        """Handle blur kernel size change - real-time processing."""
        print(f"Blur kernel changed to: {value}")
        # Auto-reprocess if image is loaded
        if self.original_cv_image is not None:
            self.process_current_image()

    def on_morph_close_changed(self, value: int):
        """Handle morphological close kernel change - real-time processing."""
        print(f"Morph close changed to: {value}")
        # Auto-reprocess if image is loaded
        if self.original_cv_image is not None:
            self.process_current_image()

    def on_morph_open_changed(self, value: int):
        """Handle morphological open kernel change - real-time processing."""
        print(f"Morph open changed to: {value}")
        # Auto-reprocess if image is loaded
        if self.original_cv_image is not None:
            self.process_current_image()

    def on_adaptive_block_changed(self, value: int):
        """Handle adaptive block size change - real-time processing."""
        print(f"Adaptive block changed to: {value}")
        # Auto-reprocess if image is loaded
        if self.original_cv_image is not None:
            self.process_current_image()

    def on_adaptive_c_changed(self, value: int):
        """Handle adaptive C constant change - real-time processing."""
        print(f"Adaptive C changed to: {value}")
        # Auto-reprocess if image is loaded
        if self.original_cv_image is not None:
            self.process_current_image()

    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event for drag-and-drop."""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            # Filter for supported image formats
            valid_files = [f for f in files if Path(f).suffix.lower() in SUPPORTED_IMAGE_FORMATS]
            if valid_files:
                self.load_image_batch(valid_files)

    def load_image_batch(self, file_paths: List[str]):
        """
        Load multiple images for batch processing.

        Args:
            file_paths: List of image file paths
        """
        self.image_batch = file_paths
        self.current_image_index = 0

        # Update dropdown
        self.image_selector.blockSignals(True)  # Prevent triggering currentIndexChanged
        self.image_selector.clear()
        for i, path in enumerate(file_paths):
            filename = Path(path).name
            self.image_selector.addItem(f"{i+1}. {filename}", path)
        self.image_selector.blockSignals(False)

        # Update navigation buttons
        self._update_navigation_buttons()

        # Load first image
        if file_paths:
            self.load_image(file_paths[0])

    def load_previous_image(self):
        """Load the previous image in the batch."""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.image_selector.setCurrentIndex(self.current_image_index)
            self.load_image(self.image_batch[self.current_image_index])

    def load_next_image(self):
        """Load the next image in the batch."""
        if self.current_image_index < len(self.image_batch) - 1:
            self.current_image_index += 1
            self.image_selector.setCurrentIndex(self.current_image_index)
            self.load_image(self.image_batch[self.current_image_index])

    def on_image_selected(self, index: int):
        """Handle image selection from dropdown."""
        if index >= 0 and index < len(self.image_batch):
            self.current_image_index = index
            self.load_image(self.image_batch[index])
            self._update_navigation_buttons()

    def _update_navigation_buttons(self):
        """Update the enabled state of navigation buttons."""
        has_images = len(self.image_batch) > 0
        has_prev = self.current_image_index > 0
        has_next = self.current_image_index < len(self.image_batch) - 1

        self.prev_button.setEnabled(has_images and has_prev)
        self.next_button.setEnabled(has_images and has_next)

        # Update counter label
        if has_images:
            self.image_counter_label.setText(
                f"Image {self.current_image_index + 1} of {len(self.image_batch)}"
            )
        else:
            self.image_counter_label.setText("No images loaded")

    def closeEvent(self, event):
        """Handle window close event."""
        # Save settings before closing
        self._save_settings()
        event.accept()
