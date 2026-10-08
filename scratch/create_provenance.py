import csv
import re
from pathlib import Path

root = Path("e:/Brahmi-OCR-main")
ks_dir = root / "kannada_stones"
data_prep_dir = root / "data" / "preprocessed"
data_bin_dir = root / "data" / "binarized"
ks_bin_dir = root / "kannada_stones_episam_binarized"

pattern_39 = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.jpg$", re.IGNORECASE)

all_files = sorted([f.name for f in ks_dir.iterdir() if f.is_file()])
shilora_39 = [f for f in all_files if pattern_39.match(f)]
episam_148 = [f for f in all_files if not pattern_39.match(f)]

provenance_rows = []

# 1. 39 SHILORA Target Stones
for f in shilora_39:
    m = re.search(r"(\d+)", f)
    idx = int(m.group(1))
    
    img_id = f"shilora_{idx:03d}"
    raw_path = f"kannada_stones/{f}"
    
    prep_name = f"stone_{idx:03d}_preprocessed.png"
    prep_path = f"data/preprocessed/{prep_name}"
    
    bin_name = f"stone_{idx:03d}_binarized.png"
    bin_path = f"data/binarized/{bin_name}"
    
    provenance_rows.append({
        "image_id": img_id,
        "source_dataset": "SHILORA_TARGET_39",
        "raw_path": raw_path,
        "preprocessing_status": "PREPROCESSED",
        "preprocessing_version": "SHILORA_V3.1_RELIEF_AMPLIFICATION",
        "preprocessed_path": prep_path,
        "binarization_status": "BINARIZED",
        "binarization_version": "SHILALEKHYA_ATTENTION_UNET_V1",
        "binarized_path": bin_path,
        "segmentation_status": "PENDING_EPISAM_INFERENCE",
        "text_label_status": "UNLABELED",
        "translation_label_status": "UNLABELED"
    })

# 2. 148 EpiSAM / Mythic Society Stones
for idx, f in enumerate(episam_148, start=1):
    stem = Path(f).stem
    img_id = f"episam_{idx:03d}_{stem}"
    raw_path = f"kannada_stones/{f}"
    
    bin_name = f"{stem}.png"
    if (data_bin_dir / bin_name).exists():
        bin_path = f"data/binarized/{bin_name}"
        bin_status = "BINARIZED"
    elif (ks_bin_dir / bin_name).exists():
        bin_path = f"kannada_stones_episam_binarized/{bin_name}"
        bin_status = "BINARIZED"
    else:
        bin_path = f"data/binarized/{bin_name}" # pending extraction/inference
        bin_status = "PENDING_BINARIZATION"
        
    provenance_rows.append({
        "image_id": img_id,
        "source_dataset": "EPISAM_MYTHIC_SOCIETY_148",
        "raw_path": raw_path,
        "preprocessing_status": "DIRECT_RAW_TO_BINARIZATION",
        "preprocessing_version": "NONE",
        "preprocessed_path": "",
        "binarization_status": bin_status,
        "binarization_version": "SHILALEKHYA_OFFICIAL_GROUND_TRUTH",
        "binarized_path": bin_path if bin_status == "BINARIZED" else "",
        "segmentation_status": "PENDING_EPISAM_INFERENCE",
        "text_label_status": "EPISAM_CHAR_TAGS_AVAILABLE",
        "translation_label_status": "PENDING_DISCOVERY"
    })

fieldnames = [
    "image_id", "source_dataset", "raw_path", "preprocessing_status",
    "preprocessing_version", "preprocessed_path", "binarization_status",
    "binarization_version", "binarized_path", "segmentation_status",
    "text_label_status", "translation_label_status"
]

out_csv = root / "reports" / "dataset_provenance.csv"
with open(out_csv, mode="w", newline="", encoding="utf-8") as fp:
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(provenance_rows)

print(f"Generated {out_csv} with {len(provenance_rows)} entries.")
