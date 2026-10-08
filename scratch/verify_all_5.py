import sys
sys.path.insert(0, "Brahmi-OCR-main/backend")
from episam_binarizer.episam_binarizer import EpiSAMBinarizer
import cv2
import numpy as np

binarizer = EpiSAMBinarizer()

stones = ["stone_kn_000006", "stone_kn_000007", "stone_kn_000010", "stone_kn_000011", "stone_kn_000019"]
for s in stones:
    img = cv2.imread(f"kannada_stones/{s}.jpg")
    m, _ = binarizer.binarize(img)
    pct = round(100.0 * np.sum(m == 255) / m.size, 2)
    # count character-like connected components
    n_lbl, _, stats, _ = cv2.connectedComponentsWithStats(m)
    print(f"[{s}] Final Binarized Ink%: {pct}%, Components: {n_lbl - 1}")
