import os
import sys
import json
import re
import hashlib
from pathlib import Path

root = Path("e:/Brahmi-OCR-main")
sys.stdout.reconfigure(encoding="utf-8")

print("=================================================================")
print("          SHILORA FORENSIC REPOSITORY INVENTORY AUDIT            ")
print("=================================================================")

# 1. Python Files
py_files = [p for p in root.rglob("*.py") if "venv" not in str(p) and ".claude" not in str(p)]
print(f"\n[1] ACTIVE PYTHON FILES AUDIT: Total = {len(py_files)}")

categories = {
    "preprocessing": [],
    "segmentation": [],
    "ocr_trocr": [],
    "translation": [],
    "orchestration_api": [],
    "legacy_brahmi": [],
    "episam_official": [],
    "audit_scratch": []
}

total_loc = 0
for p in py_files:
    s = p.as_posix()
    try:
        lines = len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
        total_loc += lines
    except:
        lines = 0
    if "preprocessing" in s or "binariz" in s:
        categories["preprocessing"].append((p, lines))
    elif "episam_official" in s:
        categories["episam_official"].append((p, lines))
    elif "Brahmi-OCR-main/backend" in s and ("gan" in s or "brahmi" in s or "mapping" in s or "weights" in s):
        categories["legacy_brahmi"].append((p, lines))
    elif "trocr" in s or "train" in s:
        categories["ocr_trocr"].append((p, lines))
    elif "translation" in s:
        categories["translation"].append((p, lines))
    elif "orchestrat" in s or "app.py" in s:
        categories["orchestration_api"].append((p, lines))
    elif "segment" in s:
        categories["segmentation"].append((p, lines))
    else:
        categories["audit_scratch"].append((p, lines))

print(f"Total Lines of Code: {total_loc}")
for k, v in categories.items():
    cat_loc = sum(x[1] for x in v)
    print(f"  - {k:22s}: {len(v):3d} files | {cat_loc:6d} lines")

# 2. Model Checkpoints
print(f"\n[2] MODEL CHECKPOINTS AUDIT:")
model_files = []
for ext in ["*.pth", "*.safetensors", "*.bin", "*.onnx", "*.h5", "*.keras", "*.pt"]:
    model_files.extend([m for m in root.rglob(ext) if m.is_file() and "venv" not in str(m) and "node_modules" not in str(m)])


for m in sorted(model_files):
    sz_mb = m.stat().st_size / (1024 * 1024)
    # Compute sha256
    h = hashlib.sha256()
    with open(m, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    sha256_prefix = h.hexdigest()[:16]
    print(f"  - {m.relative_to(root).as_posix():60s} | {sz_mb:7.2f} MB | sha256:{sha256_prefix}...")

# 3. Datasets Audit
print(f"\n[3] DATASETS & IMAGERY AUDIT:")
kannada_stones = list(Path("kannada_stones").glob("*.*"))
print(f"  - kannada_stones (Authentic physical stone scans/photos): {len(kannada_stones)} images")
gt_line_crops = list(Path("data/episam/ground_truth/line_crops").rglob("*.png"))
print(f"  - data/episam/ground_truth/line_crops (Authentic GT line crops): {len(gt_line_crops)} lines across {len(list(Path('data/episam/ground_truth/line_crops').iterdir()))} stones")

trocr_train = list(Path("data/trocr/train").glob("*.png"))
trocr_val = list(Path("data/trocr/validation").glob("*.png"))
trocr_test = list(Path("data/trocr/test").glob("*.png"))
print(f"  - data/trocr splits:")
print(f"      train     : {len(trocr_train)} lines")
print(f"      validation: {len(trocr_val)} lines")
print(f"      test      : {len(trocr_test)} lines")
print(f"      total     : {len(trocr_train) + len(trocr_val) + len(trocr_test)} lines")

# 4. Tokenizer Audit
print(f"\n[4] TOKENIZER AUDIT:")
tok_dir = root / "models" / "trocr" / "repaired_tokenizer"
if tok_dir.exists():
    with open(tok_dir / "tokenizer.json", "r", encoding="utf-8") as f:
        tok_data = json.load(f)
        vocab = tok_data.get("model", {}).get("vocab", {})
        vocab_keys = vocab.keys() if isinstance(vocab, dict) else [x[0] if isinstance(x, (list, tuple)) else str(x) for x in vocab]
        print(f"  - Repaired XLM-RoBERTa Tokenizer Path: {tok_dir.relative_to(root).as_posix()}")
        print(f"  - Total Vocab Size: {len(vocab_keys)} tokens")
        added_tokens = tok_data.get("added_tokens", [])
        print(f"  - Added Tokens: {len(added_tokens)} tokens")
        kannada_tokens = [k for k in vocab_keys if any(0x0C80 <= ord(c) <= 0x0CFF for c in k)]
        print(f"  - Kannada Unicode Block Tokens (U+0C80-U+0CFF) in base vocab: {len(kannada_tokens)} tokens")


# 5. Translation Resources Audit
print(f"\n[5] TRANSLATION RESOURCES AUDIT:")
for tf in (root / "data" / "translation").glob("*.json"):
    with open(tf, "r", encoding="utf-8") as f:
        data = json.load(f)
        count = len(data.get("entries", data.get("suffixes", data.get("archaic_character_mappings", []))))
        print(f"  - {tf.relative_to(root).as_posix():50s} : {count:4d} entries | {tf.stat().st_size:8d} bytes")

# 6. Anti-Hardcoding Forensic Scan
print(f"\n[6] ANTI-HARDCODING FORENSIC SCAN:")
scan_exts = ["*.py", "*.json", "*.csv", "*.js", "*.html"]
scan_files = []
for ext in scan_exts:
    scan_files.extend(root.rglob(ext))
scan_files = [f for f in scan_files if "venv" not in str(f) and ".claude" not in str(f) and "node_modules" not in str(f) and ".git" not in str(f)]

hardcode_patterns = [
    (r"if\s+[\w\.\(\)]*(?:stone|image|filename|file_name)\s*==\s*[\'\"]", "Filename/Stone-ID condition"),
    (r"if\s+[\w\.\(\)]*(?:hash|sha256|md5)\s*==\s*[\'\"]", "Hash-based condition"),
    (r"return\s+[\'\"](?:ಸ್ವಸ್ತಿ|ಶ್ರೀ\s*ವೀರ|Vijayanagara|Harihara|Donation\s*by|This\s*inscription\s*records)", "Canned OCR/Translation return"),
]

matches_found = []
for sf in scan_files:
    try:
        text = sf.read_text(encoding="utf-8", errors="ignore")
        for pat, desc in hardcode_patterns:
            m = re.findall(pat, text)
            if m:
                # exclude documentation/test files that explicitly test for hardcoding
                matches_found.append((sf.relative_to(root).as_posix(), desc, len(m)))
    except:
        pass

print(f"  - Total files scanned: {len(scan_files)}")
print(f"  - Potential hardcoded branches found: {len(matches_found)}")
for m in matches_found:
    print(f"    * {m[0]}: {m[1]} ({m[2]} occurrences)")

# 7. Ground Truth Label Forensic Audit (The Spreadsheet Pairing Bug)
print(f"\n[7] GROUND TRUTH LABEL PAIRING FORENSIC AUDIT:")
with open(root / "data" / "trocr" / "metadata.csv", "r", encoding="utf-8") as f:
    lines = [line.strip().split(",", 2) for line in f.readlines()[1:] if line.strip()]
print(f"  - metadata.csv records: {len(lines)}")
# Check line repetition within the same stone
from collections import defaultdict
stone_lines = defaultdict(list)
for r in lines:
    parts = r[0].split("/")
    img_name = parts[-1]
    text = r[1] if len(r) > 1 else ""
    # extract stone prefix
    st_prefix = img_name.split("_line_")[0] if "_line_" in img_name else img_name
    stone_lines[st_prefix].append(text)

repeated_lines_count = 0
for st, texts in stone_lines.items():
    if len(texts) > 1:
        # check if all or most texts are identical
        if len(set(texts)) < len(texts):
            repeated_lines_count += 1
            if repeated_lines_count <= 5:
                print(f"    WARNING: Stone '{st[:40]}' has {len(texts)} lines but only {len(set(texts))} unique label(s):")
                for idx, t in enumerate(texts[:4]):
                    print(f"       L{idx+1}: {t[:40]}")

print(f"  - Total stones with duplicated line labels in metadata.csv: {repeated_lines_count} / {len(stone_lines)}")
print("=================================================================")
