import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def inspect_folder(folder_path):
    p = Path(folder_path)
    if not p.exists():
        print(f"Folder does not exist: {p}")
        return []
    files = [f.name for f in p.iterdir() if f.is_file()]
    print(f"\n=== Folder: {folder_path} (Total files: {len(files)}) ===")
    print("First 20 filenames:")
    for f in sorted(files)[:20]:
        print("  ", f)
    if len(files) > 20:
        print(f"  ... and {len(files)-20} more")
    return files

ks = inspect_folder("e:/Brahmi-OCR-main/kannada_stones")
ks_bin = inspect_folder("e:/Brahmi-OCR-main/kannada_stones_episam_binarized")
ks_39_bin = inspect_folder("e:/Brahmi-OCR-main/kannada_stones_39_episam_binarized")
data_raw = inspect_folder("e:/Brahmi-OCR-main/data/raw")
data_prep = inspect_folder("e:/Brahmi-OCR-main/data/preprocessed")
data_bin = inspect_folder("e:/Brahmi-OCR-main/data/episam_binarized")
seg_test = inspect_folder("e:/Brahmi-OCR-main/Brahmi-OCR-main/segmentation test images")

