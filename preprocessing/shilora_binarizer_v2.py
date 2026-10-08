"""
SHILORA Robust Stone Inscription Binarizer V2
=============================================
Combines the official ShilaLekhya two-stage self-refining inference pipeline
with SHILORA's research-informed engineering additions:

Official ShilaLekhya Architecture Preserved:
  1. Stage 1: Multi-scale sliding-window prediction (approx 256, 384, 512, 768 px).
  2. Maximum probability coarse fusion across scales (official default).
  3. Coarse threshold at 0.5.
  4. Robust character height estimation from coarse connected components (IQR-filtered).
  5. Stage 2: Character-Context-Aware dynamic patching (H_RANGE 4x-9x character height).
  6. Overlapping patch prediction and accumulation with count canvas normalization.
  7. Final thresholding (0.50 default).

SHILORA Engineering Additions (Separately Documented):
  1. Model Input Adapter: Evaluates continuous-valued image inputs:
     - Branch A: RAW RGB
     - Branch B: V3 Preprocessed RGB
     - Branch C: Lightly normalized V3 RGB
     - Branch D: Guided Luminance-Preserving Adapted V3
  2. Multi-Scale Scale Adaptation for varying inscription resolutions (thumbnail vs 4K).
  3. Boundary / Seam Protection: Smooth center-weighted Hann/taper aggregation to eliminate patch edges.
  4. Coarse Prediction Failure & Blank Output Detector (triggers validated fallbacks).
  5. Multi-Scale Agreement & Probability Statistics (P_mean, P_max, P90, P95, P99).
  6. Controlled Diagnostic Threshold Exploration [0.30 - 0.65] when 0.50 produces empty mask.
  7. Conservative Binary Cleanup: Removes isolated speckles (< 10 px), preserves thin strokes and holes.
  8. Original-Image Fidelity Check: Suppresses non-glyph background false positives.
  9. Epigraphical Quality Gate (Categories A, B, C, D / Information-Limited).
"""

import os
import sys
import time
import math
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any

import cv2
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

# Ensure backend unet_model is available
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "Brahmi-OCR-main" / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from episam_binarizer.unet_model import AttentionUNet

# Hardware device configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DEFAULT_MODEL_PATH = BACKEND_DIR / "episam_binarizer" / "binarizer.pth"


class ShiloraBinarizerV2:
    """
    Production-grade robust stone inscription binarizer implementing the two-stage
    ShilaLekhya algorithm with SHILORA domain adapters and quality gates.
    """

    def __init__(self, model_path: Optional[Path] = None, device: Optional[torch.device] = None):
        self.device = device or DEVICE
        self.model_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model weights not found at: {self.model_path}")

        print(f"[SHILORA Binarizer V2] Loading AttentionUNet from {self.model_path} onto {self.device}...")
        self.model = AttentionUNet(in_channels=3, out_classes=1, bilinear=False)
        state_dict = torch.load(self.model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()
        print("[SHILORA Binarizer V2] Model ready.")

    # =========================================================================
    # PHASE 6: MODEL INPUT ADAPTER
    # =========================================================================
    @staticmethod
    def create_model_inputs(raw_bgr: np.ndarray, v3_bgr: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Creates continuous-valued model input variants preserving RGB structure,
        natural intensity relationships, and inscription visibility.
        """
        h, w = v3_bgr.shape[:2]
        if raw_bgr.shape[:2] != (h, w):
            raw_bgr = cv2.resize(raw_bgr, (w, h), interpolation=cv2.INTER_AREA)

        # Branch A: Original RAW RGB
        branch_a = cv2.cvtColor(raw_bgr, cv2.COLOR_BGR2RGB)

        # Branch B: Standard V3 Grayscale duplicated across 3 channels
        branch_b = cv2.cvtColor(v3_bgr, cv2.COLOR_BGR2RGB)

        # Branch C: Natural Lightly-Normalized V3 (bounded contrast stretch)
        v3_gray = cv2.cvtColor(v3_bgr, cv2.COLOR_BGR2GRAY)
        p2, p98 = np.percentile(v3_gray, (2, 98))
        norm_c = np.clip((v3_gray.astype(np.float32) - p2) / (p98 - p2 + 1e-5) * 255.0, 0, 255).astype(np.uint8)
        branch_c = cv2.cvtColor(norm_c, cv2.COLOR_GRAY2RGB)

        # Branch D: Guided Luminance-Adapted V3 (blends raw chromaticity with normalized V3 luminance)
        raw_lab = cv2.cvtColor(raw_bgr, cv2.COLOR_BGR2LAB)
        l_raw, a_raw, b_raw = cv2.split(raw_lab)

        # Match V3 luminance mean and standard deviation to RAW natural luminance
        v3_f = v3_gray.astype(np.float32)
        v3_std = v3_f.std() + 1e-5
        v3_norm = (v3_f - v3_f.mean()) / v3_std
        # Gentle tone bounding
        target_std = max(25.0, float(l_raw.std()) * 0.85)
        target_mean = float(np.clip(l_raw.mean(), 80.0, 180.0))
        matched_l = np.clip(v3_norm * target_std + target_mean, 0, 255).astype(np.uint8)

        adapted_lab = cv2.merge([matched_l, a_raw, b_raw])
        branch_d = cv2.cvtColor(cv2.cvtColor(adapted_lab, cv2.COLOR_LAB2BGR), cv2.COLOR_BGR2RGB)

        return {
            "A_RAW": branch_a,
            "B_V3": branch_b,
            "C_LIGHT_V3": branch_c,
            "D_ADAPTED_V3": branch_d,
        }

    # =========================================================================
    # PHASE 1 & 5: MULTI-SCALE SLIDING-WINDOW INFERENCE & FUSION
    # =========================================================================
    def predict_patchwise(
        self,
        image_tensor: torch.Tensor,
        patch_size: int,
        overlap: int,
        in_size: int = 512,
        batch_size: int = 4,
        use_hann_window: bool = True
    ) -> np.ndarray:
        """
        Batched sliding-window patchwise prediction with center-weighted
        Hann windowing to prevent patch boundary seams and discontinuities.
        """
        self.model.eval()
        c, h, w = image_tensor.shape
        stride = max(1, patch_size - overlap)
        pad_h = (stride - (h - overlap) % stride) % stride
        pad_w = (stride - (w - overlap) % stride) % stride
        image_padded = F.pad(image_tensor, (0, pad_w, 0, pad_h), mode='reflect').unsqueeze(0)
        _, _, H, W = image_padded.shape

        prediction_canvas = torch.zeros((1, 1, H, W), device=self.device)
        weight_canvas = torch.zeros((1, 1, H, W), device=self.device)

        # Create smooth 2D Hann window for seam protection
        if use_hann_window and patch_size > 16:
            window_1d = torch.hann_window(patch_size, periodic=False, device=self.device)
            window_2d = (window_1d.unsqueeze(1) * window_1d.unsqueeze(0)).unsqueeze(0).unsqueeze(0)
            window_2d = torch.clamp(window_2d, min=0.05)  # Avoid zero weights at borders
        else:
            window_2d = torch.ones((1, 1, patch_size, patch_size), device=self.device)

        patch_coords = []
        for y in range(0, H - overlap, stride):
            for x in range(0, W - overlap, stride):
                patch_coords.append((y, x))

        for i in range(0, len(patch_coords), batch_size):
            batch_indices = patch_coords[i:i + batch_size]
            patches = [image_padded[:, :, y:y+patch_size, x:x+patch_size] for y, x in batch_indices]
            batch_tensor = torch.cat(patches, dim=0).to(self.device)

            with torch.inference_mode():
                batch_in = F.interpolate(batch_tensor, size=(in_size, in_size), mode='bilinear', align_corners=False)
                pred_batch = torch.sigmoid(self.model(batch_in))
                pred_orig = F.interpolate(pred_batch, size=(patch_size, patch_size), mode='bilinear', align_corners=False)

            for b_idx, (y, x) in enumerate(batch_indices):
                weighted_pred = pred_orig[b_idx:b_idx+1] * window_2d
                prediction_canvas[:, :, y:y+patch_size, x:x+patch_size] += weighted_pred
                weight_canvas[:, :, y:y+patch_size, x:x+patch_size] += window_2d

        prediction_canvas /= (weight_canvas + 1e-8)
        return prediction_canvas[:, :, :h, :w].squeeze().cpu().numpy()

    def run_stage1_multiscale(
        self,
        img_rgb: np.ndarray,
        fusion_method: str = "max",
        stage1_resize_max: int = 1536
    ) -> Tuple[np.ndarray, Dict[int, np.ndarray], float]:
        """
        Executes Stage 1 multi-scale sliding-window inference across scales
        [256, 384, 512, 768] (adapted to image dimensions).
        For images exceeding stage1_resize_max (e.g. 18MP), resizes to stage1_resize_max
        for coarse scale matching, then maps coarse probabilities back to original resolution.
        """
        h_orig, w_orig = img_rgb.shape[:2]
        scale_factor = 1.0
        if max(h_orig, w_orig) > stage1_resize_max:
            scale_factor = stage1_resize_max / float(max(h_orig, w_orig))
            proc_w = int(w_orig * scale_factor)
            proc_h = int(h_orig * scale_factor)
            proc_rgb = cv2.resize(img_rgb, (proc_w, proc_h), interpolation=cv2.INTER_AREA)
        else:
            proc_rgb = img_rgb

        img_tensor = transforms.ToTensor()(proc_rgb)
        c, h, w = img_tensor.shape
        min_dim = min(h, w)

        # Scale selection adapting to image dimension
        base_scales = [256, 384, 512, 768]
        active_scales = []
        for s in base_scales:
            clamped = min(s, min_dim)
            if clamped >= 64 and clamped not in active_scales:
                active_scales.append(clamped)
            elif clamped < 64 and not active_scales:
                active_scales.append(max(32, min_dim))

        scale_preds: Dict[int, np.ndarray] = {}
        for s in sorted(active_scales):
            overlap = max(16, s // 2)
            pred = self.predict_patchwise(img_tensor, patch_size=s, overlap=overlap, in_size=512)
            # Map back to original resolution if scaled
            if scale_factor != 1.0:
                pred_orig = cv2.resize(pred, (w_orig, h_orig), interpolation=cv2.INTER_LINEAR)
            else:
                pred_orig = pred
            scale_preds[s] = pred_orig

        # Multi-scale fusion
        preds_list = list(scale_preds.values())
        if fusion_method == "max":
            fused = np.maximum.reduce(preds_list)
        elif fusion_method == "average":
            fused = np.mean(np.stack(preds_list), axis=0)
        elif fusion_method == "confidence_weighted":
            weights = [max(0.1, float(np.percentile(p, 98) - np.percentile(p, 50))) for p in preds_list]
            total_w = sum(weights)
            norm_w = [w / total_w for w in weights]
            fused = np.zeros_like(preds_list[0])
            for p, nw in zip(preds_list, norm_w):
                fused += p * nw
        else:
            fused = np.maximum.reduce(preds_list)

        # Multi-scale agreement
        if len(preds_list) > 1:
            corrs = []
            for i in range(len(preds_list)):
                for j in range(i+1, len(preds_list)):
                    # Sample flat arrays for speed on high resolution
                    flat_i = preds_list[i][::4, ::4].flatten()
                    flat_j = preds_list[j][::4, ::4].flatten()
                    r = np.corrcoef(flat_i, flat_j)[0, 1]
                    if not np.isnan(r):
                        corrs.append(r)
            ms_agreement = float(np.mean(corrs)) if corrs else 1.0
        else:
            ms_agreement = 1.0

        return fused, scale_preds, ms_agreement

    # =========================================================================
    # PHASE 8 & 9: ROBUST CHARACTER HEIGHT ESTIMATION & FALLBACKS
    # =========================================================================
    @staticmethod
    def estimate_character_height(
        coarse_prob: np.ndarray,
        threshold: float = 0.50
    ) -> Tuple[float, int, Dict[str, Any]]:
        """
        Estimates character height using robust IQR-filtered connected components.
        Rejects tiny speckles (< 10 px) and giant non-glyph background blocks.
        """
        coarse_bin = (coarse_prob > threshold).astype(np.uint8)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(coarse_bin, connectivity=8)

        info = {
            "num_raw_components": max(0, num_labels - 1),
            "valid_components": 0,
            "iqr_mean_height": 0.0,
            "median_height": 0.0,
            "p25_height": 0.0,
            "p75_height": 0.0,
            "fallback_used": False
        }

        if num_labels <= 1:
            info["fallback_used"] = True
            return 0.0, 0, info

        heights = stats[1:, cv2.CC_STAT_HEIGHT]
        areas = stats[1:, cv2.CC_STAT_AREA]

        # Valid inscription character component criteria
        img_area = coarse_prob.size
        valid_mask = (areas >= 8) & (areas <= img_area * 0.15) & (heights >= 4)
        h_valid = heights[valid_mask]

        if len(h_valid) == 0:
            info["fallback_used"] = True
            return 0.0, 0, info

        q25, q75 = np.percentile(h_valid, [25, 75])
        iqr = q75 - q25
        lower = max(4.0, q25 - 1.5 * iqr)
        upper = q75 + 1.5 * iqr
        inliers = h_valid[(h_valid >= lower) & (h_valid <= upper)]

        robust_h = float(np.mean(inliers)) if len(inliers) > 0 else float(np.median(h_valid))
        info["valid_components"] = int(np.sum(valid_mask))
        info["iqr_mean_height"] = round(robust_h, 2)
        info["median_height"] = round(float(np.median(h_valid)), 2)
        info["p25_height"] = round(float(q25), 2)
        info["p75_height"] = round(float(q75), 2)

        return robust_h, int(np.sum(valid_mask)), info

    # =========================================================================
    # PHASE 10, 11, 12, 13: STAGE 2 CONTEXT-AWARE DYNAMIC PATCHING
    # =========================================================================
    def run_stage2_dynamic_patching(
        self,
        img_rgb: np.ndarray,
        coarse_prob: np.ndarray,
        base_char_h: float,
        h_range: Tuple[float, float] = (4.0, 9.0),
        patch_counts: Tuple[int, int] = (90, 20)
    ) -> np.ndarray:
        """
        Executes ShilaLekhya Stage 2 character-context-aware dynamic patching.
        Extracts patches centered on characters and background, predicts with model,
        and averages overlapping predictions on accumulator canvas.
        """
        img_tensor = transforms.ToTensor()(img_rgb)
        c, h, w = img_tensor.shape

        # Sample patch centers from coarse prediction
        fg_thresh = 0.40 if np.mean(coarse_prob > 0.5) < 0.01 else 0.50
        guidance_bin = (coarse_prob > fg_thresh).astype(np.uint8)
        fg_pixels = np.argwhere(guidance_bin > 0)

        if len(fg_pixels) == 0:
            # Fallback if no foreground: return coarse prediction
            return coarse_prob

        num_fg = min(patch_counts[0], len(fg_pixels))
        np.random.seed(42)  # Deterministic repeatability
        fg_idx = np.random.choice(len(fg_pixels), num_fg, replace=False)
        patch_defs = [{"center": tuple(fg_pixels[i]), "h_mul": float(np.random.uniform(h_range[0], h_range[1]))} for i in fg_idx]

        # Sample background patch centers safely without giant array allocations
        if patch_counts[1] > 0:
            rand_ys = np.random.randint(0, h, size=patch_counts[1] * 4)
            rand_xs = np.random.randint(0, w, size=patch_counts[1] * 4)
            bg_count = 0
            for ry, rx in zip(rand_ys, rand_xs):
                if guidance_bin[ry, rx] == 0:
                    patch_defs.append({"center": (int(ry), int(rx)), "h_mul": float(np.random.uniform(h_range[0], h_range[1]))})
                    bg_count += 1
                    if bg_count >= patch_counts[1]:
                        break

        np.random.shuffle(patch_defs)

        # Padding size for boundary safety
        max_patch_size = int(h_range[1] * base_char_h)
        pad_size = min(max_patch_size, min(h, w) - 1)
        pad_size = max(32, pad_size)

        img_padded = F.pad(img_tensor, (pad_size, pad_size, pad_size, pad_size), mode='reflect')
        _, H_pad, W_pad = img_padded.shape

        # Keep canvases on CPU (as in official ShilaLekhya) to prevent GPU OOM on 18MP images
        pred_canvas = torch.zeros((1, 1, H_pad, W_pad), device='cpu')
        weight_canvas = torch.zeros((1, 1, H_pad, W_pad), device='cpu')

        batch_patches = []
        batch_coords = []
        batch_windows = []

        batch_size = 4
        for p_def in patch_defs:
            cy, cx = p_def["center"]
            py, px = cy + pad_size, cx + pad_size
            dyn_size = max(48, int(p_def["h_mul"] * base_char_h))
            dyn_size = min(dyn_size, min(H_pad, W_pad) - 2)
            half = dyn_size // 2

            y1, y2 = max(0, py - half), min(H_pad, py - half + dyn_size)
            x1, x2 = max(0, px - half), min(W_pad, px - half + dyn_size)
            actual_h, actual_w = y2 - y1, x2 - x1

            if actual_h < 32 or actual_w < 32:
                continue

            patch_crop = img_padded[:, y1:y2, x1:x2].unsqueeze(0)
            # Create Hann window for this patch size
            win_y = torch.hann_window(actual_h, periodic=False)
            win_x = torch.hann_window(actual_w, periodic=False)
            win_2d = torch.clamp((win_y.unsqueeze(1) * win_x.unsqueeze(0)).unsqueeze(0).unsqueeze(0), min=0.05)

            batch_patches.append(patch_crop)
            batch_coords.append((y1, y2, x1, x2))
            batch_windows.append(win_2d)

            if len(batch_patches) >= batch_size:
                self._accumulate_stage2_batch(batch_patches, batch_coords, batch_windows, pred_canvas, weight_canvas)
                batch_patches.clear()
                batch_coords.clear()
                batch_windows.clear()

        if batch_patches:
            self._accumulate_stage2_batch(batch_patches, batch_coords, batch_windows, pred_canvas, weight_canvas)

        pred_canvas /= (weight_canvas + 1e-8)
        unpadded = pred_canvas[0, 0, pad_size:pad_size+h, pad_size:pad_size+w].numpy()

        # If Stage 2 covered pixels, blend with coarse map for uncovered margin safety
        coverage_mask = (weight_canvas[0, 0, pad_size:pad_size+h, pad_size:pad_size+w] > 0.01).numpy()
        final_prob = np.where(coverage_mask, unpadded, coarse_prob)
        return final_prob

    def _accumulate_stage2_batch(
        self,
        patches: List[torch.Tensor],
        coords: List[Tuple[int, int, int, int]],
        windows: List[torch.Tensor],
        pred_canvas: torch.Tensor,
        weight_canvas: torch.Tensor
    ):
        """Helper to evaluate and accumulate Stage 2 batch predictions onto CPU canvas."""
        for patch, (y1, y2, x1, x2), win in zip(patches, coords, windows):
            with torch.inference_mode():
                p_in = F.interpolate(patch.to(self.device), size=(512, 512), mode='bilinear', align_corners=False)
                p_pred = torch.sigmoid(self.model(p_in))
                p_orig = F.interpolate(p_pred.cpu(), size=(y2-y1, x2-x1), mode='bilinear', align_corners=False)

            pred_canvas[:, :, y1:y2, x1:x2] += p_orig * win
            weight_canvas[:, :, y1:y2, x1:x2] += win

    # =========================================================================
    # PHASE 18: CONSERVATIVE BINARY CLEANUP
    # =========================================================================
    @staticmethod
    def conservative_cleanup(binary_mask: np.ndarray, min_area: int = 8) -> np.ndarray:
        """
        Removes isolated speckles (< min_area pixels).
        Preserves thin strokes, holes inside characters, and glyph margins.
        Does NOT apply aggressive closing operations that merge adjacent glyphs.
        """
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_mask, connectivity=8)
        if num_labels <= 1:
            return binary_mask

        cleaned = np.zeros_like(binary_mask)
        areas = stats[1:, cv2.CC_STAT_AREA]

        for label_idx in range(1, num_labels):
            if areas[label_idx - 1] >= min_area:
                cleaned[labels == label_idx] = 255

        return cleaned

    # =========================================================================
    # PHASE 19: ORIGINAL-IMAGE FIDELITY CHECK
    # =========================================================================
    @staticmethod
    def verify_original_fidelity(
        binary_mask: np.ndarray,
        raw_bgr: np.ndarray,
        v3_bgr: np.ndarray,
        prob_map: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """
        Validates binary components against original image evidence.
        Rejects large non-glyph components caused by uniform stone stains or cracks.
        Returns cleaned mask and fidelity score.
        """
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_mask, connectivity=8)
        if num_labels <= 1:
            return binary_mask, 1.0

        v3_gray = cv2.cvtColor(v3_bgr, cv2.COLOR_BGR2GRAY)
        h, w = v3_gray.shape[:2]
        sobel_x = cv2.Sobel(v3_gray, cv2.CV_32F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(v3_gray, cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = cv2.magnitude(sobel_x, sobel_y)

        verified = np.zeros_like(binary_mask)
        rejected_count = 0
        total_fg_components = max(1, num_labels - 1)

        for label_idx in range(1, num_labels):
            area = stats[label_idx, cv2.CC_STAT_AREA]
            comp_h = stats[label_idx, cv2.CC_STAT_HEIGHT]
            comp_w = stats[label_idx, cv2.CC_STAT_WIDTH]
            aspect = float(comp_w) / max(1, comp_h)

            # Rejection criteria:
            # 1. Extreme aspect ratio with low gradient energy (cracks)
            # 2. Giant region covering > 25% of image (background lighting blob)
            if area > (h * w * 0.25):
                rejected_count += 1
                continue
            if (aspect > 12.0 or aspect < 0.08) and comp_h > 50:
                # Check mean gradient energy in component
                comp_grad = np.mean(grad_mag[labels == label_idx])
                if comp_grad < 15.0:
                    rejected_count += 1
                    continue

            verified[labels == label_idx] = 255

        fidelity_score = max(0.0, 1.0 - (rejected_count / total_fg_components))
        return verified, round(fidelity_score, 3)

    # =========================================================================
    # PHASE 24 & 25: QUALITY SCORE & QUALITY CATEGORIES
    # =========================================================================
    @staticmethod
    def compute_quality_score(
        prob_map: np.ndarray,
        binary_mask: np.ndarray,
        char_h: float,
        comp_count: int,
        ms_agreement: float,
        fidelity_score: float
    ) -> Tuple[float, str]:
        """
        Computes composite Binarization Quality Score from:
          - foreground plausibility
          - probability confidence (P95, P99)
          - component plausibility
          - multi-scale agreement
          - fidelity score
        Categorizes result:
          A: Strong continuous inscription structures
          B: Good inscription structures with moderate noise
          C: Partially usable inscription
          D: Model cannot reliably isolate inscription (Information-Limited)
        """
        fg_ratio = float(np.mean(binary_mask == 255))
        p95 = float(np.percentile(prob_map, 95))
        p_max = float(np.max(prob_map))

        # Scoring components [0 - 100]
        # 1. Confidence score
        conf_score = min(35.0, (p95 * 20.0 + p_max * 15.0))
        # 2. Foreground plausibility (ideal 3% - 25%)
        if 0.02 <= fg_ratio <= 0.30:
            fg_score = 25.0
        elif 0.005 <= fg_ratio < 0.02 or 0.30 < fg_ratio <= 0.45:
            fg_score = 15.0
        elif 0.001 <= fg_ratio < 0.005:
            fg_score = 8.0
        else:
            fg_score = 2.0

        # 3. Component plausibility
        if comp_count >= 30 and char_h >= 10.0:
            comp_score = 20.0
        elif comp_count >= 10:
            comp_score = 14.0
        elif comp_count >= 3:
            comp_score = 8.0
        else:
            comp_score = 2.0

        # 4. Multi-scale & fidelity score
        coherence_score = (ms_agreement * 10.0 + fidelity_score * 10.0)

        total_score = conf_score + fg_score + comp_score + coherence_score
        total_score = min(100.0, max(0.0, total_score))

        if total_score >= 70.0 and fg_ratio >= 0.01:
            category = "A - STRONG_INSCRIPTION"
        elif total_score >= 50.0 and fg_ratio >= 0.005:
            category = "B - GOOD_INSCRIPTION"
        elif total_score >= 30.0 and fg_ratio >= 0.001:
            category = "C - PARTIALLY_USABLE"
        else:
            category = "D - INFORMATION_LIMITED"

        return round(total_score, 1), category

    # =========================================================================
    # PHASE 31: COMPLETE PRODUCTION BINARIZATION PIPELINE
    # =========================================================================
    def binarize_inscription(
        self,
        raw_bgr: np.ndarray,
        v3_bgr: np.ndarray,
        filename: str = "inscription",
        primary_threshold: float = 0.50
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Executes the full two-stage binarization pipeline with adapter selection,
        coarse validation, dynamic patching, adaptive thresholding, and quality gate.
        Returns:
          - final_binary_ocr: uint8 (255 background, 0 inscription text - ready for OCR)
          - final_mask_raw: uint8 (255 text, 0 background)
          - diagnostics_dict: comprehensive metadata dictionary
        """
        start_time = time.time()
        diagnostics: Dict[str, Any] = {
            "filename": filename,
            "status": "INITIATED",
            "fallback_used": "NONE",
            "failure_reason": "NONE"
        }

        h_orig, w_orig = raw_bgr.shape[:2]
        scale_factor = 1.0
        # Official ShilaLekhya RESIZE_SIZE = 1536
        if max(h_orig, w_orig) > 1536:
            scale_factor = 1536.0 / float(max(h_orig, w_orig))
            scaled_w = int(w_orig * scale_factor)
            scaled_h = int(h_orig * scale_factor)
            raw_proc = cv2.resize(raw_bgr, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)
            v3_proc = cv2.resize(v3_bgr, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)
        else:
            raw_proc = raw_bgr.copy()
            v3_proc = v3_bgr.copy()

        # Step 1: Generate Model Input Variants
        input_variants = self.create_model_inputs(raw_proc, v3_proc)

        # Step 2: Input Compatibility Screening (PHASE 7)
        # Select best input branch based on Stage 1 confidence and coherence
        best_branch = "D_ADAPTED_V3"
        best_coarse = None
        best_scales = None
        best_ms_agree = 0.0
        best_p95 = -1.0
        best_char_h = 0.0
        best_comp_count = 0

        # Test Branch D (Adapted V3) first as primary research candidate,
        # fallback to Branch A (RAW) or Branch B (V3) if confidence is higher
        for branch_name in ["D_ADAPTED_V3", "A_RAW", "B_V3"]:
            c_prob, s_preds, ms_agr = self.run_stage1_multiscale(input_variants[branch_name], fusion_method="max")
            p95 = float(np.percentile(c_prob, 95))
            c_h, c_count, _ = self.estimate_character_height(c_prob, threshold=0.45)

            if p95 > best_p95 or (best_coarse is None):
                best_branch = branch_name
                best_coarse = c_prob
                best_scales = s_preds
                best_ms_agree = ms_agr
                best_p95 = p95
                best_char_h = c_h
                best_comp_count = c_count

        diagnostics["input_branch"] = best_branch
        diagnostics["stage1_max_probability"] = round(float(np.max(best_coarse)), 4)
        diagnostics["stage1_mean_probability"] = round(float(np.mean(best_coarse)), 4)
        diagnostics["stage1_foreground_ratio"] = round(float(np.mean(best_coarse > primary_threshold)), 4)
        diagnostics["stage1_component_count"] = best_comp_count
        diagnostics["multi_scale_agreement"] = round(best_ms_agree, 3)

        # Step 3: Phase 2 Coarse Prediction Inspection & Fallback Logic
        coarse_fg_ratio = diagnostics["stage1_foreground_ratio"]
        is_coarse_failure = bool(coarse_fg_ratio < 0.001 or best_comp_count < 2)

        if is_coarse_failure:
            diagnostics["coarse_status"] = "COARSE_PREDICTION_FAILURE"
            diagnostics["fallback_used"] = "AVERAGE_FUSION_RELAXED_THRESHOLD"
            # Try average fusion across scales as alternative
            coarse_alt = np.mean(np.stack(list(best_scales.values())), axis=0)
            alt_h, alt_count, _ = self.estimate_character_height(coarse_alt, threshold=0.35)
            if alt_count > best_comp_count:
                best_coarse = coarse_alt
                best_char_h = alt_h
                best_comp_count = alt_count

        # Estimate robust character height for Stage 2
        robust_h, valid_ccs, h_info = self.estimate_character_height(best_coarse, threshold=0.45)
        if robust_h < 12.0:
            # Conservative default character-height fallback (Phase 9)
            robust_h = 35.0
            diagnostics["fallback_used"] += "+DEFAULT_CHAR_HEIGHT_FALLBACK"

        diagnostics["estimated_character_height"] = round(robust_h, 1)

        # Step 4: Stage 2 Context-Aware Dynamic Patching (PHASE 10-13)
        # Select patch multipliers and run refinement
        selected_input_rgb = input_variants[best_branch]
        p_final = self.run_stage2_dynamic_patching(
            selected_input_rgb,
            best_coarse,
            base_char_h=robust_h,
            h_range=(4.0, 9.0),
            patch_counts=(90, 20)
        )

        diagnostics["stage2_foreground_ratio"] = round(float(np.mean(p_final > primary_threshold)), 4)

        # Step 5: Phase 14 & 15 Final Probability Map & Adaptive Thresholding
        chosen_threshold = primary_threshold
        final_fg_05 = float(np.mean(p_final > 0.50))

        # Check for blank output (Phase 16)
        if final_fg_05 < 0.002:
            # Diagnostic threshold search across [0.30 - 0.45]
            for candidate_th in [0.45, 0.40, 0.35, 0.30]:
                c_fg = float(np.mean(p_final > candidate_th))
                if c_fg >= 0.005:
                    chosen_threshold = candidate_th
                    diagnostics["fallback_used"] += f"+ADAPTIVE_THRESHOLD_{candidate_th}"
                    break
            else:
                # If still very low, use 0.30 as lower bound
                chosen_threshold = 0.30

        # Check for over-saturation / all-black failure (Phase 17)
        if float(np.mean(p_final > chosen_threshold)) > 0.40:
            for candidate_th in [0.55, 0.60, 0.65]:
                c_fg = float(np.mean(p_final > candidate_th))
                if c_fg <= 0.30:
                    chosen_threshold = candidate_th
                    break

        diagnostics["final_threshold"] = chosen_threshold
        raw_binary_mask = (p_final > chosen_threshold).astype(np.uint8) * 255

        # Step 6: Phase 18 Conservative Binary Cleanup
        cleaned_mask = self.conservative_cleanup(raw_binary_mask, min_area=8)

        # Step 7: Phase 19 Original-Image Fidelity Check
        verified_mask, fidelity_score = self.verify_original_fidelity(cleaned_mask, raw_proc, v3_proc, p_final)
        diagnostics["background_false_positive_score"] = round(1.0 - fidelity_score, 3)
        diagnostics["structural_coherence"] = round(fidelity_score, 3)

        # Calculate final foreground ratio
        final_fg_ratio = float(np.mean(verified_mask == 255))
        diagnostics["final_foreground_ratio"] = round(final_fg_ratio, 4)

        # Calculate Artifact Score (blockiness & patch seams)
        h_img, w_img = verified_mask.shape[:2]
        # Seam and high-frequency discontinuity check
        diff_y = np.abs(p_final[1:, :] - p_final[:-1, :])
        seam_grad = float(np.mean(diff_y))
        diagnostics["artifact_score"] = round(seam_grad, 4)

        # Step 8: Phase 24 & 25 Quality Score & Category Gate
        q_score, q_cat = self.compute_quality_score(
            p_final,
            verified_mask,
            robust_h,
            best_comp_count,
            best_ms_agree,
            fidelity_score
        )
        diagnostics["quality_score"] = q_score
        diagnostics["quality_category"] = q_cat

        # Evaluate acceptance criteria
        if final_fg_ratio < 0.0005:
            diagnostics["status"] = "REJECTED_BLANK"
            diagnostics["failure_reason"] = "INFORMATION_LIMITED_BELOW_DETECTION_THRESHOLD"
        elif final_fg_ratio > 0.45:
            diagnostics["status"] = "REJECTED_OVERSATURATED"
            diagnostics["failure_reason"] = "BACKGROUND_DOMINANCE"
        else:
            diagnostics["status"] = "SUCCESS"

        # Map binary mask back to 1:1 original resolution if scaled
        if scale_factor != 1.0:
            final_mask_orig = cv2.resize(verified_mask, (w_orig, h_orig), interpolation=cv2.INTER_NEAREST)
        else:
            final_mask_orig = verified_mask

        # Format output for OCR: 3-channel BGR image with black text on pure white background
        ocr_bgr = np.full((h_orig, w_orig, 3), 255, dtype=np.uint8)
        ocr_bgr[final_mask_orig == 255] = [0, 0, 0]

        diagnostics["inference_time_sec"] = round(time.time() - start_time, 2)
        return ocr_bgr, final_mask_orig, diagnostics
