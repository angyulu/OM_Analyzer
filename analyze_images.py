"""
Diagnostic script to analyze test images and understand detection issues.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import cv2
import numpy as np
from thin_film_analyzer.core.processor import load_image_with_fallback
from thin_film_analyzer.core.detection import calculate_otsu_threshold, apply_noise_reduction

def analyze_image(image_path):
    """Analyze an image and print diagnostic information."""
    print(f"\n{'='*60}")
    print(f"Analyzing: {Path(image_path).name}")
    print(f"{'='*60}")

    # Load image
    img = load_image_with_fallback(image_path)
    print(f"Image shape: {img.shape}")
    print(f"Image dtype: {img.dtype}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Calculate statistics
    print(f"\nGrayscale statistics:")
    print(f"  Min: {gray.min()}")
    print(f"  Max: {gray.max()}")
    print(f"  Mean: {gray.mean():.2f}")
    print(f"  Median: {np.median(gray):.2f}")
    print(f"  Std: {gray.std():.2f}")

    # Calculate histogram
    hist, bins = np.histogram(gray.flatten(), bins=256, range=[0, 256])
    print(f"\nIntensity distribution:")
    print(f"  Pixels 0-63 (dark): {hist[0:64].sum()} ({100*hist[0:64].sum()/gray.size:.1f}%)")
    print(f"  Pixels 64-127 (mid-dark): {hist[64:128].sum()} ({100*hist[64:128].sum()/gray.size:.1f}%)")
    print(f"  Pixels 128-191 (mid-bright): {hist[128:192].sum()} ({100*hist[128:192].sum()/gray.size:.1f}%)")
    print(f"  Pixels 192-255 (bright): {hist[192:256].sum()} ({100*hist[192:256].sum()/gray.size:.1f}%)")

    # Test with noise reduction
    gray_blurred = apply_noise_reduction(gray, kernel_size=5)

    # Calculate Otsu threshold
    threshold_original = calculate_otsu_threshold(gray)
    threshold_blurred = calculate_otsu_threshold(gray_blurred)

    print(f"\nOtsu thresholds:")
    print(f"  Original image: {threshold_original}")
    print(f"  After noise reduction: {threshold_blurred}")

    # Apply threshold and calculate coverage
    _, binary_original = cv2.threshold(gray, threshold_original, 255, cv2.THRESH_BINARY)
    _, binary_blurred = cv2.threshold(gray_blurred, threshold_blurred, 255, cv2.THRESH_BINARY)

    coverage_original = (np.count_nonzero(binary_original) / binary_original.size) * 100
    coverage_blurred = (np.count_nonzero(binary_blurred) / binary_blurred.size) * 100

    print(f"\nCoverage percentages:")
    print(f"  Original threshold: {coverage_original:.2f}%")
    print(f"  Blurred threshold: {coverage_blurred:.2f}%")

    # Check for vignetting (darker edges)
    h, w = gray.shape
    center_region = gray[h//4:3*h//4, w//4:3*w//4]
    edge_top = gray[0:h//8, :]
    edge_bottom = gray[7*h//8:h, :]
    edge_left = gray[:, 0:w//8]
    edge_right = gray[:, 7*w//8:w]

    print(f"\nEdge vs Center brightness:")
    print(f"  Center mean: {center_region.mean():.2f}")
    print(f"  Top edge mean: {edge_top.mean():.2f}")
    print(f"  Bottom edge mean: {edge_bottom.mean():.2f}")
    print(f"  Left edge mean: {edge_left.mean():.2f}")
    print(f"  Right edge mean: {edge_right.mean():.2f}")

if __name__ == "__main__":
    # Analyze both test images
    img1 = "C:/Users/Ang-Yu Lu/python_virtual/platform/OM_Analyzer/OM_V0/thin_film_analyzer/tests/Images/OMVA1P01250400401.tif"
    img2 = "C:/Users/Ang-Yu Lu/python_virtual/platform/OM_Analyzer/OM_V0/thin_film_analyzer/tests/Images/OMVA1P01250400403.tif"

    analyze_image(img1)
    analyze_image(img2)
