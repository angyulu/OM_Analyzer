"""
Thin film detection algorithms using threshold-based segmentation.

Constitutional Algorithm:
Grayscale → Gaussian blur → Otsu/Adaptive threshold → Morphological operations → Coverage calculation
"""

import cv2
import numpy as np
from typing import Tuple, Optional


def detect_flake_brightness(grayscale_image: np.ndarray) -> str:
    """
    Detect whether flakes are brighter or darker than substrate.

    Args:
        grayscale_image: Input grayscale image

    Returns:
        "bright" if flakes are brighter, "dark" if flakes are darker
    """
    # Calculate Otsu threshold
    threshold_value, _ = cv2.threshold(
        grayscale_image,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Check which pixels are in minority
    # Flakes are typically the minority class
    _, binary = cv2.threshold(grayscale_image, threshold_value, 255, cv2.THRESH_BINARY)
    bright_pixels = np.count_nonzero(binary)
    total_pixels = binary.size

    # If less than 50% of pixels are white, flakes are bright
    # Otherwise, flakes are dark (need inverse)
    if bright_pixels < total_pixels / 2:
        return "bright"
    else:
        return "dark"


def calculate_otsu_threshold(grayscale_image: np.ndarray) -> int:
    """
    Calculate optimal threshold value using Otsu's method.

    Args:
        grayscale_image: Input grayscale image

    Returns:
        Optimal threshold value (0-255)
    """
    threshold_value, _ = cv2.threshold(
        grayscale_image,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return int(threshold_value)


def calculate_adaptive_c_auto(grayscale_image: np.ndarray, block_size: int = 101) -> int:
    """
    Automatically calculate optimal C value for adaptive threshold.

    This finds the brightness difference between substrate and thinnest flakes
    by analyzing the local difference histogram.

    Args:
        grayscale_image: Input grayscale image
        block_size: Size of local neighborhood (must be odd)

    Returns:
        Optimal C value (typically 2-20)
    """
    if block_size % 2 == 0:
        block_size += 1

    # Calculate local mean
    local_mean = cv2.GaussianBlur(grayscale_image, (block_size, block_size), 0)

    # Calculate difference image
    diff = grayscale_image.astype(np.int16) - local_mean.astype(np.int16)

    # Analyze histogram of differences
    # Substrate should be centered around 0, flakes will be positive
    hist, bins = np.histogram(diff, bins=256, range=(-128, 127))

    # Find the substrate peak (should be near 0)
    center_idx = 128  # Index corresponding to diff=0
    substrate_peak_idx = center_idx + np.argmax(hist[center_idx-10:center_idx+10]) - 10

    # Find the first significant valley after substrate peak (transition to flakes)
    # Look in the positive difference range (brighter than substrate)
    for i in range(substrate_peak_idx + 5, min(substrate_peak_idx + 50, 256)):
        # Check if we found a local minimum followed by an increase
        if i < 254 and hist[i] < hist[i-1] and hist[i] < hist[i+1]:
            # Valley found - this is the substrate-flake boundary
            optimal_c = bins[i] + 2  # Add small margin
            return max(2, min(20, int(optimal_c)))  # Clamp to reasonable range

    # If no clear valley found, use statistical approach
    # Use mean + 2*std of positive differences as threshold
    positive_diffs = diff[diff > 0]
    if len(positive_diffs) > 0:
        optimal_c = int(np.percentile(positive_diffs, 10))  # 10th percentile of positive diffs
        return max(2, min(20, optimal_c))

    # Default fallback
    return 5


def apply_threshold(
    grayscale_image: np.ndarray,
    threshold_value: Optional[int] = None,
    method: str = "otsu",
    auto_invert: bool = True,
    adaptive_block_size: int = 101,
    adaptive_c: int = 15
) -> np.ndarray:
    """
    Apply thresholding to detect thin film regions.

    Constitutional algorithm implementation:
    - Otsu's method for automatic threshold detection
    - Manual threshold for user adjustment
    - Adaptive threshold for varying illumination
    - Auto-inversion to detect dark or bright flakes

    Args:
        grayscale_image: Input grayscale image (single channel)
        threshold_value: Manual threshold (0-255). If None, uses automatic method
        method: Threshold method ("otsu", "manual", "adaptive")
        auto_invert: Automatically detect if flakes are darker than substrate

    Returns:
        Binary mask where white (255) = thin film, black (0) = substrate
    """
    if grayscale_image is None or len(grayscale_image.shape) != 2:
        raise ValueError("Input must be a grayscale image (2D array)")

    # Detect if flakes are dark (need inverse threshold)
    use_inverse = False
    if auto_invert and method != "adaptive":
        flake_type = detect_flake_brightness(grayscale_image)
        use_inverse = (flake_type == "dark")

    if method == "otsu" or (method == "manual" and threshold_value is None):
        # Otsu's method - automatic threshold selection
        thresh_type = cv2.THRESH_BINARY_INV if use_inverse else cv2.THRESH_BINARY
        _, binary_mask = cv2.threshold(
            grayscale_image,
            0,
            255,
            thresh_type + cv2.THRESH_OTSU
        )
    elif method == "manual":
        # Manual threshold
        if not (0 <= threshold_value <= 255):
            raise ValueError(f"Threshold value must be 0-255, got {threshold_value}")
        thresh_type = cv2.THRESH_BINARY_INV if use_inverse else cv2.THRESH_BINARY
        _, binary_mask = cv2.threshold(
            grayscale_image,
            threshold_value,
            255,
            thresh_type
        )
    elif method == "adaptive":
        # Adaptive threshold for varying illumination - better for vignetting
        # For thin films with varying thickness:
        # - Substrate: uniform brightness in local region
        # - Thin flakes: slightly brighter than substrate (first peak after substrate)
        # - Thick flakes: much brighter than substrate
        # We need to find the LOCAL threshold between substrate and thinnest flakes

        # Ensure block size is odd
        if adaptive_block_size % 2 == 0:
            adaptive_block_size += 1

        # Calculate local mean (removes vignetting effect)
        local_mean = cv2.GaussianBlur(grayscale_image, (adaptive_block_size, adaptive_block_size), 0)

        # Calculate local difference image
        # This normalizes for background variation - flakes will be positive values
        diff = grayscale_image.astype(np.int16) - local_mean.astype(np.int16)

        # adaptive_c now represents the minimum brightness difference for thinnest detectable flakes
        # Lower C = detect thinner flakes (more sensitive)
        # Higher C = only detect thicker flakes (less sensitive)
        binary_mask = np.zeros_like(grayscale_image)
        binary_mask[diff > adaptive_c] = 255
    else:
        raise ValueError(f"Unknown threshold method: {method}")

    return binary_mask


def apply_noise_reduction(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    Apply Gaussian blur for noise reduction preprocessing.

    Part of constitutional algorithm - reduces noise before thresholding.

    Args:
        image: Input grayscale image
        kernel_size: Size of Gaussian kernel (must be odd)

    Returns:
        Blurred image
    """
    if kernel_size % 2 == 0:
        raise ValueError("Kernel size must be odd")

    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def apply_morphological_operations(
    binary_mask: np.ndarray,
    operation: str = "close",
    kernel_size: int = 3
) -> np.ndarray:
    """
    Apply morphological operations to clean up binary mask.

    Part of constitutional algorithm - removes small holes and noise.

    Args:
        binary_mask: Input binary mask
        operation: Morphological operation ("close", "open", "dilate", "erode")
        kernel_size: Size of morphological kernel

    Returns:
        Processed binary mask
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))

    if operation == "close":
        # Close small holes in detected regions
        result = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
    elif operation == "open":
        # Remove small noise pixels
        result = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
    elif operation == "dilate":
        result = cv2.dilate(binary_mask, kernel)
    elif operation == "erode":
        result = cv2.erode(binary_mask, kernel)
    else:
        raise ValueError(f"Unknown morphological operation: {operation}")

    return result


def calculate_coverage(
    binary_mask: np.ndarray,
    roi_coords: Optional[Tuple[int, int, int, int]] = None
) -> Tuple[float, int, int]:
    """
    Calculate thin film coverage percentage from binary mask.

    Args:
        binary_mask: Binary mask where 255 = film, 0 = substrate
        roi_coords: Optional ROI (x, y, width, height) to restrict calculation

    Returns:
        Tuple of (coverage_percentage, film_pixel_count, total_pixel_count)
    """
    # Apply ROI if specified
    if roi_coords is not None:
        x, y, w, h = roi_coords
        mask_roi = binary_mask[y:y+h, x:x+w]
    else:
        mask_roi = binary_mask

    # Count white pixels (thin film regions)
    film_pixel_count = np.count_nonzero(mask_roi)
    total_pixel_count = mask_roi.size

    # Calculate percentage
    coverage_percentage = (film_pixel_count / total_pixel_count) * 100.0

    return coverage_percentage, film_pixel_count, total_pixel_count
