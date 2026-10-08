import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("Brahmi-OCR-main/backend").resolve()))

import cv2
import numpy as np

img_path = r"C:\Users\TEJAS M G\.gemini\antigravity-ide\brain\7d098130-659d-4128-b0cf-2785df3a7db0\.user_uploaded\media_1791384734075.jpg"
img_bgr = cv2.imread(img_path)
from preprocessing import ShiloraStonePreprocessor
preproc_res = ShiloraStonePreprocessor().process(img_bgr)
gray = preproc_res.final_natural # enhanced grayscale

# 1. Candidate 1: Adaptive Gaussian Conservative (larger block, conservative C)
c1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 5)

# 2. Candidate 2: Adaptive Gaussian Moderate (block 25, C=2)
c2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 2)

# 3. Candidate 3: Top-Hat & Black-Hat relief enhanced
# Chiseled incisions are dark grooves (Black-Hat) or illuminated grooves
k_size = 11
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
# Contrast between grooves and ridges:
relief_diff = cv2.subtract(blackhat, tophat)
relief_norm = cv2.normalize(relief_diff, None, 0, 255, cv2.NORM_MINMAX)
c3 = cv2.adaptiveThreshold(relief_norm, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, -3)

# 4. Candidate 4: Multi-scale gradient / Sauvola-style local contrast
# Local mean and std
mean = cv2.blur(gray.astype(np.float32), (25, 25))
sqr_mean = cv2.blur((gray.astype(np.float32))**2, (25, 25))
std = np.sqrt(np.maximum(0, sqr_mean - mean**2))
# Sauvola formula: T = mean * (1 + k * (std / R - 1))
k = 0.2
R = 128.0
sauvola_th = mean * (1.0 + k * (std / R - 1.0))
c4 = (gray.astype(np.float32) < sauvola_th).astype(np.uint8) * 255

# Let's also check the Attention U-Net binarizer
from episam_binarizer.episam_binarizer import EpiSAMBinarizer
binarizer_path = "models/shilalekhya/binarizer.pth"
binarizer = EpiSAMBinarizer(model_path=binarizer_path, device="cpu")
c_unet, _ = binarizer.binarize(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), threshold=0.40, fast_single_scale=True, invert_output_for_ocr=False)

candidates = {
    "C1_Adaptive_Gaussian_Conservative": c1,
    "C2_Adaptive_Gaussian_Moderate": c2,
    "C3_TopHat_BlackHat_Relief": c3,
    "C4_Sauvola_Local_Contrast": c4,
    "C5_Attention_UNet": c_unet
}

# Compute gradient magnitude of gray image
gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
grad_mag = np.sqrt(gx**2 + gy**2)
grad_norm = cv2.normalize(grad_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
grad_edges = (grad_norm > 35).astype(np.uint8) # strong gradient edges

print("=== CANDIDATE EVALUATION ===")
for name, mask in candidates.items():
    fg_ratio = np.mean(mask == 255)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    areas = stats[1:, cv2.CC_STAT_AREA] if num_labels > 1 else np.array([0])
    med_area = np.median(areas) if len(areas) > 0 else 0
    tiny_ratio = np.mean(areas < 15) if len(areas) > 0 else 0
    frag_ratio = np.mean(areas < 30) if len(areas) > 0 else 0
    
    # Overlap with gradient edges: what % of mask pixels have supporting image gradient
    grad_support = np.mean(grad_edges[mask == 255]) if np.sum(mask == 255) > 0 else 0
    
    print(f"[{name}]")
    print(f"  FG Ratio: {fg_ratio*100:.2f}% | Total CCs: {num_labels-1} | Median Area: {med_area:.1f}")
    print(f"  Tiny CC Ratio (<15px): {tiny_ratio*100:.1f}% | Frag Ratio (<30px): {frag_ratio*100:.1f}%")
    print(f"  Gradient Edge Support: {grad_support*100:.1f}%")
