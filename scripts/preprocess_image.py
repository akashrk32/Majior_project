"""
SHILORA Preprocessing CLI Tool
Usage:
    python scripts/preprocess_image.py --input path/to/stone.jpg --output output_dir/
    python scripts/preprocess_image.py --batch_39 --input E:\\Brahmi-OCR-main\\kannada_stones --output output_dir/
"""

import sys
import re
import argparse
from pathlib import Path

# Add project root to sys.path so preprocessing package is discoverable
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from preprocessing import ShiloraStonePreprocessor


def main():
    parser = argparse.ArgumentParser(
        description="SHILORA: Adaptive Stone Inscription Image Preprocessor (Old Kannada / Halegannada)"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to input stone image or directory of images."
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Directory where preprocessed outputs and reports will be saved."
    )
    parser.add_argument(
        "--batch_39",
        action="store_true",
        help="If set, only processes stone_kn_000001 through stone_kn_000039 in the input directory."
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=None,
        help="Manual override for Gaussian illumination sigma (20 - 60)."
    )
    parser.add_argument(
        "--clahe_clip",
        type=float,
        default=None,
        help="Manual override for CLAHE clip limit (1.5 - 3.0)."
    )
    parser.add_argument(
        "--sharpen_amount",
        type=float,
        default=None,
        help="Manual override for unsharp amount (0.15 - 0.50)."
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    preprocessor = ShiloraStonePreprocessor(
        illumination_sigma=args.sigma,
        clahe_clip_limit=args.clahe_clip,
        sharpen_amount=args.sharpen_amount
    )

    # Single Image Mode
    if input_path.is_file():
        print(f"\n========================================================")
        print(f"SHILORA Stone Preprocessing: Single Image Mode")
        print(f"Input : {input_path}")
        print(f"Output: {output_root}")
        print(f"========================================================")

        res = preprocessor.process(input_path, output_dir=output_root)
        orig_h, orig_w = res.original.shape[:2]

        print(f"OK Preprocessing complete.")
        print(f"Input dimensions : {orig_w} x {orig_h}")
        print(f"Output dimensions: {res.final_natural.shape[1]} x {res.final_natural.shape[0]}")
        print(f"Quality tier     : {res.metrics.quality_tier}")
        print(f"Adaptive sigma   : {res.metrics.illumination_sigma}")
        print(f"Adaptive CLAHE   : {res.metrics.clahe_clip_limit} (grid {res.metrics.clahe_tile_grid}x{res.metrics.clahe_tile_grid})")
        print(f"Adaptive sharpen : {res.metrics.sharpen_amount}")
        print(f"Saved artifacts  : {len(res.saved_paths)} files")
        return

    # Directory / Batch Mode
    if input_path.is_dir():
        # Match stone_kn_000001 through stone_kn_000039
        pattern_39 = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.(jpg|png|jpeg)$", re.IGNORECASE)

        valid_exts = {".jpg", ".png", ".jpeg"}
        all_files = sorted([f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in valid_exts])

        if args.batch_39:
            targets = [f for f in all_files if pattern_39.match(f.name)]
            print(f"\n[Batch 39 Mode] Filtered to {len(targets)} stone images (stone_kn_000001 to stone_kn_000039).")
        else:
            targets = all_files

        if not targets:
            print(f"No matching stone images found in {input_path}")
            return

        print(f"\n========================================================")
        print(f"SHILORA Stone Preprocessing: Batch Processing ({len(targets)} stones)")
        print(f"Destination: {output_root}")
        print(f"========================================================\n")

        for idx, stone_file in enumerate(targets, 1):
            stone_out_dir = output_root / stone_file.stem
            print(f"[{idx}/{len(targets)}] Processing {stone_file.name} -> {stone_out_dir.name}...")
            try:
                res = preprocessor.process(stone_file, output_dir=stone_out_dir)
                print(f"       OK {res.original.shape[1]}x{res.original.shape[0]} | {res.metrics.quality_tier} | "
                      f"sigma={res.metrics.illumination_sigma} | CLAHE={res.metrics.clahe_clip_limit} | sharp={res.metrics.sharpen_amount}")
            except Exception as e:
                print(f"       ERROR on {stone_file.name}: {e}")

        print(f"\nAll stones processed successfully in {output_root}")


if __name__ == "__main__":
    main()
