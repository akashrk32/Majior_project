"""
Batch EpiSAM Inscription Binarization for the 39 Stone Inscriptions
===================================================================
Applies official EpiSAM (AttentionUNet trained on Mythic Society stone inscriptions)
to the 39 stone inscriptions, keeping them strictly SEPARATE from the 148 stones.

Inputs:
  - Already preprocessed images: `data/preprocessed/stone_XXX_preprocessed.png`
    (with automatic fallback to `data/raw/stone_XXX.jpg` if needed)
Outputs (Kept in dedicated separate directories):
  - `data/episam_binarized/` (named `stone_001_binarized.png` ... `stone_039_binarized.png`)
  - `kannada_stones_39_episam_binarized/` (named `stone_kn_000001.png` ... `stone_kn_000039.png`)
Report:
  - `episam_binarization_39_report.csv`
"""

import os
import sys
import time
from pathlib import Path
import cv2
import numpy as np
import pandas as pd

# Add backend directory to sys.path
project_root = Path(__file__).resolve().parent.parent
backend_dir = project_root / "Brahmi-OCR-main" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from episam_binarizer.episam_binarizer import EpiSAMBinarizer


def run_batch_39():
    raw_dir = project_root / "data" / "raw"
    prep_dir = project_root / "data" / "preprocessed"
    
    # Separate output directories for the 39 stones
    out_dir_data = project_root / "data" / "episam_binarized"
    out_dir_kn = project_root / "kannada_stones_39_episam_binarized"
    report_csv = project_root / "episam_binarization_39_report.csv"

    out_dir_data.mkdir(parents=True, exist_ok=True)
    out_dir_kn.mkdir(parents=True, exist_ok=True)

    print("=" * 75)
    print("      EPISAM BINARIZATION FOR 39 STONES (SEPARATE FROM 148 STONES)       ")
    print(f"Source Preprocessed Dir : {prep_dir}")
    print(f"Output Dir 1 (data)     : {out_dir_data}")
    print(f"Output Dir 2 (kn_stones): {out_dir_kn}")
    print(f"Report File             : {report_csv}")
    print("=" * 75)

    binarizer = EpiSAMBinarizer()
    records = []

    success_count = 0
    total_start = time.time()

    for idx in range(1, 40):
        stone_id = f"stone_{idx:03d}"
        stone_kn_id = f"stone_kn_{idx:06d}"
        
        # Prefer the preprocessed image as primary input as requested
        prep_path = prep_dir / f"{stone_id}_preprocessed.png"
        raw_path = raw_dir / f"{stone_id}.jpg"
        
        input_path = prep_path if prep_path.exists() else raw_path
        if not input_path.exists():
            print(f"[{idx:02d}/39] ERROR: Neither preprocessed nor raw exists for {stone_id}")
            records.append({
                "stone_id": stone_id,
                "kannada_id": stone_kn_id,
                "source_used": "NONE",
                "width": 0,
                "height": 0,
                "ink_pixel_percentage": 0.0,
                "inference_time_sec": 0.0,
                "status": "FAILED: MissingFile"
            })
            continue

        out_data_file = out_dir_data / f"{stone_id}_binarized.png"
        out_kn_file = out_dir_kn / f"{stone_kn_id}.png"

        t0 = time.time()
        img = cv2.imread(str(input_path))
        if img is None:
            print(f"[{idx:02d}/39] ERROR: Could not read {input_path}")
            continue

        h, w = img.shape[:2]

        try:
            mask, clean_ocr = binarizer.binarize(
                img,
                threshold=0.40,
                fast_single_scale=True,
                invert_output_for_ocr=True
            )

            # Save in both separate destination folders for maximum clarity and compatibility
            cv2.imwrite(str(out_data_file), clean_ocr)
            cv2.imwrite(str(out_kn_file), clean_ocr)

            dt = round(time.time() - t0, 2)
            ink_pct = round(100.0 * float(np.sum(mask == 255)) / mask.size, 2)

            rec = {
                "stone_id": stone_id,
                "kannada_id": stone_kn_id,
                "source_used": input_path.name,
                "width": w,
                "height": h,
                "ink_pixel_percentage": ink_pct,
                "inference_time_sec": dt,
                "status": "SUCCESS"
            }
            records.append(rec)
            success_count += 1
            print(f"[{idx:02d}/39] ({dt:.1f}s) Binarized {stone_id} | {w}x{h} | Ink: {ink_pct}%")

        except Exception as e:
            print(f"[{idx:02d}/39] ERROR on {stone_id}: {e}")
            records.append({
                "stone_id": stone_id,
                "kannada_id": stone_kn_id,
                "source_used": input_path.name,
                "width": w,
                "height": h,
                "ink_pixel_percentage": 0.0,
                "inference_time_sec": round(time.time() - t0, 2),
                "status": f"FAILED: {str(e)}"
            })

    # Save summary report
    df = pd.DataFrame(records)
    df.to_csv(report_csv, index=False)
    total_time = round(time.time() - total_start, 1)

    print("\n" + "=" * 75)
    print("      EPISAM 39 STONES BINARIZATION FINISHED SUCCESSFULLY!      ")
    print(f"Total Processed   : {success_count} / 39")
    print(f"Total Time        : {total_time}s")
    print(f"Report Generated  : {report_csv}")
    print("=" * 75)


if __name__ == "__main__":
    run_batch_39()
