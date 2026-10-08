from pathlib import Path
from pypdf import PdfReader

PDF_DIR = Path("pdf_dataset")

for pdf in PDF_DIR.glob("*.pdf"):
    reader = PdfReader(pdf)

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    print("=" * 60)
    print(f"FILE   : {pdf.name}")
    print(f"PAGES  : {len(reader.pages)}")
    print(f"CHARS  : {len(text):,}")
    print("SAMPLE :")
    print(text[:500].replace("\n", " "))
    print()