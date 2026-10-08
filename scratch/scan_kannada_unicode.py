import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

root = "e:/Brahmi-OCR-main"
kannada_char_pattern = re.compile(r'[\u0C80-\u0CFF]')

print("=== SCANNING FOR KANNADA UNICODE IN LOCAL REPOSITORY ===")

found_files = {}

for dirpath, dirnames, filenames in os.walk(root):
    if any(ignore in dirpath for ignore in ['venv', 'node_modules', '.git', '__pycache__']):
        continue
    for f in filenames:
        ext = os.path.splitext(f)[1].lower()
        if ext in ['.txt', '.csv', '.json', '.md', '.py', '.html', '.xml']:
            full_path = os.path.join(dirpath, f)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    matches = kannada_char_pattern.findall(content)
                    if matches:
                        found_files[full_path] = len(matches)
            except Exception as e:
                pass

print(f"Files containing Kannada Unicode characters: {len(found_files)}")
for p, count in sorted(found_files.items(), key=lambda x: x[1], reverse=True):
    print(f"  {p}: {count} Kannada characters")
