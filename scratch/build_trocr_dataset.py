import csv
import json
import re
import shutil
from pathlib import Path
import random

root = Path("e:/Brahmi-OCR-main")
gt_line_dir = root / "data" / "episam" / "ground_truth" / "line_crops"
transcription_file = root / "scratch" / "mythic_society_transcriptions.csv"
chars_gt_dir = root / "data" / "episam" / "ground_truth" / "episam_dataset" / "chars"

trocr_dir = root / "data" / "trocr"
train_dir = trocr_dir / "train"
val_dir = trocr_dir / "validation"
test_dir = trocr_dir / "test"

for d in [train_dir, val_dir, test_dir, trocr_dir / "metadata"]:
    d.mkdir(parents=True, exist_ok=True)

# 1. Load expert readings from Mythic Society
expert_inscriptions = {}
with open(transcription_file, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    cur_stone = ""
    for r in reader:
        st = r["Inscription_Name"].strip()
        if st:
            cur_stone = st
        reading = r["Expert_Reading"].strip()
        if cur_stone and reading and reading != "Expert_Reading":
            if cur_stone not in expert_inscriptions:
                expert_inscriptions[cur_stone] = []
            expert_inscriptions[cur_stone].append(reading)

def norm_s(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

expert_norm_map = {norm_s(k): (k, v) for k, v in expert_inscriptions.items()}

# 2. Match stone line crop directories
stone_dirs = [d for d in gt_line_dir.iterdir() if d.is_dir()]
print(f"Total stones with GT line crops: {len(stone_dirs)}")

dataset_samples = []
matched_stone_count = 0

for s_dir in sorted(stone_dirs):
    s_norm = norm_s(s_dir.name)
    line_files = sorted(list(s_dir.glob("line_*.png")))
    if not line_files:
        continue

    # Attempt to match with expert readings
    matched_expert = None
    if s_norm in expert_norm_map:
        matched_expert = expert_norm_map[s_norm]
    else:
        # Try substring match
        for k_norm, (orig_name, readings) in expert_norm_map.items():
            if (s_norm[:18] in k_norm or k_norm[:18] in s_norm) and len(s_norm) > 10:
                matched_expert = (orig_name, readings)
                break

    if matched_expert:
        matched_stone_count += 1
        orig_stone_name, readings = matched_expert
        
        # Pair line images with expert lines
        for idx, line_f in enumerate(line_files):
            if idx < len(readings):
                text = readings[idx]
                dataset_samples.append({
                    "stone_id": s_dir.name,
                    "stone_name": orig_stone_name,
                    "line_id": line_f.stem,
                    "src_image_path": str(line_f),
                    "text": text,
                    "tier": "TIER_A_VERIFIED_EXPERT",
                    "source": "Mythic Society Inscriptions 3D Conservation"
                })

print(f"Matched stones with verified expert readings: {matched_stone_count} / {len(stone_dirs)}")
print(f"Total paired verified line-image samples (TIER A): {len(dataset_samples)}")

# 3. Add TIER B samples (EpiSAM character tags concatenated by line for stones without full expert reading)
tier_b_samples = []
for s_dir in sorted(stone_dirs):
    s_norm = norm_s(s_dir.name)
    # Check if already matched in TIER A
    if any(s["stone_id"] == s_dir.name for s in dataset_samples):
        continue

    # Look for character_polygons.json in ground truth chars
    char_poly_file = None
    for cp in chars_gt_dir.rglob("character_polygons.json"):
        if norm_s(cp.parent.name) == s_norm:
            char_poly_file = cp
            break
            
    if char_poly_file and char_poly_file.exists():
        try:
            with open(char_poly_file, "r", encoding="utf-8") as f:
                char_data = json.load(f)
            
            # Group characters by line_number and sort by char_number
            lines_dict = {}
            for k, val in char_data.items():
                ln = val.get("line_number", None)
                cn = val.get("char_number", None)
                tag = val.get("char_name", "")
                if ln is not None and tag:
                    if ln not in lines_dict:
                        lines_dict[ln] = []
                    lines_dict[ln].append((cn or 0, tag))

            line_files = sorted(list(s_dir.glob("line_*.png")))
            for line_f in line_files:
                # Extract line number from line_001.png
                m = re.search(r"(\d+)", line_f.stem)
                if m:
                    ln_num = int(m.group(1))
                    if ln_num in lines_dict:
                        sorted_chars = sorted(lines_dict[ln_num], key=lambda x: x[0])
                        tag_seq = " ".join([c[1] for c in sorted_chars if c[1]])
                        if tag_seq:
                            tier_b_samples.append({
                                "stone_id": s_dir.name,
                                "stone_name": s_dir.name,
                                "line_id": line_f.stem,
                                "src_image_path": str(line_f),
                                "text": tag_seq,
                                "tier": "TIER_B_RECONSTRUCTED_PHONETIC",
                                "source": "EpiSAM Character Polygons Tag Sequence"
                            })
        except Exception:
            pass

print(f"Total TIER B reconstructed line samples: {len(tier_b_samples)}")

# 4. Strict Stone-Level Split (Rule 17: No Data Leakage!)
unique_tier_a_stones = sorted(list(set(s["stone_id"] for s in dataset_samples)))
random.seed(42)
random.shuffle(unique_tier_a_stones)

n_stones = len(unique_tier_a_stones)
n_train = int(n_stones * 0.70)
n_val = int(n_stones * 0.15)

train_stones = set(unique_tier_a_stones[:n_train])
val_stones = set(unique_tier_a_stones[n_train:n_train + n_val])
test_stones = set(unique_tier_a_stones[n_train + n_val:])

print(f"\nStone-Level Split Summary (TIER A):")
print(f"  Training Stones   : {len(train_stones)}")
print(f"  Validation Stones : {len(val_stones)}")
print(f"  Testing Stones    : {len(test_stones)}")

# 5. Populate datasets and copy images
metadata_records = []

for sample in dataset_samples:
    st_id = sample["stone_id"]
    if st_id in train_stones:
        split = "train"
        target_folder = train_dir
    elif st_id in val_stones:
        split = "validation"
        target_folder = val_dir
    else:
        split = "test"
        target_folder = test_dir

    src_img = Path(sample["src_image_path"])
    dst_img_name = f"{st_id}_{sample['line_id']}.png"
    dst_img_path = target_folder / dst_img_name

    if not dst_img_path.exists():
        shutil.copy2(src_img, dst_img_path)

    metadata_records.append({
        "image_path": f"data/trocr/{split}/{dst_img_name}",
        "text": sample["text"],
        "stone_id": st_id,
        "line_id": sample["line_id"],
        "tier": sample["tier"],
        "source": sample["source"],
        "split": split
    })

# Write metadata.csv
meta_csv = trocr_dir / "metadata.csv"
fieldnames = ["image_path", "text", "stone_id", "line_id", "tier", "source", "split"]
with open(meta_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(metadata_records)

print(f"\nGenerated {meta_csv} with {len(metadata_records)} verified training line samples!")
print(f"  Train samples: {sum(1 for r in metadata_records if r['split'] == 'train')}")
print(f"  Val samples  : {sum(1 for r in metadata_records if r['split'] == 'validation')}")
print(f"  Test samples : {sum(1 for r in metadata_records if r['split'] == 'test')}")
