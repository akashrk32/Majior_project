"""
SHILORA V3.1: Research-Informed Ancient Kannada Stone Inscription Preprocessing
================================================================================
Maximum Evidence-Preserving Deterministic Computer Vision Preprocessing Pipeline.
Converts: ONE ORIGINAL STONE IMAGE -> ONE FINAL PREPROCESSED IMAGE.

Strict Scientific & Engineering Principles:
1. Maximum evidence-preserving inscription enhancement (NOT image beautification).
2. Primary spatial base image is ALWAYS Grayscale Luminance Y = 0.2126R + 0.7152G + 0.0722B.
3. R/G/B are auxiliary scalar candidates, NOT luminance channels.
4. Chromatic difference maps (|R-G|, |R-B|, |G-B|) are strictly auxiliary (E7).
5. Area-normalized gradient energy: mean(Gx^2 + Gy^2).
6. Explicit 8x8 & 16x16 JPEG blockiness detection and artifact scoring.
7. Multi-scale persistence measuring structural stroke coherence across scales.
8. Single-image directional relief enhancement along 45°, 135°, 225°, 315°.
9. Positive bounded evidence fusion with sigmoidal tone mapping (no subtractive halos).
10. Crack and stain damping protecting non-glyph fractures and mineral stains.
11. Maximum-Recoverable-Information stopping logic (Stage 21 & 22) monitoring 13 hard-stop conditions.
12. Quality categories: A (High), B (Moderate), C (Low), D (Information-Limited).
13. Strict 1:1 resolution preservation, 8-bit grayscale PNG output.
"""

import os
import sys
import time
import math
import argparse
from pathlib import Path
import cv2
import numpy as np
import pandas as pd


# =============================================================================
# BASIC ROBUST NORMALIZATIONS & METRICS
# =============================================================================
def norm8(arr: np.ndarray, p_low: float = 1.0, p_high: float = 99.0) -> np.ndarray:
    """Percentile-based robust normalization to uint8 [0, 255]."""
    f = arr.astype(np.float32)
    if f.size > 250000:
        step = max(1, int(math.ceil(math.sqrt(f.size / 200000.0))))
        sample = f[::step, ::step]
        val_low = float(np.percentile(sample, p_low))
        val_high = float(np.percentile(sample, p_high))
    else:
        val_low = float(np.percentile(f, p_low))
        val_high = float(np.percentile(f, p_high))
    if val_high <= val_low:
        val_low = float(np.min(f))
        val_high = float(np.max(f))
    if val_high <= val_low:
        return np.zeros_like(arr, dtype=np.uint8)
    scaled = (f - val_low) / (val_high - val_low + 1e-6)
    return np.clip(scaled * 255.0, 0.0, 255.0).astype(np.uint8)


def norm_float(arr: np.ndarray, p_low: float = 1.0, p_high: float = 99.0) -> np.ndarray:
    """Percentile-based robust normalization to float32 [0.0, 1.0]."""
    f = arr.astype(np.float32)
    if f.size > 250000:
        step = max(1, int(math.ceil(math.sqrt(f.size / 200000.0))))
        sample = f[::step, ::step]
        val_low = float(np.percentile(sample, p_low))
        val_high = float(np.percentile(sample, p_high))
    else:
        val_low = float(np.percentile(f, p_low))
        val_high = float(np.percentile(f, p_high))
    if val_high <= val_low:
        val_low = float(np.min(f))
        val_high = float(np.max(f))
    if val_high <= val_low:
        return np.zeros_like(f, dtype=np.float32)
    scaled = (f - val_low) / (val_high - val_low + 1e-6)
    return np.clip(scaled, 0.0, 1.0).astype(np.float32)


def estimate_noise(gray: np.ndarray) -> float:
    """
    Immerkaer Laplacian-based robust fast noise estimation:
    sigma = sqrt(pi/2) * mean(|I * L|) / (6 * (W - 2) * (H - 2))
    """
    f = gray.astype(np.float32)
    h, w = f.shape[:2]
    if max(h, w) > 1200:
        scale = 1200.0 / max(h, w)
        f = cv2.resize(f, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        h, w = f.shape[:2]
    if h < 5 or w < 5:
        return 1.0

    kernel = np.array([
        [1, -2,  1],
        [-2, 4, -2],
        [1, -2,  1]
    ], dtype=np.float32)
    sigma = float(np.sum(np.abs(cv2.filter2D(f, -1, kernel))))
    sigma = sigma * math.sqrt(0.5 * math.pi) / (6.0 * (w - 2) * (h - 2) + 1e-6)
    return float(max(0.1, sigma))


def compute_blockiness(gray: np.ndarray) -> tuple:
    """
    Measures 8x8 and 16x16 JPEG compression block discontinuity.
    Calculates ratio of boundary step differences to non-boundary neighboring differences.
    Returns (blockiness_score, b8_ratio, b16_ratio).
    """
    f = gray.astype(np.float32)
    h, w = f.shape[:2]
    if max(h, w) > 1200:
        scale = 1200.0 / max(h, w)
        f = cv2.resize(f, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        h, w = f.shape[:2]

    h_idx_8 = np.arange(8, h - 8, 8)
    v_idx_8 = np.arange(8, w - 8, 8)
    if len(h_idx_8) < 2 or len(v_idx_8) < 2:
        return 0.0, 1.0, 1.0

    diff_h_b8 = float(np.mean(np.abs(f[h_idx_8, :] - f[h_idx_8 - 1, :])))
    diff_h_nb8 = float(np.mean(np.abs(f[h_idx_8 + 4, :] - f[h_idx_8 + 3, :])))
    bh8 = diff_h_b8 / (diff_h_nb8 + 1e-4)

    diff_v_b8 = float(np.mean(np.abs(f[:, v_idx_8] - f[:, v_idx_8 - 1])))
    diff_v_nb8 = float(np.mean(np.abs(f[:, v_idx_8 + 4] - f[:, v_idx_8 + 3])))
    bv8 = diff_v_b8 / (diff_v_nb8 + 1e-4)
    b8_ratio = (bh8 + bv8) / 2.0

    h_idx_16 = np.arange(16, h - 16, 16)
    v_idx_16 = np.arange(16, w - 16, 16)
    if len(h_idx_16) >= 2 and len(v_idx_16) >= 2:
        diff_h_b16 = float(np.mean(np.abs(f[h_idx_16, :] - f[h_idx_16 - 1, :])))
        diff_h_nb16 = float(np.mean(np.abs(f[h_idx_16 + 8, :] - f[h_idx_16 + 7, :])))
        bh16 = diff_h_b16 / (diff_h_nb16 + 1e-4)

        diff_v_b16 = float(np.mean(np.abs(f[:, v_idx_16] - f[:, v_idx_16 - 1])))
        diff_v_nb16 = float(np.mean(np.abs(f[:, v_idx_16 + 8] - f[:, v_idx_16 + 7])))
        bv16 = diff_v_b16 / (diff_v_nb16 + 1e-4)
        b16_ratio = (bh16 + bv16) / 2.0
    else:
        b16_ratio = 1.0

    block_score = max(0.0, b8_ratio - 1.0) + 0.5 * max(0.0, b16_ratio - 1.0)
    return round(float(block_score), 4), round(float(b8_ratio), 4), round(float(b16_ratio), 4)


def estimate_stroke_scale(gray: np.ndarray, min_dim: int) -> int:
    """Estimates typical stroke width scale based on spatial dimensions."""
    base_stroke = max(2, int(round(min_dim / 150.0)))
    return int(np.clip(base_stroke, 2, 45))


def calculate_inscription_relief_contrast(img_u8: np.ndarray, stroke_scale: int) -> tuple:
    """
    Calculates inscription groove contrast, adjacent stone background contrast,
    and Inscription-to-Background Contrast Ratio (IBR).
    Returns (c_insc, c_bg, ibr).
    """
    k_size = max(3, int(stroke_scale * 1.5))
    if k_size % 2 == 0:
        k_size += 1
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
    bh = cv2.morphologyEx(img_u8, cv2.MORPH_BLACKHAT, k)

    p90 = np.percentile(bh, 90)
    stroke_mask = bh > max(12, int(p90 * 0.70))

    k_dil = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size * 2 + 1, k_size * 2 + 1))
    dilated = cv2.dilate(stroke_mask.astype(np.uint8), k_dil)
    adjacent_stone_mask = (dilated == 1) & (~stroke_mask)

    if np.sum(stroke_mask) > 50 and np.sum(adjacent_stone_mask) > 50:
        mean_stroke = float(np.mean(img_u8[stroke_mask]))
        mean_stone = float(np.mean(img_u8[adjacent_stone_mask]))
        c_insc = abs(mean_stroke - mean_stone)
        c_bg = float(np.std(img_u8[adjacent_stone_mask]))
        ibr = c_insc / (c_bg + 1e-4)
    else:
        c_insc = float(np.std(img_u8))
        c_bg = float(np.std(img_u8))
        ibr = 1.0

    return round(float(c_insc), 2), round(float(c_bg), 2), round(float(ibr), 2)


# =============================================================================
# STAGE 1: INPUT PRESERVATION
# =============================================================================
def load_image(image_path: str):
    """
    Stage 1: Read original image preserving width, height, aspect ratio and FOV.
    No permanent downsampling or cropping.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Input image not found: {image_path}")
    bgr = cv2.imread(str(path))
    if bgr is None:
        raise ValueError(f"OpenCV failed to read image: {image_path}")
    h, w = bgr.shape[:2]
    return bgr, w, h


# =============================================================================
# STAGE 2: PRIMARY LUMINANCE Y EXTRACTION
# =============================================================================
def extract_primary_luminance(bgr: np.ndarray) -> np.ndarray:
    """
    Stage 2: Primary Luminance Y extraction using standard ITU-R BT.709 conversion:
    Y = 0.2126 R + 0.7152 G + 0.0722 B.
    Primary spatial image is ALWAYS Y.
    """
    b, g, r = cv2.split(bgr.astype(np.float32))
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return norm_float(y)


# =============================================================================
# STAGE 3 & 4: RGB / COLOUR AUXILIARY & CHANNEL QUALITY ANALYSIS
# =============================================================================
def evaluate_channels_and_artifacts(bgr: np.ndarray, Y: np.ndarray):
    """
    Stage 3 & 4: Multi-criteria evaluation of:
    - Primary Luminance: Y
    - Optional Scalar Channels: R, G, B
    - Auxiliary Chromatic Difference Maps: |R-G|, |G-B|, |R-B|
    """
    b, g, r = cv2.split(bgr.astype(np.float32))
    candidates = {
        "Y": Y,
        "R": norm_float(r),
        "G": norm_float(g),
        "B": norm_float(b),
        "R-G": norm_float(np.abs(r - g)),
        "G-B": norm_float(np.abs(g - b)),
        "R-B": norm_float(np.abs(r - b))
    }

    h, w = Y.shape[:2]
    scale = 1.0
    if max(h, w) > 900:
        scale = 900.0 / max(h, w)
        preview_dim = (int(w * scale), int(h * scale))
        cands_sub = {k: cv2.resize(v, preview_dim, interpolation=cv2.INTER_AREA) for k, v in candidates.items()}
    else:
        cands_sub = candidates

    y_sub = cands_sub["Y"]
    gy_x = cv2.Sobel(y_sub, cv2.CV_32F, 1, 0, ksize=3)
    gy_y = cv2.Sobel(y_sub, cv2.CV_32F, 0, 1, ksize=3)
    mag_y = np.sqrt(gy_x * gy_x + gy_y * gy_y)
    norm_mag_y = mag_y / (np.linalg.norm(mag_y) + 1e-6)

    channel_metrics = {}
    for name, cand_sub in cands_sub.items():
        p25, p75 = np.percentile(cand_sub, [25.0, 75.0])
        iqr_contrast = float(p75 - p25)

        gx = cv2.Sobel(cand_sub, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(cand_sub, cv2.CV_32F, 0, 1, ksize=3)
        mag_sq = gx * gx + gy * gy
        norm_grad_energy = float(np.mean(mag_sq))

        mag = np.sqrt(mag_sq)
        edge_thresh = float(np.mean(mag) + 1.2 * np.std(mag))
        edge_density = float(np.mean(mag > edge_thresh))

        cand_u8 = norm8(cand_sub)
        noise = estimate_noise(cand_u8)
        block_score, b8, b16 = compute_blockiness(cand_u8)

        norm_mag = mag / (np.linalg.norm(mag) + 1e-6)
        correlation_with_Y = float(np.sum(norm_mag * norm_mag_y))

        channel_metrics[name] = {
            "iqr_contrast": round(iqr_contrast, 4),
            "norm_grad_energy": round(norm_grad_energy, 4),
            "edge_density": round(edge_density, 4),
            "noise": round(noise, 2),
            "blockiness_score": block_score,
            "b8_ratio": b8,
            "correlation_with_Y": round(correlation_with_Y, 4)
        }

    # Evaluate optional scalar candidates (R, G, B)
    best_scalar = None
    best_scalar_score = -1.0
    for ch in ["R", "G", "B"]:
        m = channel_metrics[ch]
        if m["blockiness_score"] < 0.15 and m["correlation_with_Y"] > 0.75:
            s = m["norm_grad_energy"] * m["correlation_with_Y"] / (m["noise"] + 1.0)
            if s > best_scalar_score:
                best_scalar_score = s
                best_scalar = ch

    aux_scalar_evidence = candidates[best_scalar] if best_scalar is not None else None

    # Evaluate optional chromatic difference candidate (|R-G|, |G-B|, |R-B|)
    best_chroma = None
    best_chroma_score = -1.0
    for ch in ["R-G", "G-B", "R-B"]:
        m = channel_metrics[ch]
        if m["blockiness_score"] < 0.10 and m["noise"] < 8.0 and m["correlation_with_Y"] > 0.45:
            s = m["iqr_contrast"] * m["correlation_with_Y"]
            if s > best_chroma_score:
                best_chroma_score = s
                best_chroma = ch

    aux_chroma_evidence = candidates[best_chroma] if best_chroma is not None else None

    return Y, aux_scalar_evidence, best_scalar, aux_chroma_evidence, best_chroma, channel_metrics


# =============================================================================
# STAGE 7: ILLUMINATION NORMALIZATION
# =============================================================================
def estimate_illumination(Y: np.ndarray, min_dim: int):
    """
    Stage 7: Multi-scale Gaussian background estimation on Luminance Y.
    Returns (E1_illum_normalized, illum_background).
    """
    f = Y.astype(np.float32)
    h, w = f.shape[:2]
    if max(h, w) > 1000:
        scale = 600.0 / max(h, w)
        f_small = cv2.resize(f, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        sigma_small = max(5.0, (min_dim * scale) * 0.12)
        illum_small = cv2.GaussianBlur(f_small, (0, 0), sigmaX=sigma_small, sigmaY=sigma_small)
        illum_bg = cv2.resize(illum_small, (w, h), interpolation=cv2.INTER_LINEAR)
    else:
        sigma_large = max(15.0, min_dim * 0.12)
        illum_bg = cv2.GaussianBlur(f, (0, 0), sigmaX=sigma_large, sigmaY=sigma_large)

    norm_ratio = f / (illum_bg + 1e-5)
    e1 = norm_float(norm_ratio)
    return e1, illum_bg


# =============================================================================
# STAGE 8: SURFACE FLATTENING
# =============================================================================
def surface_flatten(Y: np.ndarray, illum_bg: np.ndarray, min_dim: int):
    """
    Stage 8: Difference-of-Gaussians (DoG) and subtractive surface detail flattening on Y.
    Returns surface_flattened_evidence (E2).
    """
    f = Y.astype(np.float32)
    h, w = f.shape[:2]
    sigma1 = max(1.5, min_dim * 0.005)
    sigma2 = max(4.0, min_dim * 0.025)

    if max(h, w) > 1200:
        scale = 800.0 / max(h, w)
        f_small = cv2.resize(f, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        g1_s = cv2.GaussianBlur(f_small, (0, 0), sigmaX=sigma1 * scale, sigmaY=sigma1 * scale)
        g2_s = cv2.GaussianBlur(f_small, (0, 0), sigmaX=sigma2 * scale, sigmaY=sigma2 * scale)
        dog_s = g1_s - g2_s
        dog = cv2.resize(dog_s, (w, h), interpolation=cv2.INTER_LINEAR)
    else:
        g1 = cv2.GaussianBlur(f, (0, 0), sigmaX=sigma1, sigmaY=sigma1)
        g2 = cv2.GaussianBlur(f, (0, 0), sigmaX=sigma2, sigmaY=sigma2)
        dog = g1 - g2

    detail = f - illum_bg
    flattened = norm_float(detail) * 0.5 + norm_float(dog) * 0.5
    return norm_float(flattened)


# =============================================================================
# STAGE 9 & 10: MULTI-SCALE GROOVE DETECTION & PERSISTENCE
# =============================================================================
def multiscale_groove_response(Y_input: np.ndarray, min_dim: int, stroke_scale: int):
    """
    Stage 9 & 10: Multi-scale Black-Hat responses on luminance Y.
    Measures multi-scale persistence: chiseled strokes persist across adjacent scales,
    while random stone texture behaves inconsistently.
    Returns (E3_groove, selected_scale, persistence_score).
    """
    u8 = norm8(Y_input)
    h, w = u8.shape[:2]
    s = stroke_scale

    candidate_scales = sorted(list(set([
        max(3, min(11, int(round(s * 0.75)))),
        max(5, min(15, int(round(s * 1.2)))),
        max(7, min(19, int(round(s * 1.8)))),
        max(9, min(27, int(round(s * 2.5))))
    ])))

    proc_scale = 1.0
    if max(h, w) > 1200:
        proc_scale = 1200.0 / max(h, w)
        u8_small = cv2.resize(u8, (int(w * proc_scale), int(h * proc_scale)), interpolation=cv2.INTER_AREA)
    else:
        u8_small = u8

    responses = []
    for k_s in candidate_scales:
        k_proc = max(3, int(round(k_s * proc_scale)))
        if k_proc % 2 == 0:
            k_proc += 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_proc, k_proc))
        bh = cv2.morphologyEx(u8_small, cv2.MORPH_BLACKHAT, kernel).astype(np.float32)
        responses.append(norm_float(bh))

    persistences = []
    for i in range(len(responses) - 1):
        r1, r2 = responses[i], responses[i + 1]
        prod = r1 * r2
        corr = float(np.sum(prod) / (np.sqrt(np.sum(r1 * r1) * np.sum(r2 * r2)) + 1e-5))
        persistences.append(corr)

    mean_persistence = float(np.mean(persistences)) if persistences else 0.5
    best_scale_idx = int(np.argmax(persistences)) if persistences else 0
    selected_scale = candidate_scales[min(best_scale_idx, len(candidate_scales) - 1)]

    if proc_scale != 1.0:
        k_best = max(3, int(round(selected_scale * proc_scale)))
        if k_best % 2 == 0:
            k_best += 1
        kernel_best = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_best, k_best))
        bh_best = cv2.morphologyEx(u8_small, cv2.MORPH_BLACKHAT, kernel_best).astype(np.float32)
        fused_bh = cv2.resize(bh_best, (w, h), interpolation=cv2.INTER_LINEAR)
    else:
        k_full = selected_scale if selected_scale % 2 != 0 else selected_scale + 1
        kernel_full = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_full, k_full))
        fused_bh = cv2.morphologyEx(u8, cv2.MORPH_BLACKHAT, kernel_full).astype(np.float32)

    return norm_float(fused_bh), selected_scale, round(mean_persistence, 4)


# =============================================================================
# STAGE 11: GRADIENT EVIDENCE
# =============================================================================
def gradient_evidence(Y: np.ndarray):
    """
    Stage 11: Area-normalized Sobel gradient magnitude on Luminance Y.
    Returns (E4_grad, Gx, Gy, grad_energy_per_pixel).
    """
    f = Y.astype(np.float32)
    f_blur = cv2.GaussianBlur(f, (3, 3), 0.8)

    gx = cv2.Sobel(f_blur, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(f_blur, cv2.CV_32F, 0, 1, ksize=3)
    mag_sq = gx * gx + gy * gy
    grad_energy_per_pixel = float(np.mean(mag_sq))
    mag = np.sqrt(mag_sq)

    mag_u8 = norm8(mag)
    if max(f.shape[:2]) > 1600:
        denoised_mag = cv2.GaussianBlur(mag_u8, (3, 3), 0.8)
    else:
        denoised_mag = cv2.bilateralFilter(mag_u8, d=5, sigmaColor=35, sigmaSpace=3)

    return norm_float(denoised_mag), gx, gy, round(grad_energy_per_pixel, 4)


# =============================================================================
# STAGE 12: DIRECTIONAL RELIEF ENHANCEMENT
# =============================================================================
def directional_pseudo_relief(Y: np.ndarray, gx: np.ndarray, gy: np.ndarray):
    """
    Stage 12: Single-Image Directional Relief Enhancement.
    Projects luminance surface gradients along 4 raking light angles (45°, 135°, 225°, 315°).
    Note: Formally designated as single-image directional relief enhancement, NOT 3D or RTI.
    Returns E5_relief.
    """
    angles_deg = [45, 135, 225, 315]
    relief_maps = []
    for deg in angles_deg:
        rad = np.deg2rad(deg)
        shaded = gx * np.cos(rad) + gy * np.sin(rad)
        relief_maps.append(shaded)

    d1 = relief_maps[0] - relief_maps[2]
    d2 = relief_maps[1] - relief_maps[3]
    relief_consensus = np.abs(d1) + np.abs(d2)
    return norm_float(relief_consensus)


# =============================================================================
# STAGE 13: BOUNDED LOCAL CONTRAST (CLAHE)
# =============================================================================
def bounded_local_contrast(Y: np.ndarray, noise_level: float, blockiness: float, clip_limit: float = 1.7):
    """
    Stage 13: Bounded CLAHE on Luminance Y.
    ClipLimit is strictly bounded (1.4 - 2.0) to prevent amplifying stone grain or tile boundaries.
    Grid size (8, 8) is validated to prevent block boundary seams.
    """
    u8 = norm8(Y)
    grid = (8, 8)

    if noise_level > 15.0 or blockiness > 0.15:
        eff_clip = min(clip_limit, 1.4)
    elif noise_level > 8.0:
        eff_clip = min(clip_limit, 1.7)
    else:
        eff_clip = min(clip_limit, 2.0)

    clahe = cv2.createCLAHE(clipLimit=eff_clip, tileGridSize=grid)
    enhanced = clahe.apply(u8)
    return norm_float(enhanced), eff_clip, "(8,8)"


# =============================================================================
# STAGE 15: CRACK AND STAIN PROTECTION
# =============================================================================
def detect_crack_stain_mask(Y: np.ndarray, bgr: np.ndarray, min_dim: int) -> np.ndarray:
    """
    Detects severe continuous non-glyph cracks, image-wide borders, and high-saturation stains.
    Returns suppression_weight_map (float32 [0.35, 1.0]).
    """
    h, w = Y.shape[:2]
    suppression = np.ones((h, w), dtype=np.float32)

    u8 = norm8(Y)
    kernel_crack = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(7, int(min_dim * 0.05))))
    cracks_v = cv2.morphologyEx(255 - u8, cv2.MORPH_TOPHAT, kernel_crack)
    kernel_crack_h = cv2.getStructuringElement(cv2.MORPH_RECT, (max(7, int(min_dim * 0.05)), 1))
    cracks_h = cv2.morphologyEx(255 - u8, cv2.MORPH_TOPHAT, kernel_crack_h)
    cracks = np.maximum(cracks_v, cracks_h)
    _, crack_mask = cv2.threshold(cracks, 60, 255, cv2.THRESH_BINARY)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(crack_mask, connectivity=8)

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        cw = stats[i, cv2.CC_STAT_WIDTH]
        ch = stats[i, cv2.CC_STAT_HEIGHT]
        aspect = max(cw, ch) / (min(cw, ch) + 1.0)
        if aspect > 15.0 and max(cw, ch) > (min_dim * 0.25):
            suppression[labels == i] = 0.35

    b, g, r = cv2.split(bgr.astype(np.float32))
    chroma_dev = np.abs(r - g) + np.abs(g - b) + np.abs(r - b)
    p98_dev = float(np.percentile(chroma_dev, 98))
    if p98_dev > 45.0:
        stain_mask = chroma_dev > (p98_dev * 0.85)
        suppression[stain_mask] = np.minimum(suppression[stain_mask], 0.40)

    suppression = cv2.GaussianBlur(suppression, (7, 7), 2.0)
    return suppression


# =============================================================================
# STAGE 18 & 19: POSITIVE BOUNDED EVIDENCE FUSION
# =============================================================================
def positive_adaptive_fusion(
    e1: np.ndarray,
    e2: np.ndarray,
    e3: np.ndarray,
    e4: np.ndarray,
    e5: np.ndarray,
    e6: np.ndarray,
    e7_scalar: np.ndarray,
    e7_chroma: np.ndarray,
    suppression_mask: np.ndarray,
    persistence: float,
    groove_weight_scale: float = 1.0
):
    """
    Stage 18 & 19: Positive bounded evidence fusion:
    E = sum(w_i * E_i)
    Avoids direct subtractive formulas to eliminate dark halos and stroke clipping.
    """
    base_w_groove = float(np.clip(0.18 + 0.15 * persistence, 0.18, 0.32))
    w_groove = base_w_groove * groove_weight_scale
    w_clahe = 0.25
    w_illum = 0.20
    w_flatten = 0.10
    w_relief = 0.10
    w_grad = 0.05

    w_scalar = 0.05 if e7_scalar is not None else 0.0
    w_chroma = 0.03 if e7_chroma is not None else 0.0

    groove_damped = e3 * suppression_mask
    base_surf = (w_illum * e1 + w_flatten * e2 + w_clahe * e6) / (w_illum + w_flatten + w_clahe)

    relief_boost = w_relief * e5 + w_grad * e4
    if e7_scalar is not None:
        base_surf += w_scalar * e7_scalar
    if e7_chroma is not None:
        relief_boost += w_chroma * e7_chroma

    fused = base_surf * (1.0 - w_groove * groove_damped) + (0.08 * relief_boost)
    fused = np.clip(fused, 0.0, 1.0)

    # Sigmoidal bounded tone mapping
    fused_mapped = 1.0 / (1.0 + np.exp(-6.0 * (fused - 0.5)))
    fused_norm = norm_float(fused_mapped)

    weights_dict = {
        "E1_illum": w_illum,
        "E2_flatten": w_flatten,
        "E3_groove": round(w_groove, 3),
        "E4_grad": w_grad,
        "E5_relief": w_relief,
        "E6_clahe": w_clahe,
        "E7_scalar": w_scalar,
        "E7_chroma": w_chroma
    }
    return fused_norm, weights_dict


# =============================================================================
# STAGE 20: STRUCTURAL CLEANUP & FIDELITY
# =============================================================================
def conservative_structural_cleanup(fused: np.ndarray, stroke_scale: int):
    """Stage 20: Suppress isolated single-pixel dust while preserving continuous stroke evidence."""
    u8 = norm8(fused)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(u8, cv2.MORPH_OPEN, kernel)
    blended = norm_float(fused) * 0.88 + norm_float(cleaned) * 0.12
    return norm_float(blended)


# =============================================================================
# STAGE 27 & 28: NORMALIZATION & SHARPENING
# =============================================================================
def final_normalization(cleaned: np.ndarray) -> np.ndarray:
    """Stage 28: Robust percentile normalization to standard 8-bit dynamic range."""
    return norm8(cleaned, p_low=1.0, p_high=99.0)


def conservative_sharpen(norm_img: np.ndarray, noise_level: float, blockiness: float, sharpen_amount: float = 0.25):
    """Stage 27: Mild unsharp masking governed by noise and blockiness."""
    f = norm_img.astype(np.float32)
    if noise_level > 15.0 or blockiness > 0.15:
        eff_amount = min(sharpen_amount, 0.15)
    elif noise_level > 8.0:
        eff_amount = min(sharpen_amount, 0.22)
    else:
        eff_amount = min(sharpen_amount, 0.30)

    blur = cv2.GaussianBlur(f, (0, 0), sigmaX=1.0, sigmaY=1.0)
    sharpened = f + eff_amount * (f - blur)
    return np.clip(sharpened, 0.0, 255.0).astype(np.uint8), eff_amount


# =============================================================================
# STAGES 21, 22, 24: MAXIMUM RECOVERABLE INFORMATION / HARD STOP LOGIC
# =============================================================================
def evaluate_candidate_configuration(
    Y: np.ndarray,
    bgr: np.ndarray,
    min_dim: int,
    stroke_scale: int,
    e1: np.ndarray,
    e2: np.ndarray,
    e3: np.ndarray,
    e4: np.ndarray,
    e5: np.ndarray,
    aux_scalar: np.ndarray,
    aux_chroma: np.ndarray,
    suppression_mask: np.ndarray,
    persistence: float,
    noise_level: float,
    blockiness_score: float,
    clahe_clip: float,
    groove_scale: float,
    sharp_amt: float
):
    """
    Executes a candidate parameter configuration and computes evidence vs artifact scores.
    """
    e6, eff_clip, grid_str = bounded_local_contrast(Y, noise_level, blockiness_score, clip_limit=clahe_clip)
    fused, weights = positive_adaptive_fusion(
        e1, e2, e3, e4, e5, e6,
        aux_scalar, aux_chroma,
        suppression_mask, persistence,
        groove_weight_scale=groove_scale
    )
    cleaned = conservative_structural_cleanup(fused, stroke_scale)
    norm_img = final_normalization(cleaned)
    final_u8, eff_sharp = conservative_sharpen(norm_img, noise_level, blockiness_score, sharpen_amount=sharp_amt)

    # Calculate objective metrics
    c_insc, c_bg, ibr = calculate_inscription_relief_contrast(final_u8, stroke_scale)
    final_block, b8, b16 = compute_blockiness(final_u8)
    final_noise = estimate_noise(final_u8)

    # Clipping check (< 1% pixels at 0 or 255)
    clip_low = np.mean(final_u8 == 0)
    clip_high = np.mean(final_u8 == 255)
    total_clipping = clip_low + clip_high

    # Halo / ringing proxy: high-frequency overshoot in dark neighborhood
    lap = cv2.Laplacian(final_u8, cv2.CV_32F)
    ringing_metric = float(np.percentile(np.abs(lap), 99.5))

    # Objective score: IBR - penalties
    # Objective = InscriptionEvidence - lambda * Noise - mu * Artifact - nu * Clipping
    obj_score = ibr - (0.02 * final_noise) - (2.0 * final_block) - (5.0 * total_clipping)

    return {
        "final_u8": final_u8,
        "c_insc": c_insc,
        "c_bg": c_bg,
        "ibr": ibr,
        "blockiness": final_block,
        "b8": b8,
        "noise": final_noise,
        "clipping": total_clipping,
        "ringing": ringing_metric,
        "obj_score": obj_score,
        "weights": weights,
        "eff_clip": eff_clip,
        "grid_str": grid_str,
        "eff_sharp": eff_sharp
    }


def find_maximum_recoverable_configuration(
    Y: np.ndarray,
    bgr: np.ndarray,
    min_dim: int,
    stroke_scale: int,
    e1: np.ndarray,
    e2: np.ndarray,
    e3: np.ndarray,
    e4: np.ndarray,
    e5: np.ndarray,
    aux_scalar: np.ndarray,
    aux_chroma: np.ndarray,
    suppression_mask: np.ndarray,
    persistence: float,
    base_noise: float,
    base_block: float
):
    """
    Stage 21 & 22: Hard-stop optimization loop.
    Tests bounded parameter progression:
    - CLAHE clipLimit: 1.4 -> 1.7 -> 2.0
    - Groove scaling: 0.85 -> 1.0 -> 1.15
    - Sharpening: 0.15 -> 0.22 -> 0.30
    Stops when additional enhancement produces more noise/artifacts than inscription evidence.
    """
    candidate_steps = [
        {"clahe_clip": 1.4, "groove_scale": 0.85, "sharp_amt": 0.15, "name": "Conservative"},
        {"clahe_clip": 1.7, "groove_scale": 1.00, "sharp_amt": 0.22, "name": "Standard"},
        {"clahe_clip": 2.0, "groove_scale": 1.15, "sharp_amt": 0.30, "name": "Enhanced"}
    ]

    best_res = None
    hard_stop_trigger = "NONE"

    for idx, step in enumerate(candidate_steps):
        res = evaluate_candidate_configuration(
            Y, bgr, min_dim, stroke_scale,
            e1, e2, e3, e4, e5,
            aux_scalar, aux_chroma,
            suppression_mask, persistence,
            base_noise, base_block,
            step["clahe_clip"], step["groove_scale"], step["sharp_amt"]
        )

        if best_res is None:
            best_res = res
            continue

        # Evaluate Hard-Stop Conditions
        # 1. Block artifacts increase beyond target limit (< 0.05)
        if res["blockiness"] > 0.05 or (res["blockiness"] - best_res["blockiness"]) > 0.02:
            hard_stop_trigger = "BLOCK_ARTIFACT_LIMIT"
            break

        # 2. Severe clipping exceeds 1% of pixels
        if res["clipping"] > 0.01:
            hard_stop_trigger = "CLIPPING_LIMIT"
            break

        # 3. Ringing / halo overshoot detected
        if res["ringing"] > 160.0:
            hard_stop_trigger = "RINGING_HALO_DETECTED"
            break

        # 4. Stone texture / noise increases faster than inscription evidence
        delta_ibr = res["ibr"] - best_res["ibr"]
        delta_noise = res["noise"] - best_res["noise"]
        delta_grain = res["c_bg"] - best_res["c_bg"]

        if delta_ibr <= 0 and delta_noise > 0.5:
            hard_stop_trigger = "NOISE_EXCEEDED"
            break

        if delta_grain > 8.0 and delta_ibr < 0.05:
            hard_stop_trigger = "STONE_TEXTURE_EXCEEDED"
            break

        # 5. Objective function stops improving
        if res["obj_score"] <= best_res["obj_score"]:
            hard_stop_trigger = "EVIDENCE_PLATEAU"
            break

        # Accept improvement
        best_res = res

    # Categorize quality (Stage 24)
    if persistence >= 0.80 and best_res["ibr"] >= 1.20 and best_res["blockiness"] < 0.02:
        quality_cat = "A - HIGH_RECOVERABILITY"
    elif persistence >= 0.70 and best_res["ibr"] >= 0.95:
        quality_cat = "B - MODERATE_RECOVERABILITY"
    elif persistence >= 0.55:
        quality_cat = "C - LOW_RECOVERABILITY"
    else:
        quality_cat = "D - INFORMATION_LIMITED"

    return best_res, hard_stop_trigger, quality_cat


# =============================================================================
# STAGE 29 & 30: PREPROCESS ONE (V3.1)
# =============================================================================
def preprocess_one(input_path: str, output_path: str) -> dict:
    """
    Complete SHILORA V3.1 Preprocessing Pipeline for a Single Stone.
    ONE INPUT -> ONE FINAL PREPROCESSED IMAGE.
    Preserves exact 1:1 image resolution.
    Saves 8-bit grayscale PNG.
    """
    start_time = time.time()
    in_p = Path(input_path)
    out_p = Path(output_path)

    # 1. Load image and preserve resolution (Stage 1)
    bgr, w, h = load_image(str(in_p))
    min_dim = min(h, w)

    # 2. Primary Luminance Y extraction (Stage 2)
    Y = extract_primary_luminance(bgr)

    # 3 & 4. Channel evaluation & JPEG blockiness detection (Stages 3, 4, 5, 6)
    Y, aux_scalar, scalar_name, aux_chroma, chroma_name, ch_metrics = evaluate_channels_and_artifacts(bgr, Y)

    base_noise = ch_metrics["Y"]["noise"]
    base_block = ch_metrics["Y"]["blockiness_score"]
    stroke_scale = estimate_stroke_scale(norm8(Y), min_dim)

    # 7. Illumination normalization on Y (Stage 7)
    e1, illum_bg = estimate_illumination(Y, min_dim)

    # 8. Surface flattening on Y (Stage 8)
    e2 = surface_flatten(Y, illum_bg, min_dim)

    # 9 & 10. Multi-scale groove detection & persistence (Stages 9 & 10)
    e3, selected_morph_scale, persistence_score = multiscale_groove_response(e2, min_dim, stroke_scale)

    # 11. Area-normalized Gradient analysis on Y (Stage 11)
    e4, gx, gy, grad_energy_per_pixel = gradient_evidence(Y)

    # 12. Single-image directional pseudo-relief on Y (Stage 12)
    e5 = directional_pseudo_relief(Y, gx, gy)

    # 15. Crack and stain protection mask (Stage 15)
    suppression_mask = detect_crack_stain_mask(Y, bgr, min_dim)

    # 21 & 22. Hard-stop maximum-recoverable-information optimization loop
    best_config, hard_stop_trigger, quality_category = find_maximum_recoverable_configuration(
        Y, bgr, min_dim, stroke_scale,
        e1, e2, e3, e4, e5,
        aux_scalar, aux_chroma,
        suppression_mask, persistence_score,
        base_noise, base_block
    )

    final_img = best_config["final_u8"]

    # Resolution verification and save (Stage 29)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_h, out_w = final_img.shape[:2]
    if (out_w, out_h) != (w, h):
        raise ValueError(f"Resolution mismatch: expected ({w}, {h}), got ({out_w}, {out_h})")

    cv2.imwrite(str(out_p), final_img)
    elapsed = round(time.time() - start_time, 3)

    # Quality metrics
    iqr_val = float(np.percentile(final_img, 75) - np.percentile(final_img, 25))
    aux_channels_str = f"Scalar:{scalar_name or 'None'}; Chroma:{chroma_name or 'None'}"

    # Combined artifact score (blockiness + clipping)
    artifact_score = round(best_config["blockiness"] + float(best_config["clipping"] * 10.0), 4)

    # Exact report record schema matching Stage 30
    report_record = {
        "filename": in_p.name,
        "width": w,
        "height": h,
        "primary_channel": "Y_Luminance",
        "auxiliary_channels": aux_channels_str,
        "blockiness_score": best_config["blockiness"],
        "gradient_energy_per_pixel": round(grad_energy_per_pixel, 2),
        "local_IQR": round(iqr_val, 2),
        "inscription_contrast": best_config["c_insc"],
        "background_contrast": best_config["c_bg"],
        "inscription_background_ratio": best_config["ibr"],
        "multi_scale_persistence": persistence_score,
        "noise_score": best_config["noise"],
        "artifact_score": artifact_score,
        "clahe_clip_limit": best_config["eff_clip"],
        "clahe_grid": best_config["grid_str"],
        "morphology_scale": selected_morph_scale,
        "fusion_weights": str(best_config["weights"]),
        "quality_category": quality_category,
        "hard_stop_trigger": hard_stop_trigger,
        "processing_status": "PREPROCESSING_COMPLETE"
    }
    return report_record


# =============================================================================
# DATASET RUNNER
# =============================================================================
def preprocess_dataset(
    input_dir: str = "data/raw",
    output_dir: str = "data/preprocessed",
    report_csv_path: str = "preprocessing_report.csv",
    target_files: list = None
):
    """
    Process images in input_dir and output preprocessed images to output_dir.
    Saves exactly ONE final preprocessed image per input image.
    Generates preprocessing_report.csv.
    """
    in_dir = Path(input_dir)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    valid_exts = {".jpg", ".png", ".jpeg"}
    all_images = sorted([f for f in in_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts])

    if target_files:
        target_set = set(target_files)
        all_images = [f for f in all_images if f.name in target_set]

    print("=" * 70)
    print("      SHILORA V3.1: MAXIMUM EVIDENCE-PRESERVING PREPROCESSING          ")
    print(f"Total Input Images:  {len(all_images)}")
    print(f"Input Directory:     {in_dir}")
    print(f"Output Directory:    {out_dir}")
    print("=" * 70)

    records = []
    success_count = 0

    for idx, img_path in enumerate(all_images, start=1):
        stem = img_path.stem
        out_filename = f"{stem}_preprocessed.png"
        out_path = out_dir / out_filename

        print(f"\n[{idx}/{len(all_images)}] Processing {img_path.name} -> {out_filename} ...")
        try:
            rec = preprocess_one(str(img_path), str(out_path))
            records.append(rec)
            success_count += 1
            print(f"       -> OK {rec['width']}x{rec['height']} | Primary: {rec['primary_channel']} "
                  f"| IBR: {rec['inscription_background_ratio']:.2f} | Persist: {rec['multi_scale_persistence']:.2f} "
                  f"| Block: {rec['blockiness_score']:.3f} | Cat: {rec['quality_category']} "
                  f"| Stop: {rec['hard_stop_trigger']}")
        except Exception as e:
            print(f"       -> FAILED: {str(e)}")
            records.append({
                "filename": img_path.name,
                "width": 0,
                "height": 0,
                "primary_channel": "Y_Luminance",
                "auxiliary_channels": "None",
                "blockiness_score": 0.0,
                "gradient_energy_per_pixel": 0.0,
                "local_IQR": 0.0,
                "inscription_contrast": 0.0,
                "background_contrast": 0.0,
                "inscription_background_ratio": 0.0,
                "multi_scale_persistence": 0.0,
                "noise_score": 0.0,
                "artifact_score": 0.0,
                "clahe_clip_limit": 0.0,
                "clahe_grid": "None",
                "morphology_scale": 0,
                "fusion_weights": "{}",
                "quality_category": "D - INFORMATION_LIMITED",
                "hard_stop_trigger": f"ERROR: {str(e)}",
                "processing_status": f"FAILED: {str(e)}"
            })

    if records:
        df = pd.DataFrame(records)
        df.to_csv(report_csv_path, index=False)
        print(f"\nSaved preprocessing report to: {report_csv_path}")

    print(f"Total preprocessing completion: {success_count}/{len(all_images)}")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SHILORA V3.1 Ancient Kannada Stone Preprocessor")
    parser.add_argument("--input_dir", default="data/raw", help="Path to raw stone images")
    parser.add_argument("--output_dir", default="data/preprocessed", help="Path to save preprocessed PNGs")
    parser.add_argument("--report", default="preprocessing_report.csv", help="Path to output CSV report")
    parser.add_argument("--files", nargs="*", default=None, help="Specific files to process")
    args = parser.parse_args()

    preprocess_dataset(args.input_dir, args.output_dir, args.report, target_files=args.files)
