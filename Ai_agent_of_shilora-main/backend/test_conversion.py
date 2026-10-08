from pathlib import Path
from pypdf import PdfReader
from knconverter import process_line

pdf = next(Path("pdf_dataset").glob("*.pdf"))
reader = PdfReader(pdf)

text = reader.pages[0].extract_text() or ""

print("BEFORE:")
print(text[:1000])

print("\nAFTER:")
print(process_line(text[:1000]))