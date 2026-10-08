import sys
sys.path.insert(0, "Brahmi-OCR-main/backend")
from episam_binarizer.episam_binarizer import EpiSAMBinarizer
import cv2
import numpy as np

binarizer = EpiSAMBinarizer()

img1 = cv2.imread("kannada_stones/stone_kn_000001.jpg")
m1, _ = binarizer.binarize(img1)
print("Stone 001 ink%:", round(100.0 * np.sum(m1 == 255) / m1.size, 2))

img6 = cv2.imread("kannada_stones/stone_kn_000006.jpg")
m6, _ = binarizer.binarize(img6)
print("Stone 006 ink%:", round(100.0 * np.sum(m6 == 255) / m6.size, 2))
