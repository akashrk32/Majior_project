"""
SHILORA Robust Stone Inscription Binarization V2: Batch Runner for 39 Stones
=============================================================================
Applies the full two-stage self-refining ShilaLekhya binarizer with SHILORA
model input adapters, Hann-window seam protection, adaptive thresholding,
and original fidelity verification to all 39 ancient Kannada stone inscriptions.

Inputs:
  - RAW images: `data/raw/stone_XXX.jpg`
  - SHILORA V3 preprocessed images: `data/preprocessed/stone_XXX_preprocessed.png`

Outputs:
  - Dedicated binarized directories:
    * `data/episam_binarized/stone_XXX_binarized.png`
    * `kannada_stones_39_episam_binarized/stone_kn_XXXXXX.png`
  - Official Report:
    * `binarization_report.csv` (17 standardized columns)
"""

import os
import sys
import time
from pathlib import Path
import cv2
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "Brahmi-OCR-main" / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from preprocessing.shilora_binarizer_v2 import ShiloraBinarizerV2

REPORT_COLUMNS = [
    "filename",
    "input_branch",
    "stage1_foreground_ratio",
    "stage1_max_probability",
    "stage1_mean_probability",
    "stage1_component_count",
    "estimated_character_height",
    "stage2_foreground_ratio",
    "final_threshold",
    "final_foreground_ratio",
    "artifact_score",
    "background_false_positive_score",
    "structural_coherence",
    "quality_category",
    "fallback_used",
    "failure_reason",
    "status"
]

def run_batch():
    raw_dir = PROJECT_ROOT / "data" / "raw"
    prep_dir = PROJECT_ROOT / "data" / "preprocessed"
    out_dir_data = PROJECT_ROOT / "data" / "episam_binarized"
    out_dir_kn = PROJECT_ROOT / "kannada_stones_39_episam_binarized"
    report_csv = PROJECT_ROOT / "binarization_report.csv"

    out_dir_data.mkdir(parents=True, exist_ok=True)
    out_dir_kn.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("SHILORA ROBUST STONE INSCRIPTION BINARIZATION V2: 39 STONES DATASET")
    print(f"Raw Dir       : {raw_dir}")
    print(f"Prep Dir      : {prep_dir}")
    print(f"Output Dir 1  : {out_dir_data}")
    print(f"Output Dir 2  : {out_dir_kn}")
    print(f"Report Output : {report_csv}")
    print("=" * 80)

    binarizer = ShiloraBinarizerV2()
    records = []
    processed_stones = set()

    # Resume from existing binarization_report.csv if present
    if report_csv.exists():
        try:
            df_existing = pd.read_csv(report_csv)
            records = df_existing.to_dict('records')
            processed_stones = set(df_existing['filename'].astype(str))
            print(f"[SHILORA] Loaded {len(processed_stones)} already completed stones from {report_csv}")
        except Exception as e:
            print(f"[SHILORA] Could not read existing report: {e}")

    total_start = time.time()
    success_count = sum(1 for r in records if r.get("status") == "SUCCESS")

    for idx in range(1, 40):
        stone_id = f"stone_{idx:03d}"
        stone_kn_id = f"stone_kn_{idx:06d}"
        filename_key = f"{stone_id}.jpg"

        if filename_key in processed_stones:
            print(f"[{idx:02d}/39] SKIPPING: {stone_id} already processed in report.")
            continue

        raw_path = raw_dir / f"{stone_id}.jpg"
        prep_path = prep_dir / f"{stone_id}_preprocessed.png"

        if not raw_path.exists() or not prep_path.exists():
            print(f"[{idx:02d}/39] ERROR: Missing raw or prep image for {stone_id}")
            records.append({col: "MISSING_FILE" if col == "status" else (stone_id if col == "filename" else "NONE") for col in REPORT_COLUMNS})
            continue

        raw_bgr = cv2.imread(str(raw_path))
        prep_bgr = cv2.imread(str(prep_path))

        if raw_bgr is None or prep_bgr is None:
            print(f"[{idx:02d}/39] ERROR: Unreadable image for {stone_id}")
            continue

        t0 = time.time()
        ocr_bgr, mask_raw, diag = binarizer.binarize_inscription(
            raw_bgr=raw_bgr,
            v3_bgr=prep_bgr,
            filename=f"{stone_id}.jpg",
            primary_threshold=0.50
        )
        elapsed = round(time.time() - t0, 2)

        # Save outputs
        out_data_path = out_dir_data / f"{stone_id}_binarized.png"
        out_kn_path = out_dir_kn / f"{stone_kn_id}.png"

        cv2.imwrite(str(out_data_path), ocr_bgr)
        cv2.imwrite(str(out_kn_path), ocr_bgr)

        # Format record for report
        rec = {col: diag.get(col, "N/A") for col in REPORT_COLUMNS}
        records.append(rec)
        if diag["status"] == "SUCCESS":
            success_count += 1

        print(f"[{idx:02d}/39] ({elapsed:4.1f}s) {stone_id} | {diag['input_branch']} | "
              f"Th={diag['final_threshold']} | FG={diag['final_foreground_ratio']*100:5.2f}% | "
              f"H={diag['estimated_character_height']:4.1f}px | Cat={diag['quality_category']} | Status={diag['status']}", flush=True)

        # Save CSV report incrementally after every stone
        pd.DataFrame(records)[REPORT_COLUMNS].to_csv(report_csv, index=False)

    total_time = round(time.time() - total_start, 1)
    print("\n" + "=" * 80)
    print("SHILORA BINARIZATION V2 COMPLETE FOR ALL 39 STONES")
    print(f"Successfully Processed : {success_count} / 39")
    print(f"Total Processing Time  : {total_time}s")
    print(f"Standardized Report    : {report_csv}")
    print("=" * 80)

if __name__ == "__main__":
    run_batch()
