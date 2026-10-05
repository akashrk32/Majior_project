"""
SHILORA - Gentle Glyph Boundary Sharpening
Implements controlled unsharp masking to subtly clarify authentic inscription boundaries
without generating artificial halo rings or pixel fracture artifacts.
"""

import cv2
import numpy as np


def gentle_unsharp_mask(
    image: np.ndarray,
    sigma: float = 1.1,
    amount: float = 0.45
) -> np.ndarray:
    """
    Applies gentle unsharp masking:
        output = image * (1.0 + amount) - blurred * amount

    Args:
        image: CLAHE-enhanced grayscale image (uint8).
        sigma: Gaussian blur standard deviation for unsharp mask base (0.7 - 1.5).
        amount: Sharpening strength factor (0.15 - 0.50).

    Returns:
        sharpened: Subtly sharpened image with intact glyph geometry (uint8).
    """
    if len(image.shape) != 2:
        raise ValueError("Input to gentle_unsharp_mask must be a single-channel grayscale image.")

    blurred = cv2.GaussianBlur(
        image,
        (0, 0),
        sigmaX=float(sigma),
        sigmaY=float(sigma)
    )

    weight_orig = 1.0 + float(amount)
    weight_blur = -float(amount)

    sharpened = cv2.addWeighted(
        image,
        weight_orig,
        blurred,
        weight_blur,
        0
    )

    sharpened_clipped = np.clip(sharpened, 0, 255).astype(np.uint8)
    return sharpened_clipped
