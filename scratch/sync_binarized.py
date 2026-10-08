import shutil
import re
from pathlib import Path

root = Path("e:/Brahmi-OCR-main")
ks_dir = root / "kannada_stones"
data_bin_dir = root / "data" / "binarized"
gt_bin_dir = root / "data" / "episam" / "ground_truth" / "episam_dataset" / "binary_images"

pattern_39 = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.jpg$", re.IGNORECASE)
local_148 = [f.name for f in ks_dir.iterdir() if f.is_file() and not pattern_39.match(f.name)]

# Collect all binary files in gt_bin_dir (both train and val subdirs)
gt_bin_files = list(gt_bin_dir.rglob("*.png")) + list(gt_bin_dir.rglob("*.jpg"))
print(f"Total binary image files in ground truth: {len(gt_bin_files)}")

def norm_name(s):
    s = Path(s).stem.lower()
    return re.sub(r'[^a-z0-9]', '', s)

gt_norm_map = {norm_name(p.name): p for p in gt_bin_files}

copied_count = 0
already_present = 0
missing_in_gt = []

for f in local_148:
    stem = Path(f).stem
    target_bin = data_bin_dir / f"{stem}.png"
    if target_bin.exists():
        already_present += 1
        continue
    
    # find in gt_norm_map
    f_norm = norm_name(f)
    if f_norm in gt_norm_map:
        src = gt_norm_map[f_norm]
        shutil.copy2(src, target_bin)
        copied_count += 1
    else:
        missing_in_gt.append(f)

print(f"Already present in data/binarized: {already_present}")
print(f"Copied from official EpiSAM ground-truth binary_images: {copied_count}")
print(f"Missing in GT binary_images: {len(missing_in_gt)}: {missing_in_gt}")

# Check total now in data/binarized
total_in_bin = len(list(data_bin_dir.glob("*.png")))
print(f"Total images now in data/binarized: {total_in_bin} / 187")
