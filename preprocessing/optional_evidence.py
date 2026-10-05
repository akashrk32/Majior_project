"""
SHILORA - Optional Epigraphical Evidence Extraction & OCR Evidence Map
Generates epigraphical evidence maps:
- Color differential enhancement (R-B, R-G, B-G)
- Multi-scale surface detail extraction
- Morphological black-hat filtering for carved groove tracking
- OUTPUT 2: High-contrast OCR Evidence Map for downstream segmentation
"""

from typing import Dict, Tuple
import cv2
import numpy as np


def extract_color_differences(img_bgr: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Computes normalized color channel differences:
    (R - B), (R - G), and (B - G).
    Reveals subtle mineral or weathering color boundaries invisible in raw grayscale.
    """
    if len(img_bgr.shape) != 3 or img_bgr.shape[2] != 3:
        return {}

    b = img_bgr[:, :, 0].astype(np.float32)
    g = img_bgr[:, :, 1].astype(np.float32)
    r = img_bgr[:, :, 2].astype(np.float32)

    diffs = {
        "r_minus_b": r - b,
        "r_minus_g": r - g,
        "b_minus_g": b - g
    }

    normalized_diffs = {}
    for key, diff in diffs.items():
        min_v = diff.min()
        max_v = diff.max()
        if max_v > min_v:
            norm = ((diff - min_v) / (max_v - min_v) * 255.0).astype(np.uint8)
        else:
            norm = np.zeros_like(diff, dtype=np.uint8)
        normalized_diffs[key] = norm

    return normalized_diffs


def extract_surface_details(
    gray: np.ndarray,
    sigmas: Tuple[float, ...] = (5.0, 15.0, 30.0, 60.0)
) -> np.ndarray:
    """
    Extracts multi-scale surface details using bandpass differences:
        detail_s = gray - GaussianBlur(gray, sigma_s)
    Combines scale details with conservative weighting to highlight groove relief
    without blowing up granite speckles.
    """
    gray_f = gray.astype(np.float32)
    accum = np.zeros_like(gray_f)
    weights = [0.35, 0.35, 0.20, 0.10]

    for sigma, w in zip(sigmas, weights):
        blurred = cv2.GaussianBlur(gray_f, (0, 0), sigmaX=sigma, sigmaY=sigma)
        detail = gray_f - blurred
        accum += w * detail

    # Rescale around mid-gray 128
    surface_detail = np.clip(128.0 + accum, 0, 255).astype(np.uint8)
    return surface_detail


def extract_morphological_blackhat(
    gray: np.ndarray,
    kernel_size: int = 15
) -> np.ndarray:
    """
    Computes morphological black-hat:
        blackhat = closing(gray) - gray
    Accentuates recessed carved stroke indentations that are darker than their local neighborhood.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    return blackhat


def generate_ocr_evidence_map(
    natural_enhanced: np.ndarray,
    gray: np.ndarray,
    kernel_size: int = 15
) -> np.ndarray:
    """
    Produces OUTPUT 2: OCR Evidence Map.
    Designed specifically for line detection and character segmentation algorithms.
    Combines natural contrast with localized groove depth (black-hat) and surface details,
    then gently equalizes contrast so faint glyphs have sufficient saliency for bounding box detection.
    """
    # 1. Carved groove detection
    blackhat = extract_morphological_blackhat(natural_enhanced, kernel_size=kernel_size)
    
    # 2. Invert blackhat so carved strokes are dark on light or combine into enhanced negative
    # We subtract blackhat from natural enhanced to deepen inscribed grooves
    groove_deepened = cv2.subtract(natural_enhanced, cv2.multiply(blackhat, 1.2, dtype=cv2.CV_8U))
    
    # 3. Local contrast refinement for OCR candidate localization
    clahe_ocr = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    ocr_evidence = clahe_ocr.apply(groove_deepened)

    return ocr_evidence
