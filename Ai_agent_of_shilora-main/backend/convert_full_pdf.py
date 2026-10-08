from pathlib import Path
from pypdf import PdfReader
from knconverter import process_line

pdf = next(Path("pdf_dataset").glob("*.pdf"))
reader = PdfReader(pdf)

output = []

for page_no, page in enumerate(reader.pages, 1):
    text = page.extract_text() or ""

    for line in text.splitlines():
        line = line.strip()
        if line:
            output.append({
                "page": page_no,
                "text": process_line(line)
            })

Path("pdf_dataset/kannada_converted.json").write_text(
    __import__("json").dumps(output, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"Pages processed: {len(reader.pages)}")
print(f"Lines extracted: {len(output)}")
print("Saved: pdf_dataset/kannada_converted.json")