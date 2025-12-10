"""
Image processing pipeline for thin film coverage analysis.

Constitutional Algorithm Implementation:
1. Load image
2. Convert to grayscale
3. Apply Gaussian blur (noise reduction)
4. Apply threshold (Otsu or manual)
5. Apply morphological operations
6. Calculate coverage

Memory Optimization:
- All images maintained as uint8 (not float32/float64)
- 16-bit TIFFs normalized to uint8 on load
- OpenCV operations preserve uint8 dtype
- 3×3 tiling uses np.tile which maintains dtype
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image as PILImage
from .detection import (
    apply_threshold,
    apply_noise_reduction,
    apply_morphological_operations,
    calculate_coverage,
    calculate_otsu_threshold
)
from ..core.logger import get_logger


def load_image_with_fallback(image_path: str) -> np.ndarray:
    """
    Load image using OpenCV with PIL fallback for problematic formats.

    Args:
        image_path: Path to the image file

    Returns:
        Image as numpy array in BGR format

    Raises:
        ValueError: If image cannot be loaded
    """
    # Try OpenCV first
    img = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)

    if img is None:
        # Fallback to PIL for problematic TIFF files
        try:
            pil_image = PILImage.open(str(image_path))

            # Convert to RGB if needed
            if pil_image.mode not in ('RGB', 'L', 'RGBA'):
                pil_image = pil_image.convert('RGB')

            # Convert PIL image to numpy array
            img = np.array(pil_image)

            # Convert RGB to BGR (OpenCV format)
            if len(img.shape) == 3:
                if img.shape[2] == 3:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                elif img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

        except Exception as e:
            raise ValueError(f"Unable to load image with both OpenCV and PIL: {image_path}. Error: {str(e)}")

    if img is None:
        raise ValueError(f"Unable to load image: {image_path}")

    # Handle 16-bit images by normalizing to 8-bit
    if img.dtype == np.uint16:
        img = (img / 256).astype(np.uint8)

    # Ensure image is in BGR format for consistency
    if len(img.shape) == 2:
        # Grayscale - convert to BGR
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif len(img.shape) == 3 and img.shape[2] == 4:
        # RGBA - convert to BGR
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    return img


def process_image(
    image_path: str,
    threshold_value: Optional[int] = None,
    noise_reduction: bool = True,
    roi: Optional[Tuple[int, int, int, int]] = None,
    use_adaptive: bool = True,
    blur_kernel: int = 3,
    morph_close_kernel: int = 2,
    morph_open_kernel: int = 2,
    adaptive_block_size: int = 200,
    adaptive_c: int = 5
) -> Tuple[np.ndarray, float]:
    """
    Process a single image to detect thin film coverage.

    Implements the constitutional algorithm:
    Grayscale → Gaussian blur → Threshold → Morphological ops → Coverage calculation

    Args:
        image_path: Path to the image file
        threshold_value: Manual threshold (0-255). If None, uses Otsu's/adaptive method
        noise_reduction: Whether to apply Gaussian blur preprocessing
        roi: Optional ROI coordinates (x, y, width, height)
        use_adaptive: Use adaptive threshold instead of Otsu (better for uneven illumination)
        blur_kernel: Gaussian blur kernel size (odd number, 1-15)
        morph_close_kernel: Morphological close kernel size (0 = disabled)
        morph_open_kernel: Morphological open kernel size (0 = disabled)
        adaptive_block_size: Adaptive threshold block size (odd number)
        adaptive_c: Adaptive threshold constant (higher = less sensitive)

    Returns:
        Tuple of (binary_mask, coverage_percentage)

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image cannot be loaded or is invalid
    """
    logger = get_logger()

    # Validate file exists
    if not Path(image_path).exists():
        error_msg = f"Image file not found: {image_path}"
        logger.log_error("FileNotFoundError", error_msg, context_info=str(image_path))
        raise FileNotFoundError(error_msg)

    # Load image
    try:
        img = load_image_with_fallback(image_path)
    except Exception as e:
        logger.log_error(
            "ImageLoadError",
            str(e),
            context_info=str(image_path),
            stack_trace=str(e.__traceback__)
        )
        raise

    # Convert to grayscale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # Apply noise reduction with configurable kernel size
    if noise_reduction and blur_kernel > 0:
        # Ensure kernel is odd
        if blur_kernel % 2 == 0:
            blur_kernel += 1
        gray = apply_noise_reduction(gray, kernel_size=blur_kernel)

    # Apply threshold
    if use_adaptive:
        method = "adaptive"
        threshold_value = None  # Adaptive doesn't use manual threshold
    else:
        method = "manual" if threshold_value is not None else "otsu"

    # Apply threshold
    # Disable auto-inversion - flakes are always brighter than substrate
    binary_mask = apply_threshold(
        gray, threshold_value, method, auto_invert=False,
        adaptive_block_size=adaptive_block_size, adaptive_c=adaptive_c
    )

    # Apply morphological operations with configurable kernel sizes
    if morph_close_kernel > 0:
        binary_mask = apply_morphological_operations(binary_mask, operation="close", kernel_size=morph_close_kernel)
    if morph_open_kernel > 0:
        binary_mask = apply_morphological_operations(binary_mask, operation="open", kernel_size=morph_open_kernel)

    # Calculate coverage
    coverage_percentage, _, _ = calculate_coverage(binary_mask, roi)

    return binary_mask, coverage_percentage


def load_image_metadata(image_path: str) -> Tuple[Tuple[int, int], str]:
    """
    Load image metadata without full processing.

    Args:
        image_path: Path to the image file

    Returns:
        Tuple of (dimensions, format)
        - dimensions: (width, height)
        - format: File extension (e.g., "PNG", "JPG")
    """
    img = load_image_with_fallback(image_path)
    height, width = img.shape[:2]
    format_ext = Path(image_path).suffix.upper().lstrip('.')

    return (width, height), format_ext
