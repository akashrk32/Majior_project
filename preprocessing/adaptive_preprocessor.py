"""
SHILORA - Adaptive Stone Inscription Preprocessor
Main orchestrator for the epigraphical enhancement pipeline.
Guarantees strict 1:1 original resolution preservation (zero cropping),
adaptive parameter tuning based on stone condition, and dual outputs:
  - Output 1: Natural Enhanced Inscription Image (human readability, glyph fidelity)
  - Output 2: OCR Evidence Map (downstream segmentation and recognition)
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional, Union

import cv2
import numpy as np

from .quality_analysis import analyze_image_quality, QualityMetrics
from .illumination_normalization import normalize_illumination
from .contrast_enhancement import enhance_local_contrast
from .sharpening import gentle_unsharp_mask
from .optional_evidence import generate_ocr_evidence_map


@dataclass
class PreprocessingResult:
    original: np.ndarray
    grayscale: np.ndarray
    illumination_background: np.ndarray
    illumination_normalized: np.ndarray
    clahe_enhanced: np.ndarray
    sharpened: np.ndarray
    final_natural: np.ndarray
    ocr_evidence: np.ndarray
    metrics: QualityMetrics
    saved_paths: Dict[str, str]

    def verify_dimensions(self) -> bool:
        """Strict verification that no dimension cropping or resizing occurred."""
        orig_h, orig_w = self.original.shape[:2]
        assert self.grayscale.shape == (orig_h, orig_w), "Grayscale dimension mismatch!"
        assert self.illumination_normalized.shape == (orig_h, orig_w), "Normalized dimension mismatch!"
        assert self.final_natural.shape == (orig_h, orig_w), "Final natural image dimension mismatch!"
        assert self.ocr_evidence.shape == (orig_h, orig_w), "OCR evidence dimension mismatch!"
        return True


class ShiloraStonePreprocessor:
    """
    Production-grade adaptive preprocessor for Old Kannada / Halegannada stone inscriptions.
    """

    def __init__(
        self,
        illumination_sigma: Optional[float] = None,
        illumination_scale: Optional[float] = None,
        clahe_clip_limit: Optional[float] = None,
        clahe_tile_grid: Optional[int] = None,
        sharpen_sigma: Optional[float] = None,
        sharpen_amount: Optional[float] = None
    ):
        """
        Optional manual parameter overrides. If None, parameters are
        automatically and adaptively calculated based on stone image metrics.
        """
        self.manual_illum_sigma = illumination_sigma
        self.manual_illum_scale = illumination_scale
        self.manual_clahe_clip = clahe_clip_limit
        self.manual_clahe_grid = clahe_tile_grid
        self.manual_sharp_sigma = sharpen_sigma
        self.manual_sharp_amount = sharpen_amount

    def process(
        self,
        image_input: Union[str, Path, np.ndarray],
        output_dir: Optional[Union[str, Path]] = None,
        save_intermediates: bool = True
    ) -> PreprocessingResult:
        """
        Executes the full SHILORA stone preprocessing pipeline.

        Args:
            image_input: File path (str/Path) or pre-loaded BGR image (np.ndarray).
            output_dir: Optional directory to save the structured output files.
            save_intermediates: If True, saves all 01 through 08 stage files + json.
        """
        # 1. Read / Validate Original Image
        if isinstance(image_input, (str, Path)):
            input_path = Path(image_input)
            if not input_path.exists():
                raise FileNotFoundError(f"Stone image not found: {input_path}")
            img_bgr = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
            if img_bgr is None:
                raise ValueError(f"Could not decode image at {input_path}")
        elif isinstance(image_input, np.ndarray):
            img_bgr = image_input.copy()
            if len(img_bgr.shape) == 2:
                img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2BGR)
        else:
            raise TypeError("image_input must be a file path or a numpy array.")

        orig_h, orig_w = img_bgr.shape[:2]

        # 2. Grayscale Conversion
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # 3. Quality Analysis & Adaptive Parameter Selection
        metrics = analyze_image_quality(gray)

        illum_sigma = self.manual_illum_sigma or metrics.illumination_sigma
        illum_scale = self.manual_illum_scale or metrics.illumination_scale
        clahe_clip = self.manual_clahe_clip or metrics.clahe_clip_limit
        clahe_grid = self.manual_clahe_grid or metrics.clahe_tile_grid
        sharp_sigma = self.manual_sharp_sigma or metrics.sharpen_sigma
        sharp_amount = self.manual_sharp_amount or metrics.sharpen_amount

        # 4. Large-Scale Illumination & Surface Normalization
        background, normalized = normalize_illumination(
            gray,
            sigma=illum_sigma,
            scale=illum_scale
        )

        # 5. Local Contrast Enhancement (CLAHE)
        clahe_enhanced = enhance_local_contrast(
            normalized,
            clip_limit=clahe_clip,
            tile_grid_size=(clahe_grid, clahe_grid)
        )

        # 6. Gentle Unsharp Masking
        sharpened = gentle_unsharp_mask(
            clahe_enhanced,
            sigma=sharp_sigma,
            amount=sharp_amount
        )

        # OUTPUT 1: Final Natural Enhanced Image
        final_natural = sharpened.copy()

        # OUTPUT 2: OCR Evidence Map
        ocr_evidence = generate_ocr_evidence_map(
            natural_enhanced=final_natural,
            gray=gray,
            kernel_size=15
        )

        # 7. Strict Dimension & Integrity Verification
        assert final_natural.shape == (orig_h, orig_w), (
            f"Resolution altered! Expected {orig_w}x{orig_h}, got {final_natural.shape[1]}x{final_natural.shape[0]}"
        )
        assert ocr_evidence.shape == (orig_h, orig_w), (
            f"Resolution altered! Expected {orig_w}x{orig_h}, got {ocr_evidence.shape[1]}x{ocr_evidence.shape[0]}"
        )

        saved_paths = {}

        # 8. Save Multi-Output Files if output_dir provided
        if output_dir:
            out_p = Path(output_dir)
            out_p.mkdir(parents=True, exist_ok=True)

            stages = [
                ("01_original.png", img_bgr),
                ("02_grayscale.png", gray),
                ("03_illumination_background.png", background),
                ("04_illumination_normalized.png", normalized),
                ("05_clahe_enhanced.png", clahe_enhanced),
                ("06_sharpened.png", sharpened),
                ("07_final_preprocessed.png", final_natural),
                ("08_ocr_evidence.png", ocr_evidence)
            ]

            for fname, img in stages:
                if not save_intermediates and fname not in ["07_final_preprocessed.png", "08_ocr_evidence.png"]:
                    continue
                file_dest = out_p / fname
                cv2.imwrite(str(file_dest), img)
                saved_paths[fname] = str(file_dest)

            # Generate preprocessing_report.json
            report_data = {
                "image_width": int(orig_w),
                "image_height": int(orig_h),
                "rms_contrast": metrics.rms_contrast,
                "tenengrad": metrics.tenengrad,
                "local_std": metrics.local_std,
                "mean_intensity": metrics.mean_intensity,
                "intensity_std": metrics.intensity_std,
                "dynamic_range": metrics.dynamic_range,
                "estimated_noise": metrics.estimated_noise,
                "quality_tier": metrics.quality_tier,
                "illumination_sigma": illum_sigma,
                "illumination_scale": illum_scale,
                "clahe_clip_limit": clahe_clip,
                "clahe_tile_grid": clahe_grid,
                "sharpen_sigma": sharp_sigma,
                "sharpen_amount": sharp_amount
            }

            report_file = out_p / "preprocessing_report.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=4)
            saved_paths["preprocessing_report.json"] = str(report_file)

        result = PreprocessingResult(
            original=img_bgr,
            grayscale=gray,
            illumination_background=background,
            illumination_normalized=normalized,
            clahe_enhanced=clahe_enhanced,
            sharpened=sharpened,
            final_natural=final_natural,
            ocr_evidence=ocr_evidence,
            metrics=metrics,
            saved_paths=saved_paths
        )

        result.verify_dimensions()
        return result
