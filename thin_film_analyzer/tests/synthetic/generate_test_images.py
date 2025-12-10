"""
Generate synthetic test images with known coverage percentages.

Creates test images with 25%, 50%, and 75% thin film coverage for validation.
"""

import cv2
import numpy as np
from pathlib import Path


def generate_synthetic_image(
    coverage_percentage: float,
    image_size: tuple = (2048, 2048),
    output_path: Path = None
) -> np.ndarray:
    """
    Generate a synthetic image with known thin film coverage.

    Args:
        coverage_percentage: Target coverage percentage (0-100)
        image_size: Image dimensions (width, height)
        output_path: Path to save the image (optional)

    Returns:
        Generated image as numpy array
    """
    width, height = image_size
    total_pixels = width * height

    # Create base substrate (dark background)
    substrate_value = 50  # Dark gray
    film_value = 200  # Light gray

    # Create image with substrate
    image = np.full((height, width), substrate_value, dtype=np.uint8)

    # Calculate number of pixels for thin film
    film_pixels_needed = int((coverage_percentage / 100.0) * total_pixels)

    # Create random pattern of thin film regions
    # Generate random positions for film pixels
    total_positions = width * height
    film_positions = np.random.choice(total_positions, film_pixels_needed, replace=False)

    # Convert linear positions to 2D coordinates
    film_y = film_positions // width
    film_x = film_positions % width

    # Set film pixels
    image[film_y, film_x] = film_value

    # Apply Gaussian blur to make it more realistic
    image = cv2.GaussianBlur(image, (5, 5), 0)

    # Add some noise for realism
    noise = np.random.normal(0, 10, image.shape).astype(np.int16)
    image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Save if output path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), image)
        print(f"Generated synthetic image: {output_path} ({coverage_percentage}% coverage)")

    return image


def generate_test_suite():
    """Generate a complete suite of test images with known coverage."""
    output_dir = Path(__file__).parent

    # Generate images with different coverage percentages
    coverages = [25.0, 50.0, 75.0]

    for coverage in coverages:
        filename = f"coverage_{int(coverage)}pct.png"
        output_path = output_dir / filename
        generate_synthetic_image(coverage, output_path=output_path)

    print(f"\nGenerated {len(coverages)} synthetic test images in {output_dir}")
    print("Use these images to validate detection accuracy.")


if __name__ == "__main__":
    generate_test_suite()
