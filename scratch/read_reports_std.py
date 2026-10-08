import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for csv_path in [
    "e:/Brahmi-OCR-main/preprocessing_report.csv",
    "e:/Brahmi-OCR-main/binarization_report.csv",
    "e:/Brahmi-OCR-main/episam_binarization_report.csv",
    "e:/Brahmi-OCR-main/episam_binarization_39_report.csv"
]:
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        continue
    with open(csv_path, mode='r', encoding='utf-8', errors='replace') as f:
        reader = list(csv.reader(f))
        header = reader[0] if reader else []
        rows = reader[1:] if len(reader) > 1 else []
        print(f"\n=== {csv_path} ===")
        print(f"Total rows: {len(rows)}")
        print("Header:", header)
        if rows:
            print("Row 1:", rows[0])
            if len(rows) > 1:
                print(f"Row {len(rows)}:", rows[-1])
