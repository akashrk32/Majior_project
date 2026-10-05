"""
Batch Inscription Preprocessing using Official EpiSAM Attention U-Net
Excludes: stone_kn_000001 to stone_kn_000039 (reserved for custom training)
Processes: All other 148 stone inscription images
Output Directory: E:\\Brahmi-OCR-main\\kannada_stones_episam_binarized
"""

import os
import re
import time
from pathlib import Path
import cv2
import numpy as np
import torch

from episam_binarizer.episam_binarizer import EpiSAMBinarizer

def main():
    input_dir = Path(r"E:\Brahmi-OCR-main\kannada_stones")
    output_dir = Path(r"E:\Brahmi-OCR-main\kannada_stones_episam_binarized")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Regex to exclude stone_kn_000001 through stone_kn_000039
    skip_pattern = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.(jpg|png|jpeg)$", re.IGNORECASE)

    all_files = sorted([f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".png", ".jpeg"]])
    
    skipped = [f for f in all_files if skip_pattern.match(f.name)]
    targets = [f for f in all_files if not skip_pattern.match(f.name)]

    print(f"Total files in source: {len(all_files)}")
    print(f"Excluded (stone_kn_000001 - 000039): {len(skipped)}")
    print(f"Total to preprocess with EpiSAM: {len(targets)}")
    print(f"Destination: {output_dir}\n")

    # Initialize EpiSAM Binarizer
    binarizer = EpiSAMBinarizer()

    success_count = 0
    start_time = time.time()

    for idx, img_path in enumerate(targets, 1):
        out_name = f"{img_path.stem}.png"
        out_path = output_dir / out_name

        if out_path.exists() and out_path.stat().st_size > 1000:
            print(f"[{idx}/{len(targets)}] Already exists, skipping: {out_name}")
            success_count += 1
            continue

        t0 = time.time()
        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            print(f"[{idx}/{len(targets)}] Warning: Could not read {img_path.name}")
            continue

        try:
            mask, clean_ocr = binarizer.binarize(
                img_bgr,
                threshold=0.40,
                fast_single_scale=True,
                invert_output_for_ocr=True
            )
            cv2.imwrite(str(out_path), clean_ocr)
            dt = time.time() - t0
            ink_pct = 100.0 * float(np.sum(mask == 255)) / mask.size
            print(f"[{idx}/{len(targets)}] ({dt:.1f}s) Saved {out_name} (ink: {ink_pct:.2f}%)")
            success_count += 1
        except Exception as e:
            print(f"[{idx}/{len(targets)}] Error on {img_path.name}: {e}")

    total_time = time.time() - start_time
    print(f"\n==========================================")
    print(f"Batch preprocessing completed!")
    print(f"Successfully processed: {success_count}/{len(targets)}")
    print(f"Total time elapsed: {total_time:.1f} seconds")
    print(f"Saved to: {output_dir}")
    print(f"==========================================")

if __name__ == "__main__":
    main()
