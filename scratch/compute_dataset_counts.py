import os
import re
import io
import zipfile
import urllib.request
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Inspect local files
local_ks_dir = Path("e:/Brahmi-OCR-main/kannada_stones")
local_ks_bin_dir = Path("e:/Brahmi-OCR-main/kannada_stones_episam_binarized")
local_39_bin_dir = Path("e:/Brahmi-OCR-main/kannada_stones_39_episam_binarized")
data_raw_dir = Path("e:/Brahmi-OCR-main/data/raw")
data_prep_dir = Path("e:/Brahmi-OCR-main/data/preprocessed")
data_bin_dir = Path("e:/Brahmi-OCR-main/data/episam_binarized")

ks_files = sorted([f.name for f in local_ks_dir.iterdir() if f.is_file()])
pattern_39 = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.(jpg|png|jpeg)$", re.IGNORECASE)

shilora_39_in_ks = [f for f in ks_files if pattern_39.match(f)]
other_148_in_ks = [f for f in ks_files if not pattern_39.match(f)]

# 2. Check binarized files
ks_bin_files = set(f.name for f in local_ks_bin_dir.iterdir() if f.is_file())
ks_39_bin_files = set(f.name for f in local_39_bin_dir.iterdir() if f.is_file())
data_raw_files = sorted([f.name for f in data_raw_dir.iterdir() if f.is_file()])
data_prep_files = sorted([f.name for f in data_prep_dir.iterdir() if f.is_file()])
data_bin_files = sorted([f.name for f in data_bin_dir.iterdir() if f.is_file()])

print(f"=== LOCAL REPOSITORY COUNTS ===")
print(f"1. Total images in kannada_stones/: {len(ks_files)}")
print(f"   - SHILORA stones (stone_kn_000001 - 39): {len(shilora_39_in_ks)}")
print(f"   - Other stone inscriptions (Mythic Society / EpiSAM set): {len(other_148_in_ks)}")
print(f"2. Total in data/raw/ (SHILORA stone_001.jpg - stone_039.jpg): {len(data_raw_files)}")
print(f"3. Total in data/preprocessed/ (stone_001_preprocessed.png - 039): {len(data_prep_files)}")
print(f"4. Total in data/episam_binarized/ (stone_001_binarized.png - 039): {len(data_bin_files)}")
print(f"5. Total in kannada_stones_39_episam_binarized/ (stone_kn_000001.png - 39): {len(ks_39_bin_files)}")
print(f"6. Total in kannada_stones_episam_binarized/: {len(ks_bin_files)}")

# Check how many of the 148 are binarized
binarized_148 = [f for f in other_148_in_ks if f in ks_bin_files or Path(f).stem + '.png' in ks_bin_files]
not_binarized_148 = [f for f in other_148_in_ks if not (f in ks_bin_files or Path(f).stem + '.png' in ks_bin_files)]

print(f"   - Of the 148 other stones, binarized: {len(binarized_148)}")
print(f"   - Of the 148 other stones, NOT YET binarized: {len(not_binarized_148)}")
