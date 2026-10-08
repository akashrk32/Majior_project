import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

root = Path("e:/Brahmi-OCR-main")

print("=== SEARCHING FOR ANNOTATIONS / LABELS / TRANSCRIPTIONS ===")

text_hints = ['transcript', 'label', 'ground_truth', 'gt', 'text', 'kannada', 'translation', 'halegannada', 'char', 'line', 'mask', 'polygon', 'box', 'centroid']

candidate_files = []

for dirpath, dirnames, filenames in os.walk(root):
    if any(ignore in dirpath for ignore in ['venv', 'node_modules', '.git', '__pycache__']):
        continue
    for f in filenames:
        f_lower = f.lower()
        full_path = os.path.join(dirpath, f)
        if any(hint in f_lower for hint in text_hints) or f.endswith(('.json', '.csv', '.txt', '.xml', '.yaml', '.yml')):
            candidate_files.append(full_path)

print(f"Found {len(candidate_files)} candidate files outside venv/node_modules:")
for c in candidate_files:
    print(" -", c)
