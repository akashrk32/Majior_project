import os
import re
from pathlib import Path

ks_dir = Path("kannada_stones")
files = sorted([f.name for f in ks_dir.iterdir() if f.is_file()])
pattern_39 = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.jpg$", re.IGNORECASE)

shilora_39 = [f for f in files if pattern_39.match(f)]
episam_148 = [f for f in files if not pattern_39.match(f)]

print("=== EXACT FILESYSTEM SCAN ===")
print("Total stone images in kannada_stones:", len(files))
print("SHILORA 39 stones count:", len(shilora_39))
print("EpiSAM 148 stones count:", len(episam_148))

bin_dir = Path("data/binarized")
bin_files = set(f.name for f in bin_dir.iterdir() if f.is_file())

# 39 stones check
bin_39 = []
for f in shilora_39:
    m = re.search(r"(\d+)", f)
    idx = int(m.group(1))
    target1 = f"stone_{idx:03d}_binarized.png"
    target2 = f"{Path(f).stem}.png"
    if target1 in bin_files or target2 in bin_files:
        bin_39.append(f)

bin_148 = [f for f in episam_148 if f"{Path(f).stem}.png" in bin_files]
pending_148 = [f for f in episam_148 if f"{Path(f).stem}.png" not in bin_files]

print(f"SHILORA 39 binarized: {len(bin_39)} / 39")
print(f"EpiSAM 148 binarized in data/binarized: {len(bin_148)} / 148")
print(f"EpiSAM 148 pending binarization: {len(pending_148)} / 148")
print(f"Total binarized currently: {len(bin_39) + len(bin_148)} / 187")
