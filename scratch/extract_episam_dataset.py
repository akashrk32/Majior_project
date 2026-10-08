import zipfile
import os
import time
from pathlib import Path

zip_path = Path("e:/Brahmi-OCR-main/data/episam/episam_dataset.zip")
extract_dir = Path("e:/Brahmi-OCR-main/data/episam/ground_truth")
extract_dir.mkdir(parents=True, exist_ok=True)

print(f"Extracting {zip_path} into {extract_dir}...")
t0 = time.time()
with zipfile.ZipFile(zip_path, 'r') as zf:
    zf.extractall(extract_dir)
dt = time.time() - t0
print(f"Extraction completed in {dt:.1f}s.")

# Verify extracted folders
episam_root = extract_dir / "episam_dataset"
if episam_root.exists():
    print("Extracted contents of episam_dataset:")
    for sub in episam_root.iterdir():
        print(f"  {sub.name} ({'dir' if sub.is_dir() else 'file'})")
