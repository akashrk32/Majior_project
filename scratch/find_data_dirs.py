import os
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

root = Path("e:/Brahmi-OCR-main")

print("=== DIRECTORY INVENTORY (EXCLUDING node_modules, venv, .git) ===")

img_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
annot_extensions = {'.json', '.csv', '.xml', '.txt', '.gt', '.box'}

dirs_with_images = defaultdict(int)
dirs_with_annots = defaultdict(int)

all_images = []
all_annots = []

for dirpath, dirnames, filenames in os.walk(root):
    # filter out virtual environments and node modules
    if 'venv' in dirpath or 'node_modules' in dirpath or '.git' in dirpath or '__pycache__' in dirpath:
        continue
    for f in filenames:
        ext = os.path.splitext(f)[1].lower()
        full_path = os.path.join(dirpath, f)
        if ext in img_extensions:
            dirs_with_images[dirpath] += 1
            all_images.append(full_path)
        elif ext in annot_extensions:
            dirs_with_annots[dirpath] += 1
            all_annots.append(full_path)

print(f"\nTotal image files found: {len(all_images)}")
print("Directories containing images:")
for d, count in sorted(dirs_with_images.items(), key=lambda x: x[0]):
    print(f"  {d}: {count} images")

print(f"\nTotal potential annotation / metadata files found: {len(all_annots)}")
print("Directories containing annotations/text/metadata:")
for d, count in sorted(dirs_with_annots.items(), key=lambda x: x[0]):
    print(f"  {d}: {count} files")

