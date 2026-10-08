import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("Brahmi-OCR-main/backend").resolve()))

import cv2
import numpy as np
from preprocessing import ShiloraStonePreprocessor

img_path = r"C:\Users\TEJAS M G\.gemini\antigravity-ide\brain\7d098130-659d-4128-b0cf-2785df3a7db0\.user_uploaded\media_1791384734075.jpg"
img_bgr = cv2.imread(img_path)
print("Loaded image:", img_bgr.shape)

preprocessor = ShiloraStonePreprocessor()
preproc_res = preprocessor.process(img_bgr)
gray_natural = preproc_res.final_natural
ocr_ev = preproc_res.ocr_evidence
print("Preprocessed image shape:", gray_natural.shape)

h, w = gray_natural.shape
crop_sample = gray_natural[int(h*0.05):int(h*0.25), int(w*0.05):int(w*0.85)]
os.makedirs("scratch", exist_ok=True)
cv2.imwrite("scratch/crop_sample_gray.png", crop_sample)
print("Saved scratch/crop_sample_gray.png")
