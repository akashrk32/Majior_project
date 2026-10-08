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

# Let's inspect horizontal projection profile (horizontal sum of gradients or dark incisions)
# In Old Kannada inscriptions, characters are engraved into the stone (darker grooves or relief edges).
# Horizontal gradient / vertical profile:
sobel_y = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))
sobel_x = np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3))
edge_energy = sobel_x + sobel_y

# Horizontal profile across the middle width (avoiding stone frame borders)
roi_x1, roi_x2 = int(w * 0.10), int(w * 0.90)
horiz_profile = np.mean(edge_energy[:, roi_x1:roi_x2], axis=1)

# Smooth profile
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
smooth_profile = cv2.GaussianBlur(horiz_profile.reshape(-1, 1), (1, 21), 0).flatten()

print(f"Image shape: {h}x{w}")
print(f"Profile min: {smooth_profile.min():.1f}, max: {smooth_profile.max():.1f}, mean: {smooth_profile.mean():.1f}")

# Find peaks (line centers)
from scipy.signal import find_peaks
peaks, props = find_peaks(smooth_profile, distance=18, prominence=2.0)
print(f"Detected potential line band peaks: {len(peaks)}")
print(f"Peak positions (y): {peaks[:15]}")
