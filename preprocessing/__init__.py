"""
SHILORA Stone Inscription Image Preprocessing Package
Designed for Old Kannada / Halegannada epigraphical text enhancement.
Preserves authentic glyph geometry with zero artificial hallucination.
"""

from .quality_analysis import analyze_image_quality, QualityMetrics
from .illumination_normalization import normalize_illumination
from .contrast_enhancement import enhance_local_contrast
from .sharpening import gentle_unsharp_mask
from .optional_evidence import (
    extract_color_differences,
    extract_surface_details,
    extract_morphological_blackhat,
    generate_ocr_evidence_map
)
from .adaptive_preprocessor import ShiloraStonePreprocessor, PreprocessingResult

__all__ = [
    "analyze_image_quality",
    "QualityMetrics",
    "normalize_illumination",
    "enhance_local_contrast",
    "gentle_unsharp_mask",
    "extract_color_differences",
    "extract_surface_details",
    "extract_morphological_blackhat",
    "generate_ocr_evidence_map",
    "ShiloraStonePreprocessor",
    "PreprocessingResult"
]
