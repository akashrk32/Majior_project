import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("Brahmi-OCR-main/backend").resolve()))

import cv2
import numpy as np
import torch
from torchvision import transforms
from PIL import Image

from preprocessing import ShiloraStonePreprocessor
from episam_binarizer.episam_binarizer import EpiSAMBinarizer

# Load preprocessed image
img_path = r"C:\Users\TEJAS M G\.gemini\antigravity-ide\brain\7d098130-659d-4128-b0cf-2785df3a7db0\.user_uploaded\media_1791384734075.jpg"
img_bgr = cv2.imread(img_path)
preprocessor = ShiloraStonePreprocessor()
preproc_res = preprocessor.process(img_bgr)
preprocessed_gray = preproc_res.final_natural
preprocessed_bgr = cv2.cvtColor(preprocessed_gray, cv2.COLOR_GRAY2BGR)

# Initialize Attention U-Net
binarizer_path = "models/shilalekhya/binarizer.pth"
binarizer = EpiSAMBinarizer(model_path=binarizer_path, device="cpu")

# Let's inspect raw probability map with raw [0, 1] tensor
img_rgb = cv2.cvtColor(preprocessed_bgr, cv2.COLOR_BGR2RGB)
img_tensor = transforms.ToTensor()(Image.fromarray(img_rgb))

# Predict with single scale and with dual scale
prob_single = binarizer.predict_full_image_patchwise(img_tensor, patch_size=512, overlap=170, batch_size=4)
prob_dual_256 = binarizer.predict_full_image_patchwise(img_tensor, patch_size=256, overlap=85, batch_size=4)

print("=== RAW ATTENTION U-NET PROBABILITY ANALYSIS ===")
print("Single-scale (512):")
print(f"  Min: {prob_single.min():.4f}, Max: {prob_single.max():.4f}, Mean: {prob_single.mean():.4f}, Median: {np.median(prob_single):.4f}")
print(f"  90th percentile: {np.percentile(prob_single, 90):.4f}, 95th: {np.percentile(prob_single, 95):.4f}, 98th: {np.percentile(prob_single, 98):.4f}")

print("Scale (256):")
print(f"  Min: {prob_dual_256.min():.4f}, Max: {prob_dual_256.max():.4f}, Mean: {prob_dual_256.mean():.4f}, Median: {np.median(prob_dual_256):.4f}")

# Save raw probability maps as 8-bit images
os.makedirs("scratch", exist_ok=True)
cv2.imwrite("scratch/prob_single.png", (prob_single * 255).astype(np.uint8))
cv2.imwrite("scratch/prob_256.png", (prob_dual_256 * 255).astype(np.uint8))

# Test different thresholds on prob_single
for th in [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]:
    mask = (prob_single > th).astype(np.uint8) * 255
    fg_pct = np.mean(mask == 255) * 100
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    areas = stats[1:, cv2.CC_STAT_AREA] if num_labels > 1 else np.array([0])
    med_area = np.median(areas) if len(areas) > 0 else 0
    frag_pct = np.mean(areas < 30) * 100 if len(areas) > 0 else 0
    print(f"Threshold {th:.2f}: FG={fg_pct:.2f}%, CCs={num_labels-1}, MedArea={med_area:.1f}, Frag(<30px)={frag_pct:.1f}%")
