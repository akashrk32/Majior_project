import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("Brahmi-OCR-main/backend").resolve()))

import cv2
import numpy as np

from preprocessing import ShiloraStonePreprocessor
from preprocessing.shilora_binarizer_v2 import ShiloraBinarizerV2

img_path = r"C:\Users\TEJAS M G\.gemini\antigravity-ide\brain\7d098130-659d-4128-b0cf-2785df3a7db0\.user_uploaded\media_1791384734075.jpg"
img_bgr = cv2.imread(img_path)

# Preprocessing is LOCKED - use existing preprocessing
preprocessor = ShiloraStonePreprocessor()
preproc_res = preprocessor.process(img_bgr)
preproc_gray = preproc_res.final_natural
preproc_bgr = cv2.cvtColor(preproc_gray, cv2.COLOR_GRAY2BGR)

# Run ShiloraBinarizerV2
binarizer = ShiloraBinarizerV2()
final_ocr, final_mask, diag = binarizer.binarize_inscription(
    raw_bgr=img_bgr,
    v3_bgr=preproc_bgr,
    filename="uploaded_stone",
    primary_threshold=0.35
)

print("=== SHILORA BINARIZER V2 RESULTS ===")
print("Diagnostics:")
for k, v in diag.items():
    if k not in ["scale_predictions"]:
        print(f"  {k}: {v}")

fg_pct = np.mean(final_mask == 255) * 100
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(final_mask, connectivity=8)
areas = stats[1:, cv2.CC_STAT_AREA] if num_labels > 1 else np.array([0])
med_area = np.median(areas) if len(areas) > 0 else 0
frag_pct = np.mean(areas < 30) * 100 if len(areas) > 0 else 0

print(f"Final Mask: FG={fg_pct:.2f}%, CCs={num_labels-1}, MedArea={med_area:.1f}, Frag(<30px)={frag_pct:.1f}%")

# Save outputs to scratch to inspect
os.makedirs("scratch", exist_ok=True)
cv2.imwrite("scratch/v2_final_mask.png", final_mask)
cv2.imwrite("scratch/v2_final_ocr.png", final_ocr)
print("Saved scratch/v2_final_mask.png and scratch/v2_final_ocr.png")
