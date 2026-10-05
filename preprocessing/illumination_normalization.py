"""
SHILORA - Illumination and Surface Normalization
Estimates slowly varying illumination fields and large-scale stone brightness variations,
normalizing the surface to reveal authentic engraved character strokes uniformly.
"""

from typing import Tuple
import cv2
import numpy as np


def normalize_illumination(
    gray: np.ndarray,
    sigma: float = 35.0,
    scale: float = 150.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Normalizes stone surface illumination by dividing the grayscale image
    by its broad Gaussian background estimate.

    Args:
        gray: Grayscale stone image (uint8).
        sigma: Standard deviation for Gaussian background estimation (20 - 60).
        scale: Multiplier scale factor for division (typically ~150).

    Returns:
        background: Estimated illumination background field (uint8).
        normalized: Flattened surface image with even illumination (uint8).
    """
    if len(gray.shape) != 2:
        raise ValueError("Input to normalize_illumination must be a single-channel grayscale image.")

    # 1. Estimate large-scale background illumination field
    background = cv2.GaussianBlur(
        gray,
        (0, 0),
        sigmaX=sigma,
        sigmaY=sigma
    )

    # Prevent division by zero
    background_safe = np.maximum(background, 1)

    # 2. Divide original grayscale by estimated background
    # This flattens lighting gradients and deep shadows without destroying glyph grooves
    normalized = cv2.divide(
        gray,
        background_safe,
        scale=scale
    )

    return background, normalized
