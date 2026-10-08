from pathlib import Path
from pypdf import PdfReader

pdf = next(Path("pdf_dataset").glob("*.pdf"))
reader = PdfReader(pdf)

page = reader.pages[0]

def visitor(text, cm, tm, font_dict, font_size):
    print(repr(text))

page.extract_text(visitor_text=visitor)