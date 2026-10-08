import os
import sys
import json
import csv
from pathlib import Path
import torch
import pandas as pd
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# Setup paths
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

metadata_csv = root / "data" / "trocr" / "metadata.csv"
model_dir = root / "models" / "trocr" / "best_model"

print("=" * 60)
print("TrOCR FORENSIC VALIDATION & LEAKAGE AUDIT")
print("=" * 60)

# 1. Inspect metadata and check stone-level split leakage
df = pd.read_csv(metadata_csv)
print(f"Total rows in metadata: {len(df)}")
splits = df["split"].value_counts().to_dict()
print(f"Split distribution: {splits}")

train_stones = set(df[df["split"] == "train"]["stone_id"].unique())
val_stones = set(df[df["split"] == "validation"]["stone_id"].unique())
test_stones = set(df[df["split"] == "test"]["stone_id"].unique())

print(f"Unique stones: Train={len(train_stones)}, Val={len(val_stones)}, Test={len(test_stones)}")

leakage_train_val = train_stones.intersection(val_stones)
leakage_train_test = train_stones.intersection(test_stones)
leakage_val_test = val_stones.intersection(test_stones)

print(f"Leakage Train <-> Val:  {len(leakage_train_val)} ({leakage_train_val})")
print(f"Leakage Train <-> Test: {len(leakage_train_test)} ({leakage_train_test})")
print(f"Leakage Val <-> Test:   {len(leakage_val_test)} ({leakage_val_test})")

# 2. Check for image path leakage
train_imgs = set(df[df["split"] == "train"]["image_path"].unique())
test_imgs = set(df[df["split"] == "test"]["image_path"].unique())
img_overlap = train_imgs.intersection(test_imgs)
print(f"Direct Image Overlap Train <-> Test: {len(img_overlap)}")

# 3. Model inspection
print("\n--- MODEL ARCHITECTURE AUDIT ---")
with open(model_dir / "config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)
print(f"Architecture: {cfg.get('architectures', ['Unknown'])}")
print(f"Base model / encoder: {cfg.get('encoder', {}).get('model_type', 'Unknown')}")
print(f"Decoder model: {cfg.get('decoder', {}).get('model_type', 'Unknown')}")
print(f"Vocab size: {cfg.get('decoder', {}).get('vocab_size', 'Unknown')}")

# 4. Run test set evaluation
print("\n--- TEST SET INFERENCE & METRIC EVALUATION ---")
processor = TrOCRProcessor.from_pretrained(str(model_dir))
model = VisionEncoderDecoderModel.from_pretrained(str(model_dir))
model.eval()

test_df = df[df["split"] == "test"].dropna(subset=["text"]).copy()
print(f"Evaluating {len(test_df)} test lines across {len(test_stones)} test stones...")

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

total_edit_distance = 0
total_ref_chars = 0
exact_line_matches = 0
total_words = 0
exact_word_matches = 0
results = []

for idx, (_, row) in enumerate(test_df.iterrows(), 1):
    img_p = Path(row["image_path"])
    if not img_p.exists():
        img_p = root / row["image_path"]
    gt_text = str(row["text"]).strip()
    
    if not img_p.exists():
        print(f"Warning: Missing image {img_p}")
        continue

    pil_img = Image.open(str(img_p)).convert("RGB")
    pixel_values = processor(pil_img, return_tensors="pt").pixel_values
    
    with torch.no_grad():
        gen_ids = model.generate(pixel_values, max_length=64, num_beams=1)
    pred_text = processor.batch_decode(gen_ids, skip_special_tokens=True)[0].strip()

    ed = levenshtein(pred_text, gt_text)
    ref_len = len(gt_text)
    total_edit_distance += ed
    total_ref_chars += ref_len

    if pred_text == gt_text:
        exact_line_matches += 1

    gt_words = gt_text.split()
    pred_words = pred_text.split()
    total_words += len(gt_words)
    exact_word_matches += sum(1 for w in pred_words if w in gt_words)

    results.append({
        "stone_id": row["stone_id"],
        "line_id": row["line_id"],
        "ground_truth": gt_text,
        "prediction": pred_text,
        "edit_distance": ed,
        "cer": round(ed / max(1, ref_len), 4)
    })

evaluated_lines = len(results)
overall_cer = round(total_edit_distance / max(1, total_ref_chars), 4)
exact_line_acc = round(exact_line_matches / max(1, evaluated_lines), 4)
avg_edit_dist = round(total_edit_distance / max(1, evaluated_lines), 2)
word_acc = round(exact_word_matches / max(1, total_words), 4)

print("\n=== FINAL TEST METRICS ===")
print(f"Evaluated Test Lines: {evaluated_lines}")
print(f"Evaluated Test Stones: {len(test_stones)}")
print(f"Overall CER (Character Error Rate): {overall_cer} ({overall_cer * 100:.2f}%)")
print(f"Exact Line Accuracy: {exact_line_acc} ({exact_line_acc * 100:.2f}%)")
print(f"Average Edit Distance per line: {avg_edit_dist}")
print(f"Word Accuracy: {word_acc} ({word_acc * 100:.2f}%)")

out_eval = {
    "test_cer": overall_cer,
    "exact_line_accuracy": exact_line_acc,
    "average_edit_distance": avg_edit_dist,
    "word_accuracy": word_acc,
    "evaluated_lines": evaluated_lines,
    "evaluated_stones": len(test_stones),
    "data_leakage": {
        "train_val_overlap": len(leakage_train_val),
        "train_test_overlap": len(leakage_train_test),
        "val_test_overlap": len(leakage_val_test),
        "image_overlap": len(img_overlap),
        "leakage_passed": (len(leakage_train_test) == 0 and len(img_overlap) == 0)
    },
    "sample_predictions": results[:15]
}

with open(root / "reports" / "trocr_evaluation.json", "w", encoding="utf-8") as f:
    json.dump(out_eval, f, indent=2, ensure_ascii=False)
print(f"Saved evaluation to reports/trocr_evaluation.json")
