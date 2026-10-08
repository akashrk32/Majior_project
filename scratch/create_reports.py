import csv
import re
from pathlib import Path

root = Path("e:/Brahmi-OCR-main")

# Load all stone files
ks_dir = root / "kannada_stones"
data_raw_dir = root / "data" / "raw"
data_prep_dir = root / "data" / "preprocessed"
data_bin_dir = root / "data" / "binarized"
ks_bin_dir = root / "kannada_stones_episam_binarized"

pattern_39 = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.jpg$", re.IGNORECASE)

all_ks_files = sorted([f.name for f in ks_dir.iterdir() if f.is_file()])
shilora_files = [f for f in all_ks_files if pattern_39.match(f)]
other_148_files = [f for f in all_ks_files if not pattern_39.match(f)]

manifest_rows = []

# 1. 39 SHILORA stones
for f in shilora_files:
    # f is stone_kn_000001.jpg
    # stone_idx:
    idx_match = re.search(r"(\d+)", f)
    idx_int = int(idx_match.group(1)) if idx_match else 0
    stone_raw_name = f"stone_{idx_int:03d}.jpg"
    stone_prep_name = f"stone_{idx_int:03d}_preprocessed.png"
    stone_bin_name = f"stone_{idx_int:03d}_binarized.png"
    
    img_id = f"shilora_{idx_int:03d}"
    orig_path = f"kannada_stones/{f}"
    prep_path = f"data/preprocessed/{stone_prep_name}" if (data_prep_dir / stone_prep_name).exists() else ""
    bin_path = f"data/binarized/{stone_bin_name}" if (data_bin_dir / stone_bin_name).exists() else ""
    
    manifest_rows.append({
        "image_id": img_id,
        "source_dataset": "SHILORA_39",
        "original_path": orig_path,
        "preprocessed_path": prep_path,
        "binarized_path": bin_path,
        "character_mask_path": "",
        "line_mask_path": "",
        "annotation_available": "FALSE",
        "script": "Old Kannada / Halegannada",
        "usable_for_segmentation": "TRUE" if bin_path else "FALSE",
        "usable_for_trocr_training": "FALSE", # No ground-truth text transcription verified
        "split_group": "unlabeled_test"
    })

# 2. 148 Inscription stones (Mythic Society / EpiSAM dataset)
for idx, f in enumerate(other_148_files, start=1):
    stem = Path(f).stem
    img_id = f"episam_{idx:03d}_{stem}"
    orig_path = f"kannada_stones/{f}"
    
    # Check if binarized exists
    bin_file_png = f"{stem}.png"
    if (data_bin_dir / bin_file_png).exists():
        bin_path = f"data/binarized/{bin_file_png}"
    elif (ks_bin_dir / bin_file_png).exists():
        bin_path = f"kannada_stones_episam_binarized/{bin_file_png}"
    else:
        bin_path = ""
        
    char_mask_path = f"episam_dataset/chars/{stem}/character_polygons.json"
    line_mask_path = f"episam_dataset/lines/{stem}/line_polygons.json"
    
    manifest_rows.append({
        "image_id": img_id,
        "source_dataset": "EpiSAM_Mythic_Society_148",
        "original_path": orig_path,
        "preprocessed_path": "", # Not run through SHILORA preprocessing yet
        "binarized_path": bin_path,
        "character_mask_path": char_mask_path,
        "line_mask_path": line_mask_path,
        "annotation_available": "TRUE (EpiSAM Ground Truth)",
        "script": "Old Kannada / Halegannada",
        "usable_for_segmentation": "TRUE" if bin_path else "PENDING_BINARIZATION",
        "usable_for_trocr_training": "PENDING_TEXT_VERIFICATION", # Has char names, pending Unicode mapping
        "split_group": "train" if (idx % 5 != 0) else "validation"
    })

# 3. Write dataset_manifest.csv
manifest_file = root / "reports" / "dataset_manifest.csv"
fieldnames = [
    "image_id", "source_dataset", "original_path", "preprocessed_path",
    "binarized_path", "character_mask_path", "line_mask_path",
    "annotation_available", "script", "usable_for_segmentation",
    "usable_for_trocr_training", "split_group"
]

with open(manifest_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(manifest_rows)

print(f"Generated {manifest_file} with {len(manifest_rows)} rows.")

# 4. Generate dataset_inventory.csv
inv_file = root / "reports" / "dataset_inventory.csv"
inv_rows = [
    {
        "dataset_source": "SHILORA 39 Stones (Local)",
        "number_of_original_images": 39,
        "number_of_binarized_images": 39,
        "number_of_character_masks": 0,
        "number_of_line_masks": 0,
        "number_of_annotated_images": 0,
        "number_of_shilora_images": 39,
        "duplicates": 39, # stone_001.jpg .. 039.jpg in data/raw are identical to stone_kn_000001.jpg .. 039.jpg in kannada_stones
        "missing_pairs": 0
    },
    {
        "dataset_source": "EpiSAM / Mythic Society (kannada_stones/)",
        "number_of_original_images": 148,
        "number_of_binarized_images": 80, # 80 locally binarized, 68 pending local binarization
        "number_of_character_masks": 148, # in official EpiSAM dataset
        "number_of_line_masks": 148, # in official EpiSAM dataset (1,314 line mask files)
        "number_of_annotated_images": 148,
        "number_of_shilora_images": 0,
        "duplicates": 0,
        "missing_pairs": 68 # 68 pending binarization locally
    },
    {
        "dataset_source": "Brahmi-OCR Legacy Test Set",
        "number_of_original_images": 27,
        "number_of_binarized_images": 0,
        "number_of_character_masks": 0,
        "number_of_line_masks": 0,
        "number_of_annotated_images": 0,
        "number_of_shilora_images": 0,
        "duplicates": 0,
        "missing_pairs": 0
    },
    {
        "dataset_source": "TOTAL COMBINED KANNADA INSCRIPTIONS",
        "number_of_original_images": 187,
        "number_of_binarized_images": 119, # 39 SHILORA + 80 EpiSAM
        "number_of_character_masks": 148,
        "number_of_line_masks": 148,
        "number_of_annotated_images": 148,
        "number_of_shilora_images": 39,
        "duplicates": 39,
        "missing_pairs": 68
    }
]

inv_fields = [
    "dataset_source", "number_of_original_images", "number_of_binarized_images",
    "number_of_character_masks", "number_of_line_masks", "number_of_annotated_images",
    "number_of_shilora_images", "duplicates", "missing_pairs"
]

with open(inv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=inv_fields)
    writer.writeheader()
    writer.writerows(inv_rows)

print(f"Generated {inv_file} with {len(inv_rows)} rows.")
