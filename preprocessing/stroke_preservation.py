"""
SHILORA Multi-Representation & Stroke Preservation Engine
=========================================================
Implements DPIPP multi-candidate generation, 14-metric stroke quality evaluation,
grounded gradient verification, robust line band reconstruction, and
automatic fallback representation selection.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks


class StrokeQualityEvaluator:
    """
    Evaluates candidate binary masks against the enhanced grayscale image
    using 14 grounded morphological, topological, and gradient metrics.
    """

    @staticmethod
    def evaluate(
        mask: np.ndarray,
        gray_enhanced: np.ndarray,
        grad_edges: np.ndarray
    ) -> Dict[str, Any]:
        h, w = mask.shape[:2]
        total_pixels = float(h * w)
        fg_pixels = int(np.count_nonzero(mask == 255))
        fg_ratio = fg_pixels / max(1.0, total_pixels)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            (mask == 255).astype(np.uint8), connectivity=8
        )
        cc_count = int(num_labels - 1)
        areas = stats[1:, cv2.CC_STAT_AREA] if cc_count > 0 else np.array([0])

        if cc_count == 0 or fg_pixels == 0:
            return {
                "score": 0.0,
                "status": "FAILED_EMPTY",
                "foreground_ratio": 0.0,
                "cc_count": 0,
                "median_area": 0.0,
                "tiny_ratio": 1.0,
                "frag_ratio": 1.0,
                "grad_support": 0.0,
                "boundary_overlap": 0.0,
                "stroke_continuity": 0.0,
                "skeleton_continuity": 0.0,
                "horizontal_continuity": 0.0,
                "char_density": 0.0,
                "local_contrast": 0.0,
                "erosion_ratio": 1.0,
                "bg_contamination": 0.0
            }

        med_area = float(np.median(areas))
        tiny_count = int(np.count_nonzero(areas < 15))
        tiny_ratio = float(tiny_count / max(1, cc_count))
        frag_count = int(np.count_nonzero(areas < 30))
        frag_ratio = float(frag_count / max(1, cc_count))

        # 14. Percentage of pixels supported by actual image gradients/relief
        fg_mask_bool = (mask == 255)
        grad_support = float(np.mean(grad_edges[fg_mask_bool]))

        # 9. Edge/stroke boundary overlap with enhanced grayscale image
        kernel_cross = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        dil = cv2.dilate((fg_mask_bool).astype(np.uint8), kernel_cross)
        er = cv2.erode((fg_mask_bool).astype(np.uint8), kernel_cross)
        boundary = (dil - er) > 0
        boundary_overlap = float(np.mean(grad_edges[boundary])) if np.any(boundary) else 0.0

        # 5. Stroke continuity: ratio of FG pixels with >= 2 8-neighbors (continuous stroke)
        neighbor_filter = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.uint8)
        neighbor_count = cv2.filter2D(fg_mask_bool.astype(np.uint8), -1, neighbor_filter)
        stroke_continuity = float(np.mean((neighbor_count >= 2)[fg_mask_bool]))

        # 6. Skeleton continuity: proxy via thin strokes ratio
        skeleton_continuity = float(np.mean((neighbor_count >= 1)[fg_mask_bool]))

        # 7. Horizontal line continuity: consistency across horizontal projection
        horiz_proj = np.sum(fg_mask_bool, axis=1)
        proj_std = float(np.std(horiz_proj))
        proj_mean = float(np.mean(horiz_proj)) + 1e-6
        horizontal_continuity = float(min(1.0, proj_std / proj_mean))

        # 8. Character region density (middle 80% vs outer margins)
        inner_box = fg_mask_bool[int(h*0.1):int(h*0.9), int(w*0.1):int(w*0.9)]
        char_density = float(np.mean(inner_box))

        # 10. Local contrast preservation
        bg_pixels = gray_enhanced[mask == 0]
        fg_gray = gray_enhanced[mask == 255]
        mean_bg = float(np.mean(bg_pixels)) if len(bg_pixels) > 0 else 128.0
        mean_fg = float(np.mean(fg_gray)) if len(fg_gray) > 0 else 128.0
        local_contrast = float(min(1.0, abs(mean_bg - mean_fg) / 48.0))

        # 11. Erosion/destruction ratio: components with width or height <= 1
        widths = stats[1:, cv2.CC_STAT_WIDTH]
        heights = stats[1:, cv2.CC_STAT_HEIGHT]
        eroded_count = int(np.count_nonzero((widths <= 1) | (heights <= 1)))
        erosion_ratio = float(eroded_count / max(1, cc_count))

        # 13. Background contamination (outer 3% borders)
        m_h, m_w = max(2, int(h * 0.03)), max(2, int(w * 0.03))
        margin_mask = np.zeros_like(mask, dtype=bool)
        margin_mask[:m_h, :] = True
        margin_mask[-m_h:, :] = True
        margin_mask[:, :m_w] = True
        margin_mask[:, -m_w:] = True
        bg_contamination = float(np.mean(mask[margin_mask] == 255))

        # Composite Quality Score
        fg_target_score = max(0.0, 1.0 - abs(fg_ratio - 0.15) / 0.15)
        raw_score = (
            0.25 * grad_support
            + 0.20 * boundary_overlap
            + 0.20 * (1.0 - frag_ratio)
            + 0.15 * stroke_continuity
            + 0.10 * local_contrast
            + 0.10 * fg_target_score
        ) - 0.25 * bg_contamination - 0.20 * tiny_ratio

        score = float(max(0.0, min(1.0, raw_score)))
        status = "APPROVED" if (score >= 0.45 and frag_ratio <= 0.70) else "POOR_STROKE_PRESERVATION"

        return {
            "score": round(score, 4),
            "status": status,
            "foreground_ratio": round(fg_ratio, 4),
            "cc_count": cc_count,
            "median_area": round(med_area, 1),
            "tiny_ratio": round(tiny_ratio, 4),
            "frag_ratio": round(frag_ratio, 4),
            "grad_support": round(grad_support, 4),
            "boundary_overlap": round(boundary_overlap, 4),
            "stroke_continuity": round(stroke_continuity, 4),
            "skeleton_continuity": round(skeleton_continuity, 4),
            "horizontal_continuity": round(horizontal_continuity, 4),
            "char_density": round(char_density, 4),
            "local_contrast": round(local_contrast, 4),
            "erosion_ratio": round(erosion_ratio, 4),
            "bg_contamination": round(bg_contamination, 4)
        }


class MultiCandidateBinarizer:
    """
    Generates controlled adaptive binarization candidates:
    1. Adaptive Gaussian Conservative
    2. Adaptive Gaussian Moderate
    3. Top-Hat / Black-Hat Relief Threshold
    4. Sauvola / Local Contrast Adaptive Threshold
    """

    @staticmethod
    def generate_candidates(
        gray_enhanced: np.ndarray,
        relief_enhanced: np.ndarray
    ) -> Dict[str, np.ndarray]:
        h, w = gray_enhanced.shape[:2]

        # Gentle bilateral smoothing to reduce granite speckle noise
        smooth_gray = cv2.bilateralFilter(gray_enhanced, 5, 35, 35)

        # Candidate 1: Adaptive Gaussian Conservative (block 31, C=5, gentle closing)
        c1 = cv2.adaptiveThreshold(
            smooth_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 5
        )
        c1 = cv2.morphologyEx(c1, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))

        # Candidate 2: Adaptive Gaussian Moderate (block 25, C=2)
        c2 = cv2.adaptiveThreshold(
            smooth_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 2
        )
        c2 = cv2.morphologyEx(c2, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))

        # Candidate 3: Relief-Enhanced Threshold (Black-Hat minus Top-Hat)
        c3 = cv2.adaptiveThreshold(
            relief_enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, -3
        )

        # Candidate 4: Sauvola Local Contrast
        gray_f = gray_enhanced.astype(np.float32)
        mean = cv2.blur(gray_f, (25, 25))
        sqr_mean = cv2.blur(gray_f ** 2, (25, 25))
        std = np.sqrt(np.maximum(0.0, sqr_mean - mean ** 2))
        sauvola_th = mean * (1.0 + 0.25 * (std / 128.0 - 1.0))
        c4 = (gray_f < sauvola_th).astype(np.uint8) * 255
        c4 = cv2.morphologyEx(c4, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2)))

        return {
            "candidate_01": c1,
            "candidate_02": c2,
            "candidate_03": c3,
            "candidate_04": c4
        }


class RobustLineDetector:
    """
    Detects continuous horizontal inscription line bands EXCLUSIVELY from the
    Attention U-Net binary inscription mask, preventing isolated noise speckles
    from creating fake lines and excluding peripheral camera watermarks.
    """

    @staticmethod
    def detect_line_bands(
        binary_mask: np.ndarray,
        min_stroke_count: int = 40,
        min_width_ratio: float = 0.25
    ) -> List[Dict[str, Any]]:
        """
        Derives text-line segmentation solely from the binary mask.
        Uses horizontal stroke density projection, baseline continuity, and
        spatial proximity to identify genuine inscription lines.
        """
        h, w = binary_mask.shape[:2]

        # 1. Horizontal projection profile of Attention U-Net binary character strokes
        horiz_proj = np.sum(binary_mask > 0, axis=1).astype(np.float32)
        smooth_proj = gaussian_filter1d(horiz_proj, sigma=2.5)

        # 2. Adaptive peak prominence based on stroke density
        proj_max = float(np.max(smooth_proj)) if len(smooth_proj) > 0 else 0.0
        if proj_max < 5.0:
            return []

        prominence = max(6.0, proj_max * 0.08)
        peaks, props = find_peaks(smooth_proj, distance=16, prominence=prominence)

        if len(peaks) == 0:
            return []

        # 3. Calculate median line pitch (gap between consecutive peaks)
        line_pitches = np.diff(peaks) if len(peaks) > 1 else np.array([30])
        med_pitch = float(np.median(line_pitches)) if len(line_pitches) > 0 else 30.0

        # 4. Watermark / Peripheral artifact filtering:
        # Check if the lowest peak is near bottom margin (> 0.90 * h) with a large gap from the inscription block
        valid_peaks = []
        for i, cy in enumerate(peaks):
            # If line is in bottom 10% and separated from preceding text by > 1.8x median pitch
            if cy > int(h * 0.90) and i > 0:
                gap = cy - peaks[i - 1]
                if gap > 1.8 * med_pitch:
                    # Isolated bottom mark (e.g. camera watermark "OPPO A9 2020", timestamp)
                    continue
            valid_peaks.append(cy)

        if not valid_peaks:
            valid_peaks = peaks.tolist()

        # 5. Build line bands with bounding boxes determined from binary stroke geometry
        col_x1_default = int(w * 0.05)
        col_x2_default = int(w * 0.95)

        line_bands = []
        for i, cy in enumerate(valid_peaks):
            lh = int(med_pitch)
            if i > 0 and i < len(valid_peaks) - 1:
                lh = int((valid_peaks[i+1] - valid_peaks[i-1]) / 2.0)
            elif i < len(valid_peaks) - 1:
                lh = int(valid_peaks[i+1] - valid_peaks[i])
            elif i > 0:
                lh = int(valid_peaks[i] - valid_peaks[i-1])

            lh = max(18, min(int(med_pitch * 1.3), lh))
            y1 = max(0, int(cy - lh * 0.55))
            y2 = min(h, int(cy + lh * 0.55))

            # Inspect binary strokes inside this vertical slice
            slice_mask = binary_mask[y1:y2, :]
            stroke_pixels = int(np.count_nonzero(slice_mask))

            # Reject lines containing only isolated noise dots
            if stroke_pixels < min_stroke_count:
                continue

            # Determine horizontal extent of strokes in this line
            cols_with_fg = np.where(np.sum(slice_mask > 0, axis=0) > 0)[0]
            if len(cols_with_fg) > 0:
                bx1 = max(0, int(cols_with_fg[0] - 12))
                bx2 = min(w, int(cols_with_fg[-1] + 12))
                bw = bx2 - bx1
            else:
                bx1 = col_x1_default
                bw = col_x2_default - col_x1_default

            bh = y2 - y1

            if bw >= int(w * min_width_ratio) and bh >= 12:
                line_bands.append({
                    "line_index": len(line_bands) + 1,
                    "bbox": [bx1, y1, bw, bh],
                    "centroid_y": int(cy),
                    "stroke_pixels": stroke_pixels
                })

        return line_bands
