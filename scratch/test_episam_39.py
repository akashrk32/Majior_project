import sys, os
from pathlib import Path
backend_dir = Path("Brahmi-OCR-main/backend").resolve()
sys.path.insert(0, str(backend_dir))
from episam_binarizer.episam_binarizer import EpiSAMBinarizer
import cv2, numpy as np

os.makedirs("scratch", exist_ok=True)
binarizer = EpiSAMBinarizer()

# Test stone 001 and stone 027
for s in ["stone_001", "stone_027"]:
    raw = cv2.imread(f"data/raw/{s}.jpg")
    prep = cv2.imread(f"data/preprocessed/{s}_preprocessed.png")

    mask_raw, ocr_raw = binarizer.binarize(raw, threshold=0.40, fast_single_scale=True, invert_output_for_ocr=True)
    mask_prep, ocr_prep = binarizer.binarize(prep, threshold=0.40, fast_single_scale=True, invert_output_for_ocr=True)

    cv2.imwrite(f"scratch/{s}_episam_from_raw.png", ocr_raw)
    cv2.imwrite(f"scratch/{s}_episam_from_prep.png", ocr_prep)
    print(f"{s}: raw_ink={100*np.sum(mask_raw==255)/mask_raw.size:.2f}%, prep_ink={100*np.sum(mask_prep==255)/mask_prep.size:.2f}%")
