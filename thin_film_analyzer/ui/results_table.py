"""
Results table widget for displaying batch processing results.
"""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt


class ResultsTable(QTableWidget):
    """
    Table widget for displaying detection results.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        # Set up columns
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Filename", "Coverage %", "Area (µm²)"])

        # Configure table appearance
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setToolTip("Detection results for processed images")

    def add_result(self, filename: str, coverage_pct: float, area_um2: float = None):
        """
        Add a result row to the table.

        Args:
            filename: Image filename
            coverage_pct: Coverage percentage
            area_um2: Absolute area in µm² (None if uncalibrated)
        """
        row = self.rowCount()
        self.insertRow(row)

        # Filename
        filename_item = QTableWidgetItem(filename)
        self.setItem(row, 0, filename_item)

        # Coverage percentage
        coverage_item = QTableWidgetItem(f"{coverage_pct:.2f}")
        coverage_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(row, 1, coverage_item)

        # Area
        if area_um2 is not None and area_um2 > 0:
            area_item = QTableWidgetItem(f"{area_um2:.2f}")
        else:
            area_item = QTableWidgetItem("N/A")
        area_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(row, 2, area_item)

    def clear_results(self):
        """Clear all results from the table."""
        self.setRowCount(0)

    def get_result_count(self) -> int:
        """Get number of results in the table."""
        return self.rowCount()
