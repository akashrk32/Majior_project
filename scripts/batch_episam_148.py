"""
Batch EpiSAM Inscription Binarization for the Remaining 148 Stones
==================================================================
Official Model: AttentionUNet (trained on Mythic Society stone inscriptions)
Reference: "Unveiling Text in Challenging Stone Inscriptions: A Character-Context-Aware Patching Strategy"
           (IHDIA, IIIT Hyderabad / ICDAR 2026 EpiSAM)

Processes: All 148 remaining stone inscriptions from `kannada_stones/`
           (excluding stone_kn_000001 to stone_kn_000039)
Output:    `kannada_stones_episam_binarized/`
Report:    `episam_binarization_report.csv`
"""

import os
import sys
import re
import time
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import torch

# Add backend directory to sys.path
project_root = Path(__file__).resolve().parent.parent
backend_dir = project_root / "Brahmi-OCR-main" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from episam_binarizer.episam_binarizer import EpiSAMBinarizer


def run_batch():
    input_dir = project_root / "kannada_stones"
    output_dir = project_root / "kannada_stones_episam_binarized"
    report_csv = project_root / "episam_binarization_report.csv"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Filter out stone_kn_000001 through stone_kn_000039
    skip_pattern = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.(jpg|png|jpeg)$", re.IGNORECASE)
    all_files = sorted([f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".png", ".jpeg"]])
    target_files = [f for f in all_files if not skip_pattern.match(f.name)]

    print("=" * 70)
    print("      OFFICIAL EPISAM BATCH INSCRIBED STONE BINARIZATION PIPELINE       ")
    print(f"Total Stone Inscriptions in Source : {len(all_files)}")
    print(f"Excluded (stones 1 - 39)           : {len(all_files) - len(target_files)}")
    print(f"Target Images to Binarize          : {len(target_files)}")
    print(f"Output Directory                   : {output_dir}")
    print("=" * 70)

    # Initialize EpiSAM
    binarizer = EpiSAMBinarizer()

    records = []
    # If report exists, load previous records
    if report_csv.exists():
        try:
            df_existing = pd.read_csv(report_csv)
            records = df_existing.to_dict(orient="records")
            existing_names = {r["filename"] for r in records}
        except Exception:
            records = []
            existing_names = set()
    else:
        existing_names = set()

    success_count = 0
    total_start = time.time()

    for idx, img_path in enumerate(target_files, start=1):
        out_name = f"{img_path.stem}.png"
        out_path = output_dir / out_name

        # Skip if already exists and valid
        if out_path.exists() and out_path.stat().st_size > 1000 and img_path.name in existing_names:
            print(f"[{idx}/{len(target_files)}] Already binarized: {out_name}")
            success_count += 1
            continue

        t0 = time.time()
        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            print(f"[{idx}/{len(target_files)}] ERROR: Could not read {img_path.name}")
            records.append({
                "filename": img_path.name,
                "width": 0,
                "height": 0,
                "ink_pixel_percentage": 0.0,
                "inference_time_sec": 0.0,
                "status": "FAILED: ReadError"
            })
            continue

        h, w = img_bgr.shape[:2]

        try:
            mask, clean_ocr = binarizer.binarize(
                img_bgr,
                threshold=0.40,
                fast_single_scale=True,
                invert_output_for_ocr=True
            )
            cv2.imwrite(str(out_path), clean_ocr)
            dt = round(time.time() - t0, 2)
            ink_pct = round(100.0 * float(np.sum(mask == 255)) / mask.size, 2)

            rec = {
                "filename": img_path.name,
                "width": w,
                "height": h,
                "ink_pixel_percentage": ink_pct,
                "inference_time_sec": dt,
                "status": "SUCCESS"
            }
            # Replace existing or append
            records = [r for r in records if r["filename"] != img_path.name]
            records.append(rec)
            existing_names.add(img_path.name)
            success_count += 1

            print(f"[{idx}/{len(target_files)}] ({dt:.1f}s) Saved {out_name} | {w}x{h} | Ink: {ink_pct}%")

            # Periodically checkpoint the report
            if idx % 10 == 0 or idx == len(target_files):
                pd.DataFrame(records).to_csv(report_csv, index=False)

        except Exception as e:
            print(f"[{idx}/{len(target_files)}] ERROR on {img_path.name}: {e}")
            records.append({
                "filename": img_path.name,
                "width": w,
                "height": h,
                "ink_pixel_percentage": 0.0,
                "inference_time_sec": round(time.time() - t0, 2),
                "status": f"FAILED: {str(e)}"
            })

    # Save final report
    df = pd.DataFrame(records)
    df.to_csv(report_csv, index=False)
    total_time = round(time.time() - total_start, 1)

    print("\n" + "=" * 70)
    print("      EPISAM BATCH PREPROCESSING FINISHED SUCCESSFULLY!         ")
    print(f"Total Processed   : {success_count} / {len(target_files)}")
    print(f"Total Time        : {total_time}s")
    print(f"Report Generated  : {report_csv}")
    print("=" * 70)


if __name__ == "__main__":
    run_batch()
