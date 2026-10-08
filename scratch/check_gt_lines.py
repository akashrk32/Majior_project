import json
from pathlib import Path

lines_gt_dir = Path("e:/Brahmi-OCR-main/data/episam/ground_truth/episam_dataset/lines")
sample_stone_dirs = list(lines_gt_dir.rglob("line_polygons.json"))[:5]

print(f"Total line_polygons.json found: {len(list(lines_gt_dir.rglob('line_polygons.json')))}")

for lp in sample_stone_dirs:
    parent = lp.parent.name
    with open(lp, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "line_polygons" in data:
            line_keys = list(data["line_polygons"].keys())
        else:
            line_keys = list(data.keys())
        print(f"Stone: {parent} | Line keys ({len(line_keys)}): {line_keys}")
