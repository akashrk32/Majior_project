"""
Master Pipeline Script: Redo All Preprocessing & EpiSAM Binarization
====================================================================
Part 1:
  - Process stones 1 through 39 (stone_kn_000001 to stone_kn_000039)
  - Stage 1: SHILORA Adaptive Inscription Preprocessing
  - Stage 2: Official EpiSAM Attention U-Net Binarization
  - Generate side-by-side visual comparison panels for key stones
Part 2:

  - Process remaining 148 stone inscriptions (stone_kn_000040 to stone_kn_000187)
  - Official EpiSAM Attention U-Net Binarization
"""

import os
import sys
import re
import time
from pathlib import Path
import cv2
import numpy as np
import torch

# Add paths for imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

backend_dir = project_root / "Brahmi-OCR-main" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from preprocessing import ShiloraStonePreprocessor
from episam_binarizer.episam_binarizer import EpiSAMBinarizer


def create_tri_panel(orig_bgr, shilora_bgr, episam_bgr, max_panel_h=1000):
    """
    Creates a side-by-side [Original | SHILORA | EpiSAM] comparison panel.
    """
    h, w = orig_bgr.shape[:2]
    scale = max_panel_h / float(h) if h > max_panel_h else 1.0
    th, tw = int(h * scale), int(w * scale)

    o_res = cv2.resize(orig_bgr, (tw, th), interpolation=cv2.INTER_AREA)
    s_res = cv2.resize(shilora_bgr, (tw, th), interpolation=cv2.INTER_AREA)
    e_res = cv2.resize(episam_bgr, (tw, th), interpolation=cv2.INTER_NEAREST)

    # Ensure 3 channels
    if len(s_res.shape) == 2:
        s_res = cv2.cvtColor(s_res, cv2.COLOR_GRAY2BGR)
    if len(e_res.shape) == 2:
        e_res = cv2.cvtColor(e_res, cv2.COLOR_GRAY2BGR)

    # Add header bars with labels
    header_h = 40
    panel = np.zeros((th + header_h, tw * 3, 3), dtype=np.uint8)
    panel[:header_h, :] = (30, 30, 30)

    # Put images
    panel[header_h:, 0:tw] = o_res
    panel[header_h:, tw:tw*2] = s_res
    panel[header_h:, tw*2:tw*3] = e_res

    # Text headers
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(panel, "1. Raw Stone Photo", (20, 26), font, 0.7, (200, 200, 200), 2, cv2.LINE_AA)
    cv2.putText(panel, "2. SHILORA Preprocessed", (tw + 20, 26), font, 0.7, (0, 255, 180), 2, cv2.LINE_AA)
    cv2.putText(panel, "3. EpiSAM Binarized (OCR)", (tw * 2 + 20, 26), font, 0.7, (100, 200, 255), 2, cv2.LINE_AA)

    # Dividers
    cv2.line(panel, (tw, 0), (tw, th + header_h), (80, 80, 80), 2)
    cv2.line(panel, (tw * 2, 0), (tw * 2, th + header_h), (80, 80, 80), 2)

    return panel


def run_pipeline():
    stones_dir = project_root / "kannada_stones"
    out_shilora_39_dir = project_root / "kannada_stones_39_preprocessed"
    out_episam_39_dir = project_root / "kannada_stones_39_episam_binarized"
    out_episam_148_dir = project_root / "kannada_stones_episam_binarized"
    panels_dir = project_root / "visual_inspection_panels"

    out_shilora_39_dir.mkdir(parents=True, exist_ok=True)
    out_episam_39_dir.mkdir(parents=True, exist_ok=True)
    out_episam_148_dir.mkdir(parents=True, exist_ok=True)
    panels_dir.mkdir(parents=True, exist_ok=True)

    # Identify files
    pattern_39 = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.(jpg|png|jpeg)$", re.IGNORECASE)
    all_files = sorted([f for f in stones_dir.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".png", ".jpeg"]])

    stones_39 = [f for f in all_files if pattern_39.match(f.name)]
    stones_148 = [f for f in all_files if not pattern_39.match(f.name)]

    print("====================================================================")
    print("           SHILORA & EPISAM OCR RE-EXECUTION PIPELINE              ")
    print("====================================================================")
    print(f"Total Stones in Collection : {len(all_files)}")
    print(f"Part 1: Stones 1 - 39      : {len(stones_39)} files")
    print(f"Part 2: Remaining Stones   : {len(stones_148)} files")
    print("====================================================================\n")

    # Initialize models
    print("[INIT] Initializing SHILORA Stone Preprocessor...")
    shilora = ShiloraStonePreprocessor()

    print("[INIT] Initializing Official EpiSAM Attention U-Net Binarizer...")
    episam = EpiSAMBinarizer()

    # -------------------------------------------------------------------------
    # PART 1: STONES 1 TO 39 (SHILORA + EPISAM)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(">>> PART 1: Processing Stones 1 to 39 (SHILORA + EpiSAM)")
    print("=" * 70)

    part1_start = time.time()
    representative_stems = {"stone_kn_000001", "stone_kn_000015", "stone_kn_000022", "stone_kn_000025", "stone_kn_000026", "stone_kn_000039"}

    for idx, stone_file in enumerate(stones_39, 1):
        t0 = time.time()
        stone_stem = stone_file.stem
        stone_shilora_dir = out_shilora_39_dir / stone_stem
        episam_out_path = out_episam_39_dir / f"{stone_stem}.png"

        print(f"[{idx}/{len(stones_39)}] {stone_file.name} ...")

        # 1. SHILORA Preprocessing
        shilora_res = shilora.process(stone_file, output_dir=stone_shilora_dir)
        h, w = shilora_res.original.shape[:2]
        t_shilora = time.time() - t0

        # 2. EpiSAM Binarization (on SHILORA preprocessed natural output)
        t_epi_0 = time.time()
        # Convert grayscale preprocessed to 3-channel BGR for EpiSAM
        shilora_bgr = cv2.cvtColor(shilora_res.final_natural, cv2.COLOR_GRAY2BGR)
        _, episam_clean_ocr = episam.binarize(
            shilora_bgr,
            threshold=0.40,
            fast_single_scale=True,
            invert_output_for_ocr=True
        )
        cv2.imwrite(str(episam_out_path), episam_clean_ocr)
        t_episam = time.time() - t_epi_0
        total_stone_time = time.time() - t0

        print(f"     -> SHILORA ({t_shilora:.1f}s) | EpiSAM ({t_episam:.1f}s) | Res: {w}x{h} | Total: {total_stone_time:.1f}s")

        # 3. If representative stone, create side-by-side inspection panel
        if stone_stem in representative_stems:
            panel = create_tri_panel(shilora_res.original, shilora_bgr, episam_clean_ocr)
            panel_path = panels_dir / f"panel_{stone_stem}.jpg"
            cv2.imwrite(str(panel_path), panel)
            print(f"     -> [SAVED VISUAL PANEL] {panel_path.name}")

    part1_elapsed = time.time() - part1_start
    print(f"\n[PART 1 COMPLETE] All 39 stones processed in {part1_elapsed:.1f}s")

    # -------------------------------------------------------------------------
    # PART 2: REMAINING 148 STONES (EPISAM BINARIZATION)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(">>> PART 2: Processing Remaining 148 Stones (EpiSAM Binarization)")
    print("=" * 70)

    part2_start = time.time()
    success_148 = 0

    for idx, stone_file in enumerate(stones_148, 1):
        t0 = time.time()
        out_name = f"{stone_file.stem}.png"
        out_path = out_episam_148_dir / out_name

        img_bgr = cv2.imread(str(stone_file))
        if img_bgr is None:
            print(f"[{idx}/{len(stones_148)}] Could not read {stone_file.name}, skipping.")
            continue

        h, w = img_bgr.shape[:2]
        try:
            _, clean_ocr = episam.binarize(
                img_bgr,
                threshold=0.40,
                fast_single_scale=True,
                invert_output_for_ocr=True
            )
            cv2.imwrite(str(out_path), clean_ocr)
            dt = time.time() - t0
            success_148 += 1
            if idx % 10 == 0 or idx == len(stones_148) or idx <= 5:
                print(f"[{idx}/{len(stones_148)}] Saved {out_name} ({w}x{h}, {dt:.1f}s)")
        except Exception as e:
            print(f"[{idx}/{len(stones_148)}] Error on {stone_file.name}: {e}")

    part2_elapsed = time.time() - part2_start
    print(f"\n[PART 2 COMPLETE] {success_148}/{len(stones_148)} stones binarized in {part2_elapsed:.1f}s")

    print("\n" + "=" * 70)
    print("           REDO PIPELINE EXECUTION COMPLETED SUCCESSFULLY!          ")
    print("====================================================================")
    print(f"Part 1 Outputs (SHILORA):  {out_shilora_39_dir}")
    print(f"Part 1 Outputs (EpiSAM):   {out_episam_39_dir}")
    print(f"Part 2 Outputs (EpiSAM):   {out_episam_148_dir}")
    print(f"Visual Inspection Panels:  {panels_dir}")
    print("====================================================================")


if __name__ == "__main__":
    run_pipeline()
