import os
import shutil
import csv
import re
from pathlib import Path

root = Path("e:/Brahmi-OCR-main")

# 1. Create clean directory architecture
dirs_to_create = [
    root / "data" / "raw",
    root / "data" / "preprocessed",
    root / "data" / "binarized",
    root / "data" / "episam" / "ground_truth_masks",
    root / "data" / "episam" / "predicted_masks",
    root / "data" / "episam" / "characters",
    root / "data" / "episam" / "lines",
    root / "data" / "episam" / "metadata",
    root / "data" / "trocr" / "train",
    root / "data" / "trocr" / "validation",
    root / "data" / "trocr" / "test",
    root / "data" / "trocr" / "metadata",
    root / "models" / "shilalekhya",
    root / "models" / "episam",
    root / "models" / "trocr",
    root / "reports"
]

for d in dirs_to_create:
    d.mkdir(parents=True, exist_ok=True)

# 2. Link or copy binarizer.pth to models/shilalekhya/binarizer.pth if not present
src_binarizer = root / "Brahmi-OCR-main" / "backend" / "episam_binarizer" / "binarizer.pth"
dst_binarizer = root / "models" / "shilalekhya" / "binarizer.pth"
if src_binarizer.exists() and not dst_binarizer.exists():
    shutil.copy2(src_binarizer, dst_binarizer)
    print("Copied binarizer.pth to models/shilalekhya/binarizer.pth")

# 3. Synchronize binarized images into data/binarized/
# 39 SHILORA binarized images
src_39_bin = root / "data" / "episam_binarized"
for f in src_39_bin.glob("*.png"):
    dst = root / "data" / "binarized" / f.name
    if not dst.exists():
        shutil.copy2(f, dst)

# 80 already binarized from kannada_stones_episam_binarized
src_ks_bin = root / "kannada_stones_episam_binarized"
for f in src_ks_bin.glob("*.png"):
    if f.name == "test_sample.png":
        continue
    dst = root / "data" / "binarized" / f.name
    if not dst.exists():
        shutil.copy2(f, dst)

print("Created folder structures and populated initial data.")
