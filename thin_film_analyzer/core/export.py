"""
Results export functionality for CSV and images with overlay.
"""

import csv
import cv2
from pathlib import Path
from typing import List, Optional
from ..models.detection_result import DetectionResult
from ..models.batch_session import BatchStatistics


class ResultsExporter:
    """
    Manages export of detection results to CSV and images.
    """

    def __init__(self):
        """Initialize results exporter."""
        self.results: List[dict] = []

    def add_result(
        self,
        filename: str,
        coverage_pct: float,
        area_um2: Optional[float] = None
    ) -> None:
        """
        Add a result to the export queue.

        Args:
            filename: Image filename
            coverage_pct: Coverage percentage
            area_um2: Absolute area in µm² (None if uncalibrated)
        """
        result_dict = {
            "filename": filename,
            "coverage_percentage": round(coverage_pct, 2)
        }

        if area_um2 is not None and area_um2 > 0:
            result_dict["area_um2"] = round(area_um2, 2)
        else:
            result_dict["area_um2"] = None

        self.results.append(result_dict)

    def export_csv(
        self,
        output_path: Path,
        include_summary: bool = True,
        summary_stats: Optional[BatchStatistics] = None
    ) -> None:
        """
        Export results to CSV file with optional summary statistics.

        Args:
            output_path: Path where CSV file should be saved
            include_summary: Whether to include summary statistics footer
            summary_stats: BatchStatistics object for summary row
        """
        if not self.results:
            raise ValueError("No results to export")

        # Determine if area column should be included
        has_area = any(r["area_um2"] is not None for r in self.results)

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Define fieldnames
            if has_area:
                fieldnames = ["filename", "coverage_percentage", "area_um2"]
            else:
                fieldnames = ["filename", "coverage_percentage"]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Write data rows
            for result in self.results:
                row_data = {k: v for k, v in result.items() if k in fieldnames}
                writer.writerow(row_data)

            # Write summary statistics if requested
            if include_summary and summary_stats:
                # Add blank row
                csvfile.write("\n")

                # Write summary header
                csvfile.write("SUMMARY STATISTICS\n")

                # Write statistics
                csvfile.write(f"Mean Coverage (%),{summary_stats.mean_coverage:.2f}\n")
                csvfile.write(f"Std Dev Coverage (%),{summary_stats.std_dev_coverage:.2f}\n")
                csvfile.write(f"Min Coverage (%),{summary_stats.min_coverage:.2f}\n")
                csvfile.write(f"Max Coverage (%),{summary_stats.max_coverage:.2f}\n")

                if has_area and summary_stats.mean_area is not None:
                    csvfile.write(f"Mean Area (µm²),{summary_stats.mean_area:.2f}\n")
                    csvfile.write(f"Std Dev Area (µm²),{summary_stats.std_dev_area:.2f}\n")
                    csvfile.write(f"Min Area (µm²),{summary_stats.min_area:.2f}\n")
                    csvfile.write(f"Max Area (µm²),{summary_stats.max_area:.2f}\n")

    def export_images_with_overlay(
        self,
        results: List[DetectionResult],
        overlay_images: List,
        output_dir: Path
    ) -> None:
        """
        Export processed images with overlay visible.

        Args:
            results: List of DetectionResult objects
            overlay_images: List of overlay images (numpy arrays)
            output_dir: Directory where images should be saved
        """
        if len(results) != len(overlay_images):
            raise ValueError("Number of results and overlay images must match")

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        for result, overlay_img in zip(results, overlay_images):
            # Generate output filename
            original_name = Path(result.image_ref.filename).stem
            output_filename = f"{original_name}_overlay.png"
            output_path = output_dir / output_filename

            # Save overlay image
            cv2.imwrite(str(output_path), overlay_img)

    def clear(self) -> None:
        """Clear all results from the exporter."""
        self.results.clear()

    @property
    def result_count(self) -> int:
        """Get number of results ready for export."""
        return len(self.results)
