import cv2
import numpy as np
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, "Brahmi-OCR-main/backend")
from episam_binarizer.episam_binarizer import EpiSAMBinarizer

binarizer = EpiSAMBinarizer()

img = cv2.imread("kannada_stones/stone_kn_000006.jpg")
print("Input image shape:", img.shape)

# Let's inspect raw prediction from model
# EpiSAMBinarizer preprocesses and runs through ONNX / PyTorch model
mask, clean_ocr = binarizer.binarize(img, threshold=0.40, fast_single_scale=True)
ink_pct = 100.0 * np.sum(mask == 255) / mask.size
print("At threshold 0.40, ink_pct:", ink_pct)

# Check at different thresholds
for t in [0.50, 0.60, 0.70, 0.80, 0.90, 0.95]:
    m, _ = binarizer.binarize(img, threshold=t, fast_single_scale=True)
    pct = 100.0 * np.sum(m == 255) / m.size
    print(f"At threshold {t:.2f}, ink_pct: {pct:.2f}%")
