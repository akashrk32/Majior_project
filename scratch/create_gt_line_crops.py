import os
import json
import re
from pathlib import Path
import cv2
import numpy as np

root = Path("e:/Brahmi-OCR-main")
gt_lines_dir = root / "data" / "episam" / "ground_truth" / "episam_dataset" / "lines"
bin_dir = root / "data" / "binarized"
out_line_dir = root / "data" / "episam" / "ground_truth" / "line_crops"
out_line_dir.mkdir(parents=True, exist_ok=True)

# Map binarized images
bin_files = {Path(f).stem.lower(): f for f in bin_dir.glob("*.png")}

def norm_s(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

bin_norm_map = {norm_s(Path(f).stem): f for f in bin_dir.glob("*.png")}

# Iterate all line_polygons.json
lp_files = list(gt_lines_dir.rglob("line_polygons.json"))
print(f"Total stones with GT line polygons: {len(lp_files)}")

total_gt_lines_created = 0

for lp in lp_files:
    stone_name = lp.parent.name
    stone_norm = norm_s(stone_name)
    
    # Find matching binarized image
    bin_path = bin_norm_map.get(stone_norm, None)
    if not bin_path or not bin_path.exists():
        continue

    bin_img = cv2.imread(str(bin_path))
    if bin_img is None:
        continue
    h_img, w_img = bin_img.shape[:2]

    try:
        with open(lp, "r", encoding="utf-8") as f:
            data = json.load(f)
            polys = data.get("line_polygons", data)
    except Exception:
        continue

    stone_crop_dir = out_line_dir / norm_s(stone_name)
    stone_crop_dir.mkdir(parents=True, exist_ok=True)

    for line_id_str, poly in polys.items():
        if not poly or len(poly) < 3:
            continue
        poly_np = np.array(poly, dtype=np.int32)
        x, y, w, h = cv2.boundingRect(poly_np)
        
        # Add small margin
        x1 = max(0, x - 5)
        y1 = max(0, y - 5)
        x2 = min(w_img, x + w + 5)
        y2 = min(h_img, y + h + 5)

        line_crop = bin_img[y1:y2, x1:x2]
        if line_crop.size > 0:
            out_filename = f"line_{int(line_id_str):03d}.png"
            cv2.imwrite(str(stone_crop_dir / out_filename), line_crop)
            total_gt_lines_created += 1

print(f"Total GT line crop images created: {total_gt_lines_created}")
