"""
Auto-detection algorithms for LAB layer classification thresholds.

Provides four algorithms to automatically detect T1 (mono/bi boundary) and
T2 (bi/tri boundary) thresholds from film pixel L-channel distributions.
"""

import cv2
import numpy as np
from typing import Tuple
from scipy import signal
from skimage.filters import threshold_multiotsu


def extract_film_l_values(binary_mask: np.ndarray, image: np.ndarray) -> np.ndarray:
    """
    Extract L-channel values from film pixels only.

    Helper function to avoid code duplication across algorithms.

    Args:
        binary_mask: V1 binary detection result (0=substrate, 1=film)
        image: Original BGR image

    Returns:
        1D array of L-channel values for film pixels only

    Raises:
        ValueError: If no film pixels found
    """
    # Convert to LAB and extract L-channel
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel = lab_image[:, :, 0]

    # Extract only film pixel L-values
    # Handle both 0/1 and 0/255 binary masks
    film_pixels = (binary_mask == 1) | (binary_mask == 255)
    l_values = l_channel[film_pixels]

    if len(l_values) == 0:
        raise ValueError("No film pixels found in binary_mask (check if mask is 0/1 or 0/255)")

    return l_values


def detect_thresholds_kmeans(
    binary_mask: np.ndarray,
    image: np.ndarray
) -> Tuple[int, int]:
    """
    Auto-detect T1, T2 using K-means clustering.

    Groups film pixel L-values into 3 clusters (mono, bi, tri) and calculates
    thresholds as midpoints between cluster centers.

    CRITICAL: Only analyzes pixels where binary_mask == 1.

    Args:
        binary_mask: V1 binary detection result (0=substrate, 1=film)
        image: Original BGR image

    Returns:
        Tuple of (t1, t2) where t1 is mono/bi boundary, t2 is bi/tri boundary

    Raises:
        ValueError: If no film pixels found or clustering fails
    """
    # Extract film L-values
    l_values = extract_film_l_values(binary_mask, image)

    # Prepare for K-means (needs float32, 2D array)
    l_flat = l_values.reshape(-1, 1).astype(np.float32)

    # K-means with 3 clusters (mono, bi, tri)
    # Substrate already excluded by binary_mask
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(
        l_flat,
        3,  # 3 clusters: mono, bi, tri
        None,
        criteria,
        10,  # Attempts
        cv2.KMEANS_PP_CENTERS
    )

    # Sort cluster centers in ascending order
    centers_sorted = np.sort(centers.flatten())

    # Thresholds are midpoints between cluster centers
    t1 = int((centers_sorted[0] + centers_sorted[1]) / 2)  # Mono/Bi boundary
    t2 = int((centers_sorted[1] + centers_sorted[2]) / 2)  # Bi/Tri boundary

    # Ensure valid range and ordering
    t1 = max(0, min(254, t1))
    t2 = max(t1 + 1, min(255, t2))

    return t1, t2


def detect_thresholds_percentile(
    binary_mask: np.ndarray,
    image: np.ndarray
) -> Tuple[int, int]:
    """
    Auto-detect T1, T2 using percentile-based thresholding.

    Uses 33rd and 66th percentiles to split film pixels into three equal groups.
    Simple and fast statistical approach.

    CRITICAL: Only analyzes pixels where binary_mask == 1.

    Args:
        binary_mask: V1 binary detection result (0=substrate, 1=film)
        image: Original BGR image

    Returns:
        Tuple of (t1, t2) where t1 is mono/bi boundary, t2 is bi/tri boundary

    Raises:
        ValueError: If no film pixels found
    """
    # Extract film L-values
    l_values = extract_film_l_values(binary_mask, image)

    # Calculate 33rd and 66th percentiles
    t1 = int(np.percentile(l_values, 33))
    t2 = int(np.percentile(l_values, 66))

    # Ensure valid range and ordering
    t1 = max(0, min(254, t1))
    t2 = max(t1 + 1, min(255, t2))

    return t1, t2


def detect_thresholds_histogram(
    binary_mask: np.ndarray,
    image: np.ndarray
) -> Tuple[int, int]:
    """
    Auto-detect T1, T2 using histogram peak detection.

    Finds peaks in L-channel histogram corresponding to mono/bi/tri layers
    and calculates thresholds as valleys between peaks.

    Best for images with distinct intensity modes.

    CRITICAL: Only analyzes pixels where binary_mask == 1.

    Args:
        binary_mask: V1 binary detection result (0=substrate, 1=film)
        image: Original BGR image

    Returns:
        Tuple of (t1, t2) where t1 is mono/bi boundary, t2 is bi/tri boundary

    Raises:
        ValueError: If no film pixels found or insufficient peaks
    """
    # Extract film L-values
    l_values = extract_film_l_values(binary_mask, image)

    # Compute histogram
    hist, bins = np.histogram(l_values, bins=256, range=(0, 255))

    # Smooth histogram to reduce noise
    hist_smooth = signal.savgol_filter(hist, window_length=11, polyorder=3)

    # Find peaks
    peaks, properties = signal.find_peaks(
        hist_smooth,
        prominence=np.max(hist_smooth) * 0.1  # Minimum 10% of max prominence
    )

    if len(peaks) < 2:
        # Fallback to percentile if insufficient peaks
        return detect_thresholds_percentile(binary_mask, image)

    # Sort peaks by L-value (ascending)
    peaks_sorted = np.sort(peaks)

    # If 2 peaks: assume mono and bi, extrapolate tri
    # If 3+ peaks: use first 3
    if len(peaks_sorted) == 2:
        t1 = int((peaks_sorted[0] + peaks_sorted[1]) / 2)
        # Extrapolate t2 assuming similar spacing
        spacing = peaks_sorted[1] - peaks_sorted[0]
        t2 = int(peaks_sorted[1] + spacing / 2)
    else:
        # Use valleys between first 3 peaks
        t1 = int((peaks_sorted[0] + peaks_sorted[1]) / 2)
        t2 = int((peaks_sorted[1] + peaks_sorted[2]) / 2)

    # Ensure valid range and ordering
    t1 = max(0, min(254, t1))
    t2 = max(t1 + 1, min(255, t2))

    return t1, t2


def detect_thresholds_otsu_multi(
    binary_mask: np.ndarray,
    image: np.ndarray
) -> Tuple[int, int]:
    """
    Auto-detect T1, T2 using Otsu's multi-threshold method.

    Applies multi-class Otsu's method to find optimal thresholds that maximize
    inter-class variance for 3 classes (mono, bi, tri).

    Mathematical optimization approach.

    CRITICAL: Only analyzes pixels where binary_mask == 1.

    Args:
        binary_mask: V1 binary detection result (0=substrate, 1=film)
        image: Original BGR image

    Returns:
        Tuple of (t1, t2) where t1 is mono/bi boundary, t2 is bi/tri boundary

    Raises:
        ValueError: If no film pixels found or Otsu fails
    """
    # Extract film L-values
    l_values = extract_film_l_values(binary_mask, image)

    try:
        # Apply multi-threshold Otsu (returns sorted thresholds)
        thresholds = threshold_multiotsu(l_values, classes=3)

        t1 = int(thresholds[0])
        t2 = int(thresholds[1])

        # Ensure valid range and ordering
        t1 = max(0, min(254, t1))
        t2 = max(t1 + 1, min(255, t2))

        return t1, t2

    except Exception:
        # Fallback to K-means if Otsu fails
        return detect_thresholds_kmeans(binary_mask, image)
