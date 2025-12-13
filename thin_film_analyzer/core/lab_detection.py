"""
LAB color space layer detection for thin film thickness classification.

This module provides layer classification (monolayer, bilayer, trilayer) based on
LAB color space L-channel (lightness) analysis. Works in conjunction with V1
adaptive threshold detection to classify film pixels by thickness.
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Optional


def apply_vignetting_correction(
    l_channel: np.ndarray,
    binary_mask: np.ndarray
) -> np.ndarray:
    """
    Apply vignetting correction to L-channel for film pixels only.

    Uses local normalization to reduce edge darkening effects (vignetting)
    that can cause misclassification of edge flakes as thinner layers.

    Args:
        l_channel: LAB L-channel (lightness) image (uint8, 0-255)
        binary_mask: V1 binary detection result (0=substrate, 1=film)

    Returns:
        Corrected L-channel with vignetting removed (uint8, 0-255)
    """
    # Calculate local mean using large Gaussian blur
    local_mean = cv2.GaussianBlur(l_channel, (101, 101), 30)

    # Calculate global mean (only for film pixels to avoid substrate bias)
    # Handle both 0/1 and 0/255 binary masks
    film_mask = (binary_mask == 1) | (binary_mask == 255)
    film_pixels = l_channel[film_mask]
    if len(film_pixels) == 0:
        return l_channel  # No film pixels, return unchanged

    global_mean = np.mean(film_pixels)

    # Normalize: L_corrected = L * (global_mean / local_mean)
    # Add small epsilon to avoid division by zero
    l_corrected = l_channel.astype(np.float32) * (global_mean / (local_mean.astype(np.float32) + 1e-6))

    # Clip to valid range and convert back to uint8
    l_corrected = np.clip(l_corrected, 0, 255).astype(np.uint8)

    return l_corrected


def detect_lab_layers(
    binary_mask: np.ndarray,
    image: np.ndarray,
    t1: int,
    t2: int,
    apply_vignetting_correction_flag: bool = True
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Detect monolayer, bilayer, trilayer regions using LAB L-channel analysis.

    CRITICAL: Only analyzes pixels where binary_mask == 1 (V1 detected film).
    Substrate pixels (binary_mask == 0) remain 0 in output layer_mask.

    Args:
        binary_mask: V1 binary detection result (0=substrate, 1=film)
        image: Original BGR image (from cv2.imread or similar)
        t1: Threshold between monolayer and bilayer (0-255)
        t2: Threshold between bilayer and trilayer (0-255)
        apply_vignetting_correction_flag: Apply vignetting correction to L-channel

    Returns:
        layer_mask: np.ndarray with values {0: substrate, 1: mono, 2: bi, 3: tri}
                    Substrate pixels (binary_mask==0) are 0
        stats: Dictionary containing:
            'total_coverage': float (% from V1 binary mask)
            'mono_coverage': float (% monolayer)
            'bi_coverage': float (% bilayer)
            'tri_coverage': float (% trilayer)

    Raises:
        ValueError: If t1 >= t2 or values out of range [0, 255]
    """
    # Validation
    if not (0 <= t1 <= 255 and 0 <= t2 <= 255):
        raise ValueError(f"Thresholds must be in range [0, 255], got t1={t1}, t2={t2}")

    if t1 >= t2:
        raise ValueError(f"T1 must be less than T2, got t1={t1}, t2={t2}")

    if binary_mask.shape[:2] != image.shape[:2]:
        raise ValueError(
            f"binary_mask shape {binary_mask.shape[:2]} != image shape {image.shape[:2]}"
        )

    # Convert image to LAB color space
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel = lab_image[:, :, 0]  # Extract L-channel (lightness)

    # Apply vignetting correction if requested
    if apply_vignetting_correction_flag:
        l_channel = apply_vignetting_correction(l_channel, binary_mask)

    # Initialize layer_mask (all substrate by default)
    layer_mask = np.zeros_like(binary_mask, dtype=np.uint8)

    # CRITICAL: Only classify film pixels (where binary_mask == 255 or == 1)
    # Note: binary_mask can be either 0/1 or 0/255 depending on source
    film_pixels = (binary_mask == 1) | (binary_mask == 255)

    # Extract L-values for film pixels
    l_values = l_channel[film_pixels]

    # Three-way classification based on T1, T2
    # Monolayer: L < T1
    mono_pixels = l_values < t1
    # Bilayer: T1 <= L < T2
    bi_pixels = (l_values >= t1) & (l_values < t2)
    # Trilayer: L >= T2
    tri_pixels = l_values >= t2

    # Create temporary mask for layer classification
    temp_mask = np.zeros_like(l_values, dtype=np.uint8)
    temp_mask[mono_pixels] = 1
    temp_mask[bi_pixels] = 2
    temp_mask[tri_pixels] = 3

    # Assign classified values back to layer_mask (only for film pixels)
    layer_mask[film_pixels] = temp_mask

    # Calculate per-layer coverage statistics
    total_pixels = binary_mask.size
    # Handle both 0/1 and 0/255 binary masks
    total_coverage = np.sum(film_pixels) / total_pixels * 100.0
    mono_coverage = np.sum(layer_mask == 1) / total_pixels * 100.0
    bi_coverage = np.sum(layer_mask == 2) / total_pixels * 100.0
    tri_coverage = np.sum(layer_mask == 3) / total_pixels * 100.0

    stats = {
        'total_coverage': round(total_coverage, 2),
        'mono_coverage': round(mono_coverage, 2),
        'bi_coverage': round(bi_coverage, 2),
        'tri_coverage': round(tri_coverage, 2)
    }

    return layer_mask, stats
