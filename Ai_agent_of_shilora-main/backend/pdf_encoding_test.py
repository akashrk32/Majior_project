from pathlib import Path
from pypdf import PdfReader

pdf = next(Path("pdf_dataset").glob("*.pdf"))
reader = PdfReader(pdf)

text = reader.pages[0].extract_text() or ""

print("RAW TEXT:")
print(text[:3000])

print("\nUNICODE KANNADA DETECTION:")
print("Kannada characters:", sum('\u0C80' <= c <= '\u0CFF' for c in text))