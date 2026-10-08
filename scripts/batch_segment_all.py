"""
Batch EpiSAM Segmentation Runner for All 187 Stones
===================================================
Iterates through all 187 binarized stone images in data/binarized/,
runs candidate discovery, official EpiSAM segmentation, quality control,
and line reconstruction. Updates reports/segmentation_report.csv.
"""

import sys
import os
import csv
import time
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "scripts"))
sys.path.insert(0, str(root / "episam_official"))

import torch
from segment_anything import sam_model_registry
from run_episam_segmentation import process_stone_inscription

def run_batch_segmentation(limit=None):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading EpiSAM vit_b on {device}...")
    sam = sam_model_registry["vit_b"](checkpoint=str(root / "models/episam/episam.pth"))
    sam.to(device=device)
    sam.eval()

    bin_dir = root / "data/binarized"
    raw_dir = root / "data/raw"
    ks_dir = root / "kannada_stones"
    
    out_dirs = {
        "characters": root / "data/episam/characters",
        "predictions": root / "data/episam/predictions",
        "lines": root / "data/episam/lines",
        "metadata": root / "data/episam/metadata"
    }

    report_csv = root / "reports/segmentation_report.csv"
    existing_records = {}
    if report_csv.exists():
        with open(report_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                existing_records[r["stone_id"]] = r

    bin_files = sorted(list(bin_dir.glob("*.png")))
    if limit:
        bin_files = bin_files[:limit]

    print(f"Total binarized stones to process: {len(bin_files)}")

    fieldnames = [
        "stone_id", "source_dataset", "total_characters", "total_lines",
        "valid_characters", "questionable_characters", "segmentation_quality", "status"
    ]

    records = list(existing_records.values())

    for idx, bf in enumerate(bin_files, start=1):
        stone_id = bf.stem
        if stone_id in existing_records and existing_records[stone_id]["status"] == "SUCCESS":
            print(f"[{idx}/{len(bin_files)}] Skipping already segmented: {stone_id}")
            continue

        # Find raw / original visual image
        raw_path = raw_dir / f"{stone_id}.jpg"
        if not raw_path.exists():
            raw_path = ks_dir / f"{stone_id}.png"
        if not raw_path.exists():
            raw_path = ks_dir / f"{stone_id}.jpg"
        if not raw_path.exists():
            raw_path = bf # fallback to binarized image itself

        source_ds = "SHILORA_TARGET_39" if "stone_0" in stone_id or "stone_kn_0" in stone_id else "EPISAM_MYTHIC_SOCIETY_148"

        t0 = time.time()
        print(f"[{idx}/{len(bin_files)}] Segmenting {stone_id}...")
        try:
            res = process_stone_inscription(sam, raw_path, bf, out_dirs, device=device)
            dt = time.time() - t0
            
            total_chars = res.get("total_characters", 0)
            valid_chars = res.get("valid_characters", 0)
            valid_ratio = (valid_chars / total_chars) if total_chars > 0 else 0
            
            if valid_ratio >= 0.85:
                quality = "GOOD"
            elif valid_ratio >= 0.60:
                quality = "MODERATE"
            else:
                quality = "LOW"

            rec = {
                "stone_id": stone_id,
                "source_dataset": source_ds,
                "total_characters": total_chars,
                "total_lines": res.get("total_lines", 0),
                "valid_characters": valid_chars,
                "questionable_characters": res.get("questionable_characters", 0),
                "segmentation_quality": quality,
                "status": res.get("status", "SUCCESS")
            }
            records.append(rec)
            existing_records[stone_id] = rec
            print(f"    -> Done in {dt:.1f}s | Chars: {total_chars} | Lines: {res.get('total_lines', 0)} | Quality: {quality}")

            # Checkpoint CSV
            with open(report_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)

        except Exception as e:
            print(f"    -> ERROR on {stone_id}: {e}")
            rec = {
                "stone_id": stone_id,
                "source_dataset": source_ds,
                "total_characters": 0,
                "total_lines": 0,
                "valid_characters": 0,
                "questionable_characters": 0,
                "segmentation_quality": "FAILED",
                "status": f"FAILED: {str(e)}"
            }
            records.append(rec)
            with open(report_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)

if __name__ == "__main__":
    # By default, process first 10 stones or all
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    run_batch_segmentation(limit=args.limit)
