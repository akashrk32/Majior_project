import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

for csv_file in [
    "e:/Brahmi-OCR-main/preprocessing_report.csv",
    "e:/Brahmi-OCR-main/binarization_report.csv",
    "e:/Brahmi-OCR-main/episam_binarization_report.csv",
    "e:/Brahmi-OCR-main/episam_binarization_39_report.csv"
]:
    try:
        df = pd.read_csv(csv_file)
        print(f"\n=== {csv_file} ===")
        print(f"Shape: {df.shape}")
        print("Columns:", df.columns.tolist())
        print(df.head(3))
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
