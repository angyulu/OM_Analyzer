"""
Main application window for the Thin Film Analyzer.
"""

import cv2
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCheckBox, QFileDialog, QLabel, QGroupBox, QMessageBox, QComboBox, QSlider, QSpinBox,
    QProgressDialog, QApplication, QScrollArea
)
from PyQt6.QtCore import Qt

from .image_viewer import ImageViewer
from .widgets import ThresholdSlider, TransparencySlider, ThumbnailPanel, BatchProgressBar
from .results_table import ResultsTable
from .dialogs import show_error_dialog, show_info_dialog

from ..models.image import Image, ImageStatus
from ..models.detection_result import DetectionResult
from ..core.processor import process_image, process_image_hybrid, load_image_metadata, load_image_with_fallback
from ..core.overlay import generate_overlay, generate_layer_overlay
from ..core.detection_algorithms import (
    detect_thresholds_kmeans,
    detect_thresholds_percentile,
    detect_thresholds_histogram,
    detect_thresholds_otsu_multi
)
from ..core.export import save_analyzed_image_with_overlay, append_result_to_text_file, handle_duplicate_result
from ..core.settings import SettingsManager
from ..core.logger import get_logger
from ..core.detection import calculate_otsu_threshold, apply_noise_reduction
from ..config.defaults import (
    SUPPORTED_IMAGE_FORMATS, DEFAULT_THRESHOLD, DEFAULT_OVERLAY_TRANSPARENCY,
    MINIMUM_WINDOW_WIDTH, MINIMUM_WINDOW_HEIGHT, CONTROL_PANEL_MAX_WIDTH
)
import cv2
import numpy as np


class MainWindow(QMainWindow):
    """
    Main application window with drag-drop, image processing, and results display.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thin Film Coverage Analyzer v2.2.1")
        self.resize(1200, 800)
        self.setMinimumSize(MINIMUM_WINDOW_WIDTH, MINIMUM_WINDOW_HEIGHT)  # v2.2.0: Set minimum window size

        # Initialize managers
        self.settings_manager = SettingsManager()
        self.logger = get_logger()
        self.settings = self.settings_manager.load_settings()

        # State
        self.current_image: Optional[Image] = None
        self.current_result: Optional[DetectionResult] = None
        self.binary_mask: Optional = None
        self.original_cv_image: Optional = None
        self.layer_mask: Optional = None  # v2.1.0: Layer classification mask

        # Batch processing state
        self.image_batch: List[str] = []  # List of image file paths
        self.current_image_index: int = 0  # Current image index in batch
        self.batch_results: List[DetectionResult] = []  # Processed results for batch export (v2.1.0)
        self.current_folder: Optional[Path] = None  # v2.2.0: Track current folder for results file

        # Debouncing timer for parameter changes
        from PyQt6.QtCore import QTimer
        self.processing_timer = QTimer()
        self.processing_timer.setSingleShot(True)
        self.processing_timer.timeout.connect(self._do_process_image)

        self._init_ui()
        self._load_settings()

        # v2.2.0: Drag-and-drop removed in favor of folder selection

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

        # v2.2.0: Add folder selection
        select_folder_action = file_menu.addAction("Select Folder...")
        select_folder_action.setShortcut("Ctrl+Shift+O")
        select_folder_action.setToolTip("Load all images from a selected folder")
        select_folder_action.triggered.connect(self.select_folder_dialog)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        # Batch menu (v2.1.0)
        batch_menu = menubar.addMenu("Batch")

        process_all_action = batch_menu.addAction("Process All Images")
        process_all_action.setShortcut("Ctrl+P")
        process_all_action.setToolTip("Process all loaded images with current settings")
        process_all_action.triggered.connect(self.on_batch_process_all)

        batch_menu.addSeparator()

        export_csv_action = batch_menu.addAction("Export Results to CSV...")
        export_csv_action.setShortcut("Ctrl+E")
        export_csv_action.setToolTip("Export batch results to CSV file")
        export_csv_action.triggered.connect(self.on_batch_export_csv)

        export_overlays_action = batch_menu.addAction("Export Overlay Images...")
        export_overlays_action.setToolTip("Save overlay images for all processed images")
        export_overlays_action.triggered.connect(self.on_batch_export_overlays)

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

        # Adaptive bias (v2.1.0)
        adaptive_bias_layout = QHBoxLayout()
        adaptive_bias_label = QLabel("Adaptive Bias:")
        self.adaptive_bias_spinbox = QSpinBox()
        self.adaptive_bias_spinbox.setRange(-10, 10)
        self.adaptive_bias_spinbox.setValue(0)
        self.adaptive_bias_spinbox.setToolTip(
            "Fine-tune adaptive threshold sensitivity\n"
            "Negative = more sensitive (detect thinner flakes)\n"
            "Positive = less sensitive (only thicker flakes)"
        )
        self.adaptive_bias_spinbox.valueChanged.connect(self.on_adaptive_bias_changed)
        adaptive_bias_layout.addWidget(adaptive_bias_label)
        adaptive_bias_layout.addWidget(self.adaptive_bias_spinbox)
        process_layout.addLayout(adaptive_bias_layout)

        process_group.setLayout(process_layout)
        layout.addWidget(process_group)

        # V2 Layer Classification panel (v2.1.0)
        v2_group = self._create_v2_layer_panel()
        layout.addWidget(v2_group)

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

        self.coverage_label = QLabel("Total Coverage: --")
        self.coverage_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        results_layout.addWidget(self.coverage_label)

        self.area_label = QLabel("Area: --")
        results_layout.addWidget(self.area_label)

        # Layer breakdown (v2.1.0)
        self.mono_label = QLabel("Monolayer: --")
        self.mono_label.setStyleSheet("color: red;")
        results_layout.addWidget(self.mono_label)

        self.bi_label = QLabel("Bilayer: --")
        self.bi_label.setStyleSheet("color: blue;")
        results_layout.addWidget(self.bi_label)

        self.tri_label = QLabel("Trilayer: --")
        self.tri_label.setStyleSheet("color: green;")
        results_layout.addWidget(self.tri_label)

        # Processing indicator
        self.processing_label = QLabel("⏳ Processing...")
        self.processing_label.setStyleSheet("color: orange; font-style: italic;")
        self.processing_label.hide()
        results_layout.addWidget(self.processing_label)

        # v2.2.0: Submit button for saving results
        self.submit_button = QPushButton("Submit")
        self.submit_button.setToolTip("Save analyzed image and append results to text file")
        self.submit_button.setEnabled(False)  # Disabled by default
        self.submit_button.clicked.connect(self.submit_current_image)
        results_layout.addWidget(self.submit_button)

        # Success feedback label
        self.submit_feedback_label = QLabel("")
        self.submit_feedback_label.setStyleSheet("color: green; font-style: italic;")
        self.submit_feedback_label.hide()
        results_layout.addWidget(self.submit_feedback_label)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        layout.addStretch()

        panel.setLayout(layout)

        # v2.2.1: Wrap panel in scroll area to prevent controls from being blocked when window shrinks
        scroll_area = QScrollArea()
        scroll_area.setWidget(panel)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)  # Clean appearance, no border
        scroll_area.setMaximumWidth(CONTROL_PANEL_MAX_WIDTH)  # Same width constraint as panel

        return scroll_area

    def _create_v2_layer_panel(self) -> QGroupBox:
        """Create V2 layer classification panel (v2.1.0)."""
        group = QGroupBox("Layer Classification (V2)")
        layout = QVBoxLayout()

        # Enable layer detection checkbox
        self.enable_layer_detection_checkbox = QCheckBox("Enable Layer Detection")
        self.enable_layer_detection_checkbox.setChecked(False)  # Default disabled (V1 only)
        self.enable_layer_detection_checkbox.setToolTip(
            "Enable/disable V2 layer classification.\n"
            "Checked: Full V1+V2 pipeline (film + layer detection)\n"
            "Unchecked: V1 only (basic film detection)"
        )
        self.enable_layer_detection_checkbox.toggled.connect(self.on_layer_detection_toggled)
        layout.addWidget(self.enable_layer_detection_checkbox)

        # Algorithm selector
        algo_layout = QHBoxLayout()
        algo_label = QLabel("Algorithm:")
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["K-means", "Percentile", "Histogram", "Otsu Multi"])
        self.algorithm_combo.setCurrentIndex(0)  # Default to K-means
        self.algorithm_combo.setToolTip("Auto-detection algorithm for T1/T2 thresholds")
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.algorithm_combo)
        layout.addLayout(algo_layout)

        # Auto-detect button
        self.auto_detect_button = QPushButton("Auto-Detect Thresholds")
        self.auto_detect_button.setToolTip("Automatically calculate T1 and T2 using selected algorithm")
        self.auto_detect_button.clicked.connect(self.on_auto_detect_thresholds)
        layout.addWidget(self.auto_detect_button)

        # T1 slider (Mono/Bi boundary)
        t1_layout = QVBoxLayout()
        t1_label = QLabel("T1 (Mono/Bi Boundary):")
        self.t1_slider = QSlider(Qt.Orientation.Horizontal)
        self.t1_slider.setRange(0, 255)
        self.t1_slider.setValue(85)  # Default from defaults.py
        self.t1_slider.setToolTip("Threshold between monolayer and bilayer (lower L-values)")
        self.t1_value_label = QLabel("85")
        self.t1_slider.valueChanged.connect(self.on_t1_changed)
        t1_layout.addWidget(t1_label)
        t1_value_layout = QHBoxLayout()
        t1_value_layout.addWidget(self.t1_slider)
        t1_value_layout.addWidget(self.t1_value_label)
        t1_layout.addLayout(t1_value_layout)
        layout.addLayout(t1_layout)

        # T2 slider (Bi/Tri boundary)
        t2_layout = QVBoxLayout()
        t2_label = QLabel("T2 (Bi/Tri Boundary):")
        self.t2_slider = QSlider(Qt.Orientation.Horizontal)
        self.t2_slider.setRange(0, 255)
        self.t2_slider.setValue(170)  # Default from defaults.py
        self.t2_slider.setToolTip("Threshold between bilayer and trilayer (higher L-values)")
        self.t2_value_label = QLabel("170")
        self.t2_slider.valueChanged.connect(self.on_t2_changed)
        t2_layout.addWidget(t2_label)
        t2_value_layout = QHBoxLayout()
        t2_value_layout.addWidget(self.t2_slider)
        t2_value_layout.addWidget(self.t2_value_label)
        t2_layout.addLayout(t2_value_layout)
        layout.addLayout(t2_layout)

        # Lock thresholds button
        self.lock_thresholds_button = QPushButton("🔓 Unlock Thresholds")
        self.lock_thresholds_button.setCheckable(True)
        self.lock_thresholds_button.setChecked(False)
        self.lock_thresholds_button.setToolTip(
            "Lock T1/T2 for batch consistency.\n"
            "Locked: All batch images use these values.\n"
            "Unlocked: Manual adjustment per image."
        )
        self.lock_thresholds_button.toggled.connect(self.on_lock_thresholds_toggled)
        layout.addWidget(self.lock_thresholds_button)

        # Vignetting correction checkbox
        self.vignetting_correction_checkbox = QCheckBox("Apply Vignetting Correction")
        self.vignetting_correction_checkbox.setChecked(True)
        self.vignetting_correction_checkbox.setToolTip(
            "Correct for vignetting (darker edges) in L-channel analysis"
        )
        self.vignetting_correction_checkbox.toggled.connect(self.on_vignetting_correction_changed)
        layout.addWidget(self.vignetting_correction_checkbox)

        group.setLayout(layout)
        return group

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

    def select_folder_dialog(self):
        """Open folder dialog to select a folder and load all images from it (v2.2.0)."""
        # Use last folder path as starting directory
        start_dir = self.settings.last_folder_path if self.settings.last_folder_path else ""

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder Containing Images",
            start_dir,
            QFileDialog.Option.ShowDirsOnly
        )

        if folder_path:
            image_files = self.load_images_from_folder(folder_path)
            if image_files:
                self.current_folder = Path(folder_path)  # v2.2.0: Track folder for results file

                # Save last folder path to settings
                self.settings.last_folder_path = folder_path
                self.settings_manager.save_settings(self.settings)

                self.load_image_batch(image_files)
            else:
                show_info_dialog(
                    self,
                    "No Images Found",
                    f"No supported image files found in the selected folder.\n"
                    f"Supported formats: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
                )

    def load_images_from_folder(self, folder_path: str) -> List[str]:
        """
        Scan folder for supported image files (v2.2.0).

        Args:
            folder_path: Path to folder to scan

        Returns:
            List of image file paths found in folder
        """
        folder = Path(folder_path)
        image_files = []

        # Get all files in folder (non-recursive)
        all_files = list(folder.glob("*"))

        # Create progress dialog
        progress = QProgressDialog(
            "Scanning folder for images...",
            "Cancel",
            0,
            len(all_files),
            self
        )
        progress.setWindowTitle("Loading Images")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        for i, file_path in enumerate(all_files):
            # Check if user canceled
            if progress.wasCanceled():
                break

            # Update progress
            progress.setValue(i)
            progress.setLabelText(f"Loading images: {len(image_files)} / {len(all_files)}")
            QApplication.processEvents()  # Update UI

            # Check if it's a file (not directory) with supported extension
            if file_path.is_file():
                ext = file_path.suffix.lower()
                # Exclude _analyzed files and check for supported format
                if ext in SUPPORTED_IMAGE_FORMATS and "_analyzed" not in file_path.stem:
                    image_files.append(str(file_path))

        progress.setValue(len(all_files))
        progress.close()

        return image_files

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
            self.image_viewer.display_image(self.original_cv_image, is_original=True)

            # Calculate optimal threshold using Otsu's method
            gray = cv2.cvtColor(self.original_cv_image, cv2.COLOR_BGR2GRAY)
            if self.noise_reduction_checkbox.isChecked():
                gray = apply_noise_reduction(gray, kernel_size=self.blur_kernel_spinbox.value())
            optimal_threshold = calculate_otsu_threshold(gray)
            self.threshold_slider.set_value(optimal_threshold)

            # Reset results
            self.coverage_label.setText("Total Coverage: --")
            self.area_label.setText("Area: --")
            self.mono_label.setText("Monolayer: --")
            self.bi_label.setText("Bilayer: --")
            self.tri_label.setText("Trilayer: --")
            self.current_result = None
            self.binary_mask = None
            self.layer_mask = None

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

    def _do_process_image(self):
        """Internal method called by debouncing timer to process image."""
        self.processing_label.show()
        self.process_current_image()
        self.processing_label.hide()

    def process_current_image(self):
        """Process the currently loaded image using V1 or hybrid V1+V2 pipeline."""
        if self.current_image is None:
            return

        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt as QtCore_Qt

            # Set wait cursor during processing
            QApplication.setOverrideCursor(QtCore_Qt.CursorShape.WaitCursor)

            self.current_image.status = ImageStatus.PROCESSING

            # Get V1 processing parameters
            threshold = self.threshold_slider.get_value()
            noise_reduction = self.noise_reduction_checkbox.isChecked()
            use_adaptive = self.adaptive_threshold_checkbox.isChecked()
            blur_kernel = self.blur_kernel_spinbox.value()
            morph_close = self.morph_close_spinbox.value()
            morph_open = self.morph_open_spinbox.value()
            adaptive_block = self.adaptive_block_spinbox.value()
            adaptive_c = self.adaptive_c_spinbox.value()
            adaptive_bias = self.adaptive_bias_spinbox.value()

            # Check if layer detection is enabled
            if self.enable_layer_detection_checkbox.isChecked():
                # V1+V2 hybrid pipeline
                print("[DEBUG] Processing with V2 layer detection enabled")
                t1 = self.t1_slider.value()
                t2 = self.t2_slider.value()
                apply_vignetting = self.vignetting_correction_checkbox.isChecked()
                print(f"[DEBUG] V2 parameters: T1={t1}, T2={t2}, Vignetting={apply_vignetting}")

                original_img, self.binary_mask, combined_stats, self.layer_mask = process_image_hybrid(
                    str(self.current_image.file_path),
                    # V1 parameters
                    threshold_value=threshold if not use_adaptive else None,
                    use_adaptive=use_adaptive,
                    adaptive_block_size=adaptive_block,
                    adaptive_c=adaptive_c,
                    adaptive_bias=adaptive_bias,
                    noise_reduction=noise_reduction,
                    blur_kernel=blur_kernel,
                    morph_close_kernel=morph_close,
                    morph_open_kernel=morph_open,
                    # V2 parameters
                    t1=t1,
                    t2=t2,
                    apply_vignetting_correction=apply_vignetting,
                    # Other
                    roi=None
                )
                print(f"[DEBUG] Hybrid processing complete. Stats: {combined_stats}")
                print(f"[DEBUG] Binary mask shape: {self.binary_mask.shape}, Layer mask shape: {self.layer_mask.shape}")

                # Generate layer overlay (color-coded: Red=mono, Blue=bi, Green=tri)
                overlay_img = generate_layer_overlay(
                    original_img,
                    self.layer_mask,
                    opacity=self.transparency_slider.get_opacity()
                )

                # Create detection result with layer statistics
                self.current_result = DetectionResult(
                    image_ref=self.current_image,
                    coverage_percentage=combined_stats['total_coverage'],
                    area_um2=0.0,
                    threshold_value=threshold,
                    roi_coords=None,
                    film_pixel_count=int(cv2.countNonZero(self.binary_mask)),
                    total_pixel_count=self.binary_mask.size,
                    processing_timestamp=datetime.now(),
                    mono_coverage=combined_stats['mono_coverage'],
                    bi_coverage=combined_stats['bi_coverage'],
                    tri_coverage=combined_stats['tri_coverage'],
                    thresholds=(t1, t2)
                )

                # Update UI with layer breakdown
                self.coverage_label.setText(f"Total Coverage: {combined_stats['total_coverage']:.2f}%")
                self.area_label.setText("Area: N/A (uncalibrated)")
                self.mono_label.setText(f"Monolayer: {combined_stats['mono_coverage']:.2f}%")
                self.bi_label.setText(f"Bilayer: {combined_stats['bi_coverage']:.2f}%")
                self.tri_label.setText(f"Trilayer: {combined_stats['tri_coverage']:.2f}%")

                print(f"Processed image: {combined_stats['total_coverage']:.2f}% total coverage")
                print(f"  Mono: {combined_stats['mono_coverage']:.2f}%, Bi: {combined_stats['bi_coverage']:.2f}%, Tri: {combined_stats['tri_coverage']:.2f}%")
                print(f"[DEBUG] Overlay image generated, shape: {overlay_img.shape}")

            else:
                # V1 only pipeline
                print("[DEBUG] Processing with V1 only (layer detection disabled)")
                self.binary_mask, v1_coverage = process_image(
                    str(self.current_image.file_path),
                    threshold_value=threshold if not use_adaptive else None,
                    noise_reduction=noise_reduction,
                    roi=None,
                    use_adaptive=use_adaptive,
                    blur_kernel=blur_kernel,
                    morph_close_kernel=morph_close,
                    morph_open_kernel=morph_open,
                    adaptive_block_size=adaptive_block,
                    adaptive_c=adaptive_c,
                    adaptive_bias=adaptive_bias
                )
                self.layer_mask = None

                # Generate simple red overlay
                overlay_img = generate_overlay(
                    self.original_cv_image,
                    self.binary_mask,
                    opacity=self.transparency_slider.get_opacity()
                )

                # Create detection result without layer statistics
                self.current_result = DetectionResult(
                    image_ref=self.current_image,
                    coverage_percentage=v1_coverage,
                    area_um2=0.0,
                    threshold_value=threshold,
                    roi_coords=None,
                    film_pixel_count=int(cv2.countNonZero(self.binary_mask)),
                    total_pixel_count=self.binary_mask.size,
                    processing_timestamp=datetime.now(),
                    mono_coverage=None,
                    bi_coverage=None,
                    tri_coverage=None,
                    thresholds=None
                )

                # Update UI (no layer breakdown)
                self.coverage_label.setText(f"Total Coverage: {v1_coverage:.2f}%")
                self.area_label.setText("Area: N/A (uncalibrated)")
                self.mono_label.setText("Monolayer: --")
                self.bi_label.setText("Bilayer: --")
                self.tri_label.setText("Trilayer: --")

                print(f"Processed image: {v1_coverage:.2f}% total coverage (V1 only)")

            # Set overlay image and display
            print(f"[DEBUG] Setting overlay image, overlay_img is None: {overlay_img is None}")
            self.image_viewer.set_overlay_image(overlay_img)

            self.current_image.status = ImageStatus.COMPLETE

            # Update overlay display if it's enabled
            overlay_enabled = self.overlay_checkbox.isChecked()
            print(f"[DEBUG] Overlay checkbox is checked: {overlay_enabled}")
            if overlay_enabled:
                print("[DEBUG] Calling toggle_overlay(True)")
                self.image_viewer.toggle_overlay(True)
            else:
                print("[DEBUG] Calling toggle_overlay(False)")
                self.image_viewer.toggle_overlay(False)

        except Exception as e:
            self.current_image.status = ImageStatus.ERROR
            import traceback
            error_details = traceback.format_exc()
            print(f"[ERROR] Processing failed: {str(e)}")
            print(f"[ERROR] Full traceback:\n{error_details}")
            self.logger.log_error("ProcessingError", str(e), context_info=str(self.current_image.file_path))
            show_error_dialog(
                self,
                "Processing Error",
                f"Error processing image: {str(e)}\n\nCheck console for full details."
            )
        finally:
            # Restore cursor
            QApplication.restoreOverrideCursor()
            # v2.2.0: Update submit button state
            self.update_submit_button_state()

    def on_threshold_changed(self, new_threshold: int):
        """Handle threshold slider change - debounced processing."""
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)  # 300ms delay

    def on_noise_reduction_changed(self, checked: bool):
        """Handle noise reduction checkbox change - debounced processing."""
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_threshold_method_changed(self, checked: bool):
        """Handle adaptive threshold checkbox change - debounced processing."""
        # Disable threshold slider when using adaptive method
        self.threshold_slider.setEnabled(not checked)
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_transparency_changed(self, new_opacity: float):
        """Handle transparency slider change - real-time overlay update."""
        # Update overlay if it exists
        if self.original_cv_image is not None and self.binary_mask is not None:
            if self.enable_layer_detection_checkbox.isChecked() and self.layer_mask is not None:
                # V2 layer overlay
                overlay_img = generate_layer_overlay(
                    self.original_cv_image,
                    self.layer_mask,
                    opacity=new_opacity
                )
            else:
                # V1 simple overlay
                overlay_img = generate_overlay(
                    self.original_cv_image,
                    self.binary_mask,
                    opacity=new_opacity
                )

            self.image_viewer.set_overlay_image(overlay_img)

            # Refresh display if overlay is shown
            if self.overlay_checkbox.isChecked():
                self.image_viewer.toggle_overlay(True)

    def on_overlay_toggled(self, checked: bool):
        """Handle overlay checkbox toggle - real-time display update."""
        self.image_viewer.toggle_overlay(checked)

    def update_submit_button_state(self):
        """Update submit button enabled state based on current conditions (v2.2.0)."""
        # Enable submit if we have a valid result and a folder is selected
        can_submit = (
            self.current_image is not None and
            self.current_result is not None and
            self.current_folder is not None
        )
        self.submit_button.setEnabled(can_submit)

    def submit_current_image(self):
        """Submit current image analysis: save overlay image and append to results file (v2.2.0)."""
        # Validate state
        if not self.current_image or not self.current_result:
            show_error_dialog(
                self,
                "Submit Error",
                "No image or analysis result available. Please process an image first."
            )
            return

        if not self.current_folder:
            show_error_dialog(
                self,
                "Submit Error",
                "No folder selected. Please use 'Select Folder' to load images first."
            )
            return

        # Hide previous feedback
        self.submit_feedback_label.hide()

        try:
            # Get overlay image from viewer
            overlay_image = self.image_viewer.get_overlay_image()
            if overlay_image is None:
                show_error_dialog(
                    self,
                    "Submit Error",
                    "No overlay image available. The analysis may have failed."
                )
                return

            # Save analyzed image
            success, message = save_analyzed_image_with_overlay(
                self.current_image.file_path,
                overlay_image
            )

            if not success:
                show_error_dialog(
                    self,
                    "Image Save Error",
                    f"Failed to save analyzed image:\n{message}"
                )
                return

            analyzed_image_path = message  # message contains the path on success

            # Prepare result data
            filename = Path(self.current_image.file_path).name
            coverage = self.current_result.coverage_percentage
            # v2.2.0 fix: Check if values are None, not just if attribute exists
            mono_coverage = self.current_result.mono_coverage if self.current_result.mono_coverage is not None else 0.0
            bi_coverage = self.current_result.bi_coverage if self.current_result.bi_coverage is not None else 0.0
            tri_coverage = self.current_result.tri_coverage if self.current_result.tri_coverage is not None else 0.0

            # Append to results file
            success, message, duplicate_action = append_result_to_text_file(
                self.current_folder,
                filename,
                coverage,
                mono_coverage,
                bi_coverage,
                tri_coverage
            )

            if not success:
                if message == "duplicate":
                    # Handle duplicate - show dialog
                    choice = self.show_duplicate_dialog(filename)
                    if choice == "cancel":
                        return
                    elif choice in ["overwrite", "append"]:
                        # Handle the duplicate with chosen action
                        success, message = handle_duplicate_result(
                            self.current_folder,
                            filename,
                            coverage,
                            mono_coverage,
                            bi_coverage,
                            tri_coverage,
                            choice
                        )
                        if not success:
                            show_error_dialog(
                                self,
                                "Results Save Error",
                                f"Failed to save results:\n{message}"
                            )
                            return
                else:
                    show_error_dialog(
                        self,
                        "Results Save Error",
                        f"Failed to save results:\n{message}"
                    )
                    return

            # Show success feedback
            results_file = self.current_folder / f"{self.current_folder.name}_Analyzed.txt"
            self.submit_feedback_label.setText(f"✓ Saved: {Path(analyzed_image_path).name}")
            self.submit_feedback_label.show()

            # Auto-hide feedback after 5 seconds
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(5000, self.submit_feedback_label.hide)

        except Exception as e:
            show_error_dialog(
                self,
                "Submit Error",
                f"An unexpected error occurred:\n{str(e)}"
            )

    def show_duplicate_dialog(self, filename: str) -> str:
        """Show dialog for handling duplicate results (v2.2.0)."""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Duplicate Result")
        dialog.setText(f"Results for '{filename}' already exist in the results file.")
        dialog.setInformativeText("What would you like to do?")

        overwrite_btn = dialog.addButton("Overwrite", QMessageBox.ButtonRole.AcceptRole)
        append_btn = dialog.addButton("Append new row", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        dialog.exec()

        clicked = dialog.clickedButton()
        if clicked == overwrite_btn:
            return "overwrite"
        elif clicked == append_btn:
            return "append"
        else:
            return "cancel"

    def on_blur_kernel_changed(self, value: int):
        """Handle blur kernel size change - debounced processing."""
        print(f"Blur kernel changed to: {value}")
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_morph_close_changed(self, value: int):
        """Handle morphological close kernel change - debounced processing."""
        print(f"Morph close changed to: {value}")
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_morph_open_changed(self, value: int):
        """Handle morphological open kernel change - debounced processing."""
        print(f"Morph open changed to: {value}")
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_adaptive_block_changed(self, value: int):
        """Handle adaptive block size change - debounced processing."""
        print(f"Adaptive block changed to: {value}")
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_adaptive_c_changed(self, value: int):
        """Handle adaptive C constant change - debounced processing."""
        print(f"Adaptive C changed to: {value}")
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_adaptive_bias_changed(self, value: int):
        """Handle adaptive bias change - debounced processing (v2.1.0)."""
        print(f"Adaptive bias changed to: {value}")
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_t1_changed(self, value: int):
        """Handle T1 slider change - debounced processing (v2.1.0)."""
        self.t1_value_label.setText(str(value))
        # Ensure T1 < T2
        if value >= self.t2_slider.value():
            self.t2_slider.setValue(value + 1)
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_t2_changed(self, value: int):
        """Handle T2 slider change - debounced processing (v2.1.0)."""
        self.t2_value_label.setText(str(value))
        # Ensure T1 < T2
        if value <= self.t1_slider.value():
            self.t1_slider.setValue(value - 1)
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_vignetting_correction_changed(self, checked: bool):
        """Handle vignetting correction checkbox change - debounced processing (v2.1.0)."""
        print(f"Vignetting correction: {checked}")
        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_layer_detection_toggled(self, checked: bool):
        """Handle layer detection enable/disable toggle."""
        # Enable/disable V2 controls based on checkbox state
        self.algorithm_combo.setEnabled(checked)
        self.auto_detect_button.setEnabled(checked)
        self.t1_slider.setEnabled(checked and not self.lock_thresholds_button.isChecked())
        self.t2_slider.setEnabled(checked and not self.lock_thresholds_button.isChecked())
        self.lock_thresholds_button.setEnabled(checked)
        self.vignetting_correction_checkbox.setEnabled(checked)

        print(f"Layer detection: {'enabled' if checked else 'disabled'}")

        if self.original_cv_image is not None:
            self.processing_timer.stop()
            self.processing_timer.start(300)

    def on_lock_thresholds_toggled(self, checked: bool):
        """Handle threshold lock toggle (v2.1.0)."""
        if checked:
            # Locked state
            self.lock_thresholds_button.setText("🔒 Lock Thresholds")
            self.t1_slider.setEnabled(False)
            self.t2_slider.setEnabled(False)
            print(f"Thresholds locked: T1={self.t1_slider.value()}, T2={self.t2_slider.value()}")
        else:
            # Unlocked state
            self.lock_thresholds_button.setText("🔓 Unlock Thresholds")
            self.t1_slider.setEnabled(True)
            self.t2_slider.setEnabled(True)
            print("Thresholds unlocked")

    def on_auto_detect_thresholds(self):
        """Auto-detect T1 and T2 thresholds using selected algorithm (v2.1.0)."""
        if self.binary_mask is None or self.original_cv_image is None:
            show_info_dialog(
                self,
                "No Image Loaded",
                "Please load an image first before auto-detecting thresholds."
            )
            return

        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt as QtCore_Qt

            # Set wait cursor
            QApplication.setOverrideCursor(QtCore_Qt.CursorShape.WaitCursor)

            # Get selected algorithm
            algorithm = self.algorithm_combo.currentText()

            # Map algorithm name to function
            algorithm_map = {
                "K-means": detect_thresholds_kmeans,
                "Percentile": detect_thresholds_percentile,
                "Histogram": detect_thresholds_histogram,
                "Otsu Multi": detect_thresholds_otsu_multi
            }

            detect_func = algorithm_map[algorithm]

            # Run auto-detection
            t1, t2 = detect_func(self.binary_mask, self.original_cv_image)

            # Update sliders
            self.t1_slider.setValue(t1)
            self.t2_slider.setValue(t2)

            print(f"Auto-detected thresholds using {algorithm}: T1={t1}, T2={t2}")

            # Reprocess with new thresholds
            self.process_current_image()

        except Exception as e:
            self.logger.log_error("AutoDetectError", str(e))
            show_error_dialog(
                self,
                "Auto-Detection Error",
                f"Error auto-detecting thresholds: {str(e)}"
            )
        finally:
            QApplication.restoreOverrideCursor()

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

    def on_batch_process_all(self):
        """Process all images in batch with current settings (v2.1.0)."""
        if not self.image_batch:
            show_info_dialog(
                self,
                "No Images Loaded",
                "Please load multiple images first using File > Open Image or drag-and-drop."
            )
            return

        from PyQt6.QtWidgets import QProgressDialog, QApplication
        from PyQt6.QtCore import Qt as QtCore_Qt

        # Clear previous batch results
        self.batch_results.clear()

        # Get locked thresholds if applicable
        t1 = self.t1_slider.value()
        t2 = self.t2_slider.value()
        use_locked_thresholds = self.lock_thresholds_button.isChecked()

        # Create progress dialog
        progress = QProgressDialog(
            "Processing images...",
            "Cancel",
            0,
            len(self.image_batch),
            self
        )
        progress.setWindowModality(QtCore_Qt.WindowModality.WindowModal)
        progress.setWindowTitle("Batch Processing")
        progress.setMinimumDuration(0)

        try:
            for i, image_path in enumerate(self.image_batch):
                # Check if canceled
                if progress.wasCanceled():
                    show_info_dialog(self, "Cancelled", f"Batch processing cancelled. Processed {i} of {len(self.image_batch)} images.")
                    break

                # Update progress
                progress.setValue(i)
                progress.setLabelText(f"Processing {Path(image_path).name}... ({i+1}/{len(self.image_batch)})")
                QApplication.processEvents()

                # Load and process image
                self.load_image(image_path)

                # If thresholds are locked, ensure they're applied
                if use_locked_thresholds:
                    self.t1_slider.setValue(t1)
                    self.t2_slider.setValue(t2)
                    self.process_current_image()

                # Store result
                if self.current_result:
                    self.batch_results.append(self.current_result)

            progress.setValue(len(self.image_batch))

            if not progress.wasCanceled():
                show_info_dialog(
                    self,
                    "Batch Processing Complete",
                    f"Successfully processed {len(self.batch_results)} images.\n"
                    f"Use Batch > Export Results to CSV to save results."
                )

        except Exception as e:
            self.logger.log_error("BatchProcessError", str(e))
            show_error_dialog(
                self,
                "Batch Processing Error",
                f"Error during batch processing: {str(e)}"
            )
        finally:
            progress.close()

    def on_batch_export_csv(self):
        """Export batch results to CSV file (v2.1.0)."""
        if not self.batch_results:
            show_info_dialog(
                self,
                "No Results to Export",
                "Please process images first using Batch > Process All Images."
            )
            return

        from ..core.export import ResultsExporter
        from ..models.batch_session import BatchStatistics

        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results to CSV",
            f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return  # User cancelled

        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt as QtCore_Qt

            QApplication.setOverrideCursor(QtCore_Qt.CursorShape.WaitCursor)

            # Create exporter
            exporter = ResultsExporter()

            # Add all results
            for result in self.batch_results:
                exporter.add_result(
                    filename=result.image_ref.filename,
                    coverage_pct=result.coverage_percentage,
                    area_um2=result.area_um2 if result.area_um2 > 0 else None,
                    mono_coverage=result.mono_coverage,
                    bi_coverage=result.bi_coverage,
                    tri_coverage=result.tri_coverage
                )

            # Calculate summary statistics
            summary_stats = BatchStatistics.calculate(self.batch_results)

            # Export to CSV
            exporter.export_csv(
                output_path=Path(file_path),
                include_summary=True,
                summary_stats=summary_stats
            )

            QApplication.restoreOverrideCursor()

            show_info_dialog(
                self,
                "Export Successful",
                f"Results exported to:\n{file_path}\n\n"
                f"Exported {len(self.batch_results)} results with layer statistics."
            )

        except Exception as e:
            QApplication.restoreOverrideCursor()
            self.logger.log_error("CSVExportError", str(e))
            show_error_dialog(
                self,
                "Export Error",
                f"Error exporting to CSV: {str(e)}"
            )

    def on_batch_export_overlays(self):
        """Export overlay images for all processed results (v2.1.0)."""
        if not self.batch_results:
            show_info_dialog(
                self,
                "No Results to Export",
                "Please process images first using Batch > Process All Images."
            )
            return

        from ..core.export import ResultsExporter

        # Get save directory
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory for Overlay Images",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if not output_dir:
            return  # User cancelled

        try:
            from PyQt6.QtWidgets import QApplication, QProgressDialog
            from PyQt6.QtCore import Qt as QtCore_Qt

            QApplication.setOverrideCursor(QtCore_Qt.CursorShape.WaitCursor)

            # Create progress dialog
            progress = QProgressDialog(
                "Generating overlay images...",
                "Cancel",
                0,
                len(self.batch_results),
                self
            )
            progress.setWindowModality(QtCore_Qt.WindowModality.WindowModal)
            progress.setWindowTitle("Exporting Overlays")
            progress.setMinimumDuration(0)

            overlay_images = []

            for i, result in enumerate(self.batch_results):
                if progress.wasCanceled():
                    break

                progress.setValue(i)
                progress.setLabelText(f"Processing {result.image_ref.filename}... ({i+1}/{len(self.batch_results)})")
                QApplication.processEvents()

                # Load image and regenerate layer overlay
                img = load_image_with_fallback(str(result.image_ref.file_path))

                # Reprocess to get layer mask (we need to store this in batch_results in future)
                _, _, _, layer_mask = process_image_hybrid(
                    str(result.image_ref.file_path),
                    threshold_value=result.threshold_value,
                    t1=result.thresholds[0] if result.thresholds else 85,
                    t2=result.thresholds[1] if result.thresholds else 170
                )

                # Generate overlay
                overlay_img = generate_layer_overlay(img, layer_mask, opacity=0.5)
                overlay_images.append(overlay_img)

            progress.setValue(len(self.batch_results))
            progress.close()

            # Export overlay images
            exporter = ResultsExporter()
            exporter.export_images_with_overlay(
                results=self.batch_results,
                overlay_images=overlay_images,
                output_dir=Path(output_dir)
            )

            QApplication.restoreOverrideCursor()

            show_info_dialog(
                self,
                "Export Successful",
                f"Overlay images exported to:\n{output_dir}\n\n"
                f"Exported {len(overlay_images)} overlay images."
            )

        except Exception as e:
            QApplication.restoreOverrideCursor()
            self.logger.log_error("OverlayExportError", str(e))
            show_error_dialog(
                self,
                "Export Error",
                f"Error exporting overlay images: {str(e)}"
            )

    def closeEvent(self, event):
        """Handle window close event."""
        # Save settings before closing
        self._save_settings()
        event.accept()
