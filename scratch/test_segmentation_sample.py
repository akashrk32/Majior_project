import sys
from pathlib import Path
import time
import json

root = Path("e:/Brahmi-OCR-main")
sys.path.insert(0, str(root / "scripts"))
sys.path.insert(0, str(root / "episam_official"))

import torch
from segment_anything import sam_model_registry
from run_episam_segmentation import process_stone_inscription

# Load model
print("Loading EpiSAM vit_b model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)
sam = sam_model_registry["vit_b"](checkpoint=str(root / "models/episam/episam.pth"))
sam.to(device=device)
sam.eval()

out_dirs = {
    "characters": root / "data/episam/characters",
    "predictions": root / "data/episam/predictions",
    "lines": root / "data/episam/lines",
    "metadata": root / "data/episam/metadata"
}

# Test sample 1: SHILORA stone 001
print("\n--- Testing SHILORA stone_001 ---")
t0 = time.time()
res1 = process_stone_inscription(
    sam,
    image_path=root / "data/raw/stone_001.jpg",
    binarized_path=root / "data/binarized/stone_001_binarized.png",
    output_dirs=out_dirs,
    device=device
)
print("Result 1:", res1, f"Time: {time.time()-t0:.2f}s")

# Test sample 2: An EpiSAM stone
print("\n--- Testing EpiSAM stone Agara_1363CE... ---")
t0 = time.time()
res2 = process_stone_inscription(
    sam,
    image_path=root / "kannada_stones/Agara_1363CE_Kameyanayaka_s_Donation_Inscription.png",
    binarized_path=root / "data/binarized/Agara_1363CE_Kameyanayaka_s_Donation_Inscription.png",
    output_dirs=out_dirs,
    device=device
)
print("Result 2:", res2, f"Time: {time.time()-t0:.2f}s")
