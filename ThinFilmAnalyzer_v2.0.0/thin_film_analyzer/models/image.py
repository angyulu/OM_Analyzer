"""
Image entity representing a loaded optical microscope image.
"""

from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Tuple, Optional


class ImageStatus(Enum):
    """Processing status of an image."""
    UNPROCESSED = "unprocessed"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class Image:
    """
    Represents a loaded optical microscope image file.

    Attributes:
        filename: Name of the image file
        file_path: Absolute path to the image file
        dimensions: Width x height in pixels (width, height)
        format: File format (PNG/JPG/TIFF/BMP)
        status: Current processing status
    """
    filename: str
    file_path: Path
    dimensions: Tuple[int, int]  # (width, height)
    format: str
    status: ImageStatus = ImageStatus.UNPROCESSED

    def __post_init__(self):
        """Validate image data after initialization."""
        if not isinstance(self.file_path, Path):
            self.file_path = Path(self.file_path)

        if self.dimensions[0] <= 0 or self.dimensions[1] <= 0:
            raise ValueError(f"Invalid image dimensions: {self.dimensions}")

        if not isinstance(self.status, ImageStatus):
            raise TypeError(f"status must be ImageStatus enum, got {type(self.status)}")

    @property
    def width(self) -> int:
        """Get image width in pixels."""
        return self.dimensions[0]

    @property
    def height(self) -> int:
        """Get image height in pixels."""
        return self.dimensions[1]

    @property
    def total_pixels(self) -> int:
        """Get total number of pixels in the image."""
        return self.dimensions[0] * self.dimensions[1]
