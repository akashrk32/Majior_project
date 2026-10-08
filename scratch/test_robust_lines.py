import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("Brahmi-OCR-main/backend").resolve()))

import cv2
import numpy as np

img_path = r"C:\Users\TEJAS M G\.gemini\antigravity-ide\brain\7d098130-659d-4128-b0cf-2785df3a7db0\.user_uploaded\media_1791384734075.jpg"
img_bgr = cv2.imread(img_path)
h, w = img_bgr.shape[:2]

from preprocessing import ShiloraStonePreprocessor
preproc_res = ShiloraStonePreprocessor().process(img_bgr)
gray = preproc_res.final_natural

sobel_y = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))
sobel_x = np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3))
edge_energy = sobel_x + sobel_y

col_x1, col_x2 = int(w * 0.08), int(w * 0.92)
row_energy = np.mean(edge_energy[:, col_x1:col_x2], axis=1)

from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

smooth_energy = gaussian_filter1d(row_energy, sigma=3.5)

peaks, props = find_peaks(smooth_energy, distance=18, prominence=1.5)
print(f"Detected line centers ({len(peaks)}): {peaks}")

lines = []
for i in range(len(peaks)):
    cy = peaks[i]
    lh = 28
    if i > 0 and i < len(peaks) - 1:
        lh = int((peaks[i+1] - peaks[i-1]) / 2.0)
    elif i < len(peaks) - 1:
        lh = int(peaks[i+1] - peaks[i])
    elif i > 0:
        lh = int(peaks[i] - peaks[i-1])
        
    lh = max(20, min(55, lh))
    y1 = max(0, int(cy - lh * 0.55))
    y2 = min(h, int(cy + lh * 0.55))
    x1 = col_x1
    x2 = col_x2
    lines.append([x1, y1, x2 - x1, y2 - y1])

print(f"Generated {len(lines)} line bands.")
for idx, bbox in enumerate(lines[:10], 1):
    print(f"Line {idx:02d}: y=[{bbox[1]}, {bbox[1]+bbox[3]}], h={bbox[3]}")
