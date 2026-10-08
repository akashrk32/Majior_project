import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("Brahmi-OCR-main/backend").resolve()))

import cv2
import numpy as np
import json

from preprocessing import ShiloraStonePreprocessor

img_path = r"C:\Users\TEJAS M G\.gemini\antigravity-ide\brain\7d098130-659d-4128-b0cf-2785df3a7db0\.user_uploaded\media_1791384734075.jpg"
img_bgr = cv2.imread(img_path)
h, w = img_bgr.shape[:2]

# 1. Preprocessing
preprocessor = ShiloraStonePreprocessor()
preproc_res = preprocessor.process(img_bgr)
gray = preproc_res.final_natural # 02_preprocessed

# 2. Gradient of Gray Image for Grounding
gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
grad_mag = np.sqrt(gx**2 + gy**2)
grad_norm = cv2.normalize(grad_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
grad_edges = (grad_norm > 30).astype(np.uint8)

# Relief representation
k_size = 9
kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel_ellipse)
blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel_ellipse)
relief = cv2.normalize(cv2.subtract(blackhat, tophat), None, 0, 255, cv2.NORM_MINMAX)

# 3. Generate Candidates
# Candidate 1: Adaptive Gaussian Conservative
# To prevent speckle noise, gentle bilateral filter before threshold
smooth_gray = cv2.bilateralFilter(gray, 5, 40, 40)
c1 = cv2.adaptiveThreshold(smooth_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 5)
# Conservative closing to connect strokes
c1_closed = cv2.morphologyEx(c1, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))

# Candidate 2: Adaptive Gaussian Moderate
c2 = cv2.adaptiveThreshold(smooth_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 2)
c2_closed = cv2.morphologyEx(c2, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))

# Candidate 3: Relief-Enhanced Local Adaptive Threshold
c3 = cv2.adaptiveThreshold(relief, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, -3)

# Candidate 4: Sauvola Local Contrast
mean = cv2.blur(gray.astype(np.float32), (25, 25))
sqr_mean = cv2.blur((gray.astype(np.float32))**2, (25, 25))
std = np.sqrt(np.maximum(0, sqr_mean - mean**2))
sauvola_th = mean * (1.0 + 0.25 * (std / 128.0 - 1.0))
c4 = (gray.astype(np.float32) < sauvola_th).astype(np.uint8) * 255

candidates = {
    "candidate_01": c1_closed,
    "candidate_02": c2_closed,
    "candidate_03": c3,
    "candidate_04": c4
}

def evaluate_stroke_quality(mask, gray_img, grad_edges_img):
    total_pixels = mask.size
    fg_pixels = np.sum(mask == 255)
    fg_ratio = fg_pixels / float(total_pixels)
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    areas = stats[1:, cv2.CC_STAT_AREA] if num_labels > 1 else np.array([0])
    cc_count = num_labels - 1
    
    if cc_count == 0 or fg_pixels == 0:
        return {"score": 0.0, "status": "FAILED_EMPTY"}
    
    med_area = float(np.median(areas))
    tiny_ratio = float(np.mean(areas < 15))
    frag_ratio = float(np.mean(areas < 30))
    
    # Gradient support: fraction of mask pixels supported by gradient
    grad_support = float(np.mean(grad_edges_img[mask == 255]))
    
    # Boundary overlap with gradients
    kernel_cross = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    dil = cv2.dilate(mask, kernel_cross)
    er = cv2.erode(mask, kernel_cross)
    boundary = (dil - er) > 0
    boundary_overlap = float(np.mean(grad_edges_img[boundary])) if np.sum(boundary) > 0 else 0.0
    
    # Stroke continuity via hit-or-miss skeleton analysis
    # Simple proxy: percentage of foreground pixels that have at least 2 neighbors
    neighbor_filter = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.uint8)
    neighbor_count = cv2.filter2D((mask == 255).astype(np.uint8), -1, neighbor_filter)
    stroke_continuity = float(np.mean((neighbor_count >= 2)[mask == 255]))
    
    # Background contamination: outer 3% margin density
    margin_mask = np.zeros_like(mask, dtype=bool)
    m_h, m_w = int(h * 0.03), int(w * 0.03)
    margin_mask[:m_h, :] = True
    margin_mask[-m_h:, :] = True
    margin_mask[:, :m_w] = True
    margin_mask[:, -m_w:] = True
    bg_contam = float(np.mean(mask[margin_mask] == 255))
    
    # Local contrast preservation: mean gray difference between FG and BG
    bg_pixels = gray_img[mask == 0]
    fg_gray_pixels = gray_img[mask == 255]
    mean_bg = np.mean(bg_pixels) if len(bg_pixels) > 0 else 128.0
    mean_fg = np.mean(fg_gray_pixels) if len(fg_gray_pixels) > 0 else 128.0
    local_contrast = max(0.0, min(1.0, float(abs(mean_bg - mean_fg) / 64.0)))
    
    # Composite Quality Score
    score = (
        0.25 * grad_support
        + 0.20 * boundary_overlap
        + 0.20 * (1.0 - frag_ratio)
        + 0.15 * stroke_continuity
        + 0.10 * local_contrast
        + 0.10 * max(0.0, 1.0 - abs(fg_ratio - 0.15) / 0.15)
    ) - 0.20 * bg_contam - 0.20 * tiny_ratio
    score = max(0.0, min(1.0, score))
    
    return {
        "score": round(score, 4),
        "foreground_ratio": round(fg_ratio, 4),
        "cc_count": int(cc_count),
        "median_area": round(med_area, 1),
        "tiny_ratio": round(tiny_ratio, 4),
        "frag_ratio": round(frag_ratio, 4),
        "grad_support": round(grad_support, 4),
        "boundary_overlap": round(boundary_overlap, 4),
        "stroke_continuity": round(stroke_continuity, 4),
        "bg_contamination": round(bg_contam, 4),
        "local_contrast": round(local_contrast, 4)
    }

evaluations = {}
for name, m in candidates.items():
    metrics = evaluate_stroke_quality(m, gray, grad_edges)
    evaluations[name] = metrics
    print(f"{name}: Score={metrics['score']} | FG={metrics['foreground_ratio']*100:.1f}% | Frag={metrics['frag_ratio']*100:.1f}% | GradSupp={metrics['grad_support']*100:.1f}%")

best_cand_name = max(evaluations, key=lambda k: evaluations[k]["score"])
print(f"Best Candidate: {best_cand_name} (Score: {evaluations[best_cand_name]['score']})")
