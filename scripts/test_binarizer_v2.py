"""
Test Script for SHILORA Robust Stone Inscription Binarizer V2
=============================================================
Evaluates the test set:
  - stone_005 (challenging low-signal thumbnail)
  - stone_006 (challenging near-blank thumbnail)
  - stone_027 (challenging narrow estampage)
  - stone_034 (high-resolution natural stone photograph)

Saves:
  - Final binarized OCR outputs
  - Inspection panels: RAW vs V3 vs Stage 1 Coarse vs Stage 2 Final
  - Diagnostic table
"""

import os
import sys
from pathlib import Path
import cv2
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "Brahmi-OCR-main" / "backend"))

from preprocessing.shilora_binarizer_v2 import ShiloraBinarizerV2

def run_test():
    binarizer = ShiloraBinarizerV2()
    test_stones = ["stone_005", "stone_006", "stone_027", "stone_034"]

    out_dir = PROJECT_ROOT / "scratch" / "v2_test_results"
    out_dir.mkdir(parents=True, exist_ok=True)

    records = []

    print("=" * 80)
    print("RUNNING SHILORA BINARIZER V2 ON VALIDATION TEST SET")
    print("=" * 80)

    for sid in test_stones:
        raw_path = PROJECT_ROOT / "data" / "raw" / f"{sid}.jpg"
        v3_path = PROJECT_ROOT / "data" / "preprocessed" / f"{sid}_preprocessed.png"

        raw_bgr = cv2.imread(str(raw_path))
        v3_bgr = cv2.imread(str(v3_path))

        ocr_bgr, mask_raw, diag = binarizer.binarize_inscription(
            raw_bgr, v3_bgr, filename=f"{sid}.jpg", primary_threshold=0.50
        )

        records.append(diag)

        # Save output images
        cv2.imwrite(str(out_dir / f"{sid}_binarized_ocr.png"), ocr_bgr)
        cv2.imwrite(str(out_dir / f"{sid}_mask_raw.png"), mask_raw)

        # Create 4-panel visual comparison: RAW, V3, Mask, OCR
        h, w = ocr_bgr.shape[:2]
        raw_resized = cv2.resize(raw_bgr, (w, h))
        v3_resized = cv2.resize(v3_bgr, (w, h))
        mask_3ch = cv2.cvtColor(mask_raw, cv2.COLOR_GRAY2BGR)

        # Add labels
        def add_label(img, text):
            annotated = img.copy()
            cv2.rectangle(annotated, (0, 0), (annotated.shape[1], 24), (30, 30, 30), -1)
            cv2.putText(annotated, text, (6, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            return annotated

        panel_raw = add_label(raw_resized, f"RAW: {sid}")
        panel_v3 = add_label(v3_resized, "SHILORA V3")
        panel_mask = add_label(mask_3ch, f"Stage2 Mask (th={diag['final_threshold']})")
        panel_ocr = add_label(ocr_bgr, f"OCR Output (FG: {diag['final_foreground_ratio']*100:.2f}%)")

        comparison = np.hstack([panel_raw, panel_v3, panel_mask, panel_ocr])
        cv2.imwrite(str(out_dir / f"{sid}_comparison_panel.png"), comparison)

        print(f"[{sid}] Status: {diag['status']} | Branch: {diag['input_branch']} | "
              f"Thresh: {diag['final_threshold']} | FG: {diag['final_foreground_ratio']*100:.2f}% | "
              f"Char_H: {diag['estimated_character_height']}px | Score: {diag['quality_score']} | "
              f"Cat: {diag['quality_category']}")

    df = pd.DataFrame(records)
    print("\nTest Summary:")
    print(df[["filename", "input_branch", "final_threshold", "final_foreground_ratio", "quality_score", "quality_category", "status"]])

if __name__ == "__main__":
    run_test()
