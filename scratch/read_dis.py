import sys

sys.stdout.reconfigure(encoding='utf-8')

for p in ["e:/Brahmi-OCR-main/scratch_dis.txt", "e:/Brahmi-OCR-main/README.md"]:
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f:
            print(f"=== {p} ===")
            print(f.read()[:2000])
    except Exception as e:
        print(f"Err {p}: {e}")
