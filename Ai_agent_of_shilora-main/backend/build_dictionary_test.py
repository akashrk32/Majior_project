from pathlib import Path
from pypdf import PdfReader
import json

pdf = next(Path("pdf_dataset").glob("*.pdf"))
reader = PdfReader(pdf)

entries = []

for page_no in range(1, 6):
    text = reader.pages[page_no - 1].extract_text() or ""

    for line in text.splitlines():
        line = line.strip()
        if line:
            entries.append({
                "page": page_no,
                "raw": line
            })

Path("pdf_dataset/test_entries.json").write_text(
    json.dumps(entries, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"Created {len(entries)} raw entries")
print("Output: pdf_dataset/test_entries.json")