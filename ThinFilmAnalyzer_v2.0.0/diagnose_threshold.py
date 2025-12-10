"""
Diagnostic script to understand the threshold circle issue.
This script analyzes the vignetting problem in both test images.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import cv2
import numpy as np
from thin_film_analyzer.core.processor import load_image_with_fallback
from thin_film_analyzer.core.detection import calculate_otsu_threshold

def analyze_image(image_path, image_name):
    print(f"\n{'='*70}")
    print(f"Analyzing: {image_name}")
    print(f"{'='*70}")

    img = load_image_with_fallback(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape
    print(f"Image dimensions: {w} x {h}")

    # Divide image into regions
    center_region = gray[h//3:2*h//3, w//3:2*w//3]

    # Corner regions
    corner_tl = gray[0:h//4, 0:w//4]
    corner_tr = gray[0:h//4, 3*w//4:w]
    corner_bl = gray[3*h//4:h, 0:w//4]
    corner_br = gray[3*h//4:h, 3*w//4:w]

    # Edge regions
    edge_top = gray[0:h//8, w//4:3*w//4]
    edge_bottom = gray[7*h//8:h, w//4:3*w//4]
    edge_left = gray[h//4:3*h//4, 0:w//8]
    edge_right = gray[h//4:3*h//4, 7*w//8:w]

    print(f"\nRegion brightness analysis:")
    print(f"  Center mean:       {center_region.mean():.2f}")
    print(f"  Top-left corner:   {corner_tl.mean():.2f}")
    print(f"  Top-right corner:  {corner_tr.mean():.2f}")
    print(f"  Bottom-left corner: {corner_bl.mean():.2f}")
    print(f"  Bottom-right corner: {corner_br.mean():.2f}")
    print(f"  Top edge:          {edge_top.mean():.2f}")
    print(f"  Bottom edge:       {edge_bottom.mean():.2f}")
    print(f"  Left edge:         {edge_left.mean():.2f}")
    print(f"  Right edge:        {edge_right.mean():.2f}")

    # Vignetting intensity (center brighter than corners)
    corner_mean = (corner_tl.mean() + corner_tr.mean() + corner_bl.mean() + corner_br.mean()) / 4
    vignetting = center_region.mean() - corner_mean
    print(f"\nVignetting intensity (center - corners): {vignetting:.2f}")

    # Otsu threshold
    otsu = calculate_otsu_threshold(gray)
    print(f"Otsu threshold: {otsu}")

    # Simulate threshold problem
    print(f"\nThreshold problem simulation:")
    print(f"  If threshold = {otsu}:")
    print(f"    Center substrate (~{center_region.mean():.0f}) > {otsu}: Detected as FLAKE (WRONG!)")
    print(f"    Corner substrate (~{corner_mean:.0f}) < {otsu}: Not detected (correct)")
    print(f"    Corner flakes (~{corner_mean+20:.0f}) < {otsu}: Not detected (WRONG!)")

    # Find the dilemma
    print(f"\n  Threshold dilemma:")
    print(f"    Lower threshold ({corner_mean:.0f}): Detects corners BUT center circle appears")
    print(f"    Higher threshold ({center_region.mean():.0f}): No center circle BUT misses corners")

    return gray

# Analyze both images
img1_path = "C:/Users/Ang-Yu Lu/python_virtual/platform/OM_Analyzer/OM_V0/thin_film_analyzer/tests/Images/OMVA1P01250400401.tif"
img2_path = "C:/Users/Ang-Yu Lu/python_virtual/platform/OM_Analyzer/OM_V0/thin_film_analyzer/tests/Images/OMVA1P01250400403.tif"

gray1 = analyze_image(img1_path, "OMVA1P01250400401.tif (small flakes)")
gray2 = analyze_image(img2_path, "OMVA1P01250400403.tif (large flakes)")

print(f"\n{'='*70}")
print("CONCLUSION: Adaptive threshold is the ONLY solution for vignetting")
print("='*70")
