"""
Overlay generation and blending for visual verification.

Generates colored overlays on original images to show detected thin film regions.
"""

import cv2
import numpy as np
from typing import Tuple


def generate_overlay(
    original_image: np.ndarray,
    binary_mask: np.ndarray,
    opacity: float = 0.5,
    color: Tuple[int, int, int] = (255, 0, 0)
) -> np.ndarray:
    """
    Generate overlay image with detected regions highlighted.

    Args:
        original_image: Original RGB/BGR image
        binary_mask: Binary mask (255 = film, 0 = substrate)
        opacity: Overlay transparency (0.0 = transparent, 1.0 = opaque)
        color: Overlay color in BGR format (default: red)

    Returns:
        RGB image with overlay applied
    """
    if original_image is None or binary_mask is None:
        raise ValueError("original_image and binary_mask cannot be None")

    if not (0.0 <= opacity <= 1.0):
        raise ValueError(f"Opacity must be 0.0-1.0, got {opacity}")

    # Ensure original image is 3-channel BGR
    if len(original_image.shape) == 2:
        # Convert grayscale to BGR
        original_bgr = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
    else:
        original_bgr = original_image.copy()

    # Ensure binary mask matches image dimensions
    if original_bgr.shape[:2] != binary_mask.shape[:2]:
        raise ValueError(
            f"Image and mask dimensions must match: "
            f"image {original_bgr.shape[:2]} vs mask {binary_mask.shape[:2]}"
        )

    # Create colored overlay
    overlay = np.zeros_like(original_bgr)
    overlay[binary_mask == 255] = color

    # Blend original image with overlay using alpha blending
    blended = cv2.addWeighted(original_bgr, 1.0, overlay, opacity, 0)

    return blended


def toggle_overlay(
    original_image: np.ndarray,
    overlay_image: np.ndarray,
    show_overlay: bool
) -> np.ndarray:
    """
    Toggle between original image and overlay image.

    Args:
        original_image: Original image without overlay
        overlay_image: Image with overlay applied
        show_overlay: If True, return overlay_image; else return original_image

    Returns:
        Image to display
    """
    return overlay_image if show_overlay else original_image


def update_overlay_opacity(
    original_image: np.ndarray,
    binary_mask: np.ndarray,
    opacity: float,
    color: Tuple[int, int, int] = (255, 0, 0)
) -> np.ndarray:
    """
    Update overlay with new opacity value (for real-time slider updates).

    Args:
        original_image: Original image
        binary_mask: Binary detection mask
        opacity: New opacity value (0.0-1.0)
        color: Overlay color

    Returns:
        New overlay image with updated opacity
    """
    return generate_overlay(original_image, binary_mask, opacity, color)
