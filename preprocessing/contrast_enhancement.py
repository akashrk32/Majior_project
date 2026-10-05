"""
SHILORA - Local Contrast Enhancement
Enhances local visibility of ancient inscription strokes using Contrast Limited
Adaptive Histogram Equalization (CLAHE) without blowing out highlights or amplifying noise.
"""

from typing import Tuple, Union
import cv2
import numpy as np


def enhance_local_contrast(
    image: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Union[int, Tuple[int, int]] = (12, 12)
) -> np.ndarray:
    """
    Applies CLAHE to enhance local inscription stroke visibility.

    Args:
        image: Single-channel illumination-normalized image (uint8).
        clip_limit: Threshold for contrast limiting (1.5 - 3.0).
        tile_grid_size: Size of grid for histogram equalization (8x8 - 16x16).

    Returns:
        enhanced: Locally contrast-enhanced image (uint8).
    """
    if len(image.shape) != 2:
        raise ValueError("Input to enhance_local_contrast must be a single-channel grayscale image.")

    if isinstance(tile_grid_size, int):
        grid = (tile_grid_size, tile_grid_size)
    else:
        grid = tuple(tile_grid_size)

    clahe = cv2.createCLAHE(
        clipLimit=float(clip_limit),
        tileGridSize=grid
    )

    enhanced = clahe.apply(image)
    return enhanced
