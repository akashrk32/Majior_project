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

img_path = r"C:\Users\TEJAS M G\.gemini\antigravity-ide\brain\7d098130-659d-4128-b0cf-2785df3a7db0\.user_uploaded\media_1791384734075.jpg"
img_bgr = cv2.imread(img_path)

# 1. Preprocessing is locked
preprocessor = ShiloraStonePreprocessor()
preproc_res = preprocessor.process(img_bgr)
preproc_gray = preproc_res.final_natural
preproc_bgr = cv2.cvtColor(preproc_gray, cv2.COLOR_GRAY2BGR)

# Attention U-Net
binarizer = EpiSAMBinarizer(model_path="models/shilalekhya/binarizer.pth", device="cpu")
img_tensor = transforms.ToTensor()(Image.fromarray(cv2.cvtColor(preproc_bgr, cv2.COLOR_BGR2RGB)))

# Test patch sizes: 192, 256, 384
for psize in [192, 256, 384]:
    overlap = psize // 3
    prob = binarizer.predict_full_image_patchwise(img_tensor, patch_size=psize, overlap=overlap, batch_size=4)
    print(f"\n--- Patch size {psize} ---")
    print(f"Max: {prob.max():.4f}, Mean: {prob.mean():.4f}, 95th: {np.percentile(prob, 95):.4f}, 99th: {np.percentile(prob, 99):.4f}")
    for th in [0.15, 0.25, 0.35, 0.45]:
        mask = (prob > th).astype(np.uint8) * 255
        fg = np.mean(mask == 255) * 100
        n_cc, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
        areas = stats[1:, cv2.CC_STAT_AREA] if n_cc > 1 else [0]
        print(f"  Th={th:.2f}: FG={fg:.2f}%, CCs={n_cc-1}, MedArea={np.median(areas):.1f}")
        
    cv2.imwrite(f"scratch/prob_{psize}.png", (prob * 255).astype(np.uint8))
