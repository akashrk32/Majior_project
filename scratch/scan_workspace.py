import os
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

root = Path("e:/Brahmi-OCR-main")

print("Scanning directory:", root)

ext_counts = defaultdict(int)
all_files = []
pth_files = []
zip_files = []
csv_files = []
json_files = []
txt_files = []

for dirpath, dirnames, filenames in os.walk(root):
    # Skip .git or cache if needed, but let's see everything
    for f in filenames:
        ext = os.path.splitext(f)[1].lower()
        ext_counts[ext] += 1
        full_path = os.path.join(dirpath, f)
        all_files.append(full_path)
        if ext in ['.pth', '.pt', '.ckpt', '.bin', '.onnx']:
            pth_files.append(full_path)
        elif ext in ['.zip', '.tar', '.gz']:
            zip_files.append(full_path)
        elif ext in ['.csv']:
            csv_files.append(full_path)
        elif ext in ['.json']:
            json_files.append(full_path)
        elif ext in ['.txt']:
            txt_files.append(full_path)

print(f"Total files found: {len(all_files)}")
print("\nTop file extensions:")
for ext, count in sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:25]:
    print(f"  {ext if ext else '(no ext)'}: {count}")

print("\nModel / Weight files:")
for p in pth_files:
    print(f"  {p} ({os.path.getsize(p) / (1024*1024):.2f} MB)")

print("\nArchive files:")
for z in zip_files:
    print(f"  {z} ({os.path.getsize(z) / (1024*1024):.2f} MB)")

print("\nCSV / Metadata files:")
for c in csv_files:
    print(f"  {c}")

print("\nJSON files (first 30):")
for j in json_files[:30]:
    print(f"  {j}")
if len(json_files) > 30:
    print(f"  ... and {len(json_files) - 30} more JSON files")
