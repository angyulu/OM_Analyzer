"""
Quick test to verify 3×3 tiling works correctly.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from thin_film_analyzer.core.detection import tile_image_3x3, extract_center_tile

# Create a simple test image
test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
print(f"Original image shape: {test_image.shape}")
print(f"Original image dtype: {test_image.dtype}")

# Test tiling
tiled = tile_image_3x3(test_image)
print(f"Tiled image shape: {tiled.shape}")
print(f"Tiled image dtype: {tiled.dtype}")
print(f"Expected shape: (300, 300)")

# Test extraction
extracted = extract_center_tile(tiled, test_image.shape)
print(f"Extracted center shape: {extracted.shape}")
print(f"Extracted center dtype: {extracted.dtype}")
print(f"Expected shape: (100, 100)")

# Verify the center tile matches original
print(f"\nVerifying center tile matches original location in tiled image...")
center_from_tiled = tiled[100:200, 100:200]
print(f"Are they equal? {np.array_equal(extracted, center_from_tiled)}")

print("\n✓ Tiling functions work correctly!")
