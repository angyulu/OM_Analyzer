"""
Dialog widgets for user confirmations and inputs.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt


class PresetOverwriteDialog(QDialog):
    """
    Confirmation dialog for overwriting existing scale presets.
    """

    def __init__(self, preset_name: str, parent=None):
        super().__init__(parent)
        self.preset_name = preset_name
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("Confirm Overwrite")
        self.setModal(True)

        layout = QVBoxLayout()

        # Message
        message = QLabel(f"Preset '{self.preset_name}' already exists. Overwrite?")
        message.setWordWrap(True)
        layout.addWidget(message)

        # Buttons
        button_layout = QHBoxLayout()
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")

        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)

        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class ScaleInputDialog(QDialog):
    """
    Dialog for manual scale calibration input.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("Manual Scale Calibration")
        self.setModal(True)

        layout = QVBoxLayout()

        # Scale input
        scale_label = QLabel("Enter scale calibration (µm/pixel):")
        layout.addWidget(scale_label)

        self.scale_input = QLineEdit()
        self.scale_input.setPlaceholderText("e.g., 0.65")
        layout.addWidget(self.scale_input)

        # Preset name input
        name_label = QLabel("Preset name (optional):")
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., 10x objective")
        layout.addWidget(self.name_input)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_values(self):
        """
        Get entered values.

        Returns:
            Tuple of (scale_value, preset_name) or None if invalid
        """
        try:
            scale_value = float(self.scale_input.text())
            preset_name = self.name_input.text().strip() or None
            return scale_value, preset_name
        except ValueError:
            return None


def show_error_dialog(parent, title: str, message: str):
    """
    Show an error message dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        message: Error message
    """
    QMessageBox.critical(parent, title, message)


def show_info_dialog(parent, title: str, message: str):
    """
    Show an information message dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        message: Information message
    """
    QMessageBox.information(parent, title, message)


def show_warning_dialog(parent, title: str, message: str) -> bool:
    """
    Show a warning message dialog with OK/Cancel buttons.

    Args:
        parent: Parent widget
        title: Dialog title
        message: Warning message

    Returns:
        True if user clicked OK, False if Cancel
    """
    reply = QMessageBox.warning(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
    )
    return reply == QMessageBox.StandardButton.Ok
