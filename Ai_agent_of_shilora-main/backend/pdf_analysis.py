from pathlib import Path
from pypdf import PdfReader

pdf = next(Path("pdf_dataset").glob("*.pdf"))
reader = PdfReader(pdf)

print(f"File: {pdf.name}")
print(f"Pages: {len(reader.pages)}")

for page_no in [1, 2, 100, 200, 300, 396]:
    text = reader.pages[page_no - 1].extract_text() or ""
    print(f"\n--- PAGE {page_no} ---")
    print(text[:1000])