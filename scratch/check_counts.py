import re
from pathlib import Path

kannada_stones = Path("e:/Brahmi-OCR-main/kannada_stones")
all_files = sorted([f.name for f in kannada_stones.iterdir() if f.is_file()])
pattern_39 = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.(jpg|png|jpeg)$", re.IGNORECASE)

stones_39 = [f for f in all_files if pattern_39.match(f)]
other_148 = [f for f in all_files if not pattern_39.match(f)]

print(f"Total files in kannada_stones: {len(all_files)}")
print(f"Matches stone_kn_000001 - 39: {len(stones_39)}")
print(f"Other inscription files: {len(other_148)}")

data_raw = Path("e:/Brahmi-OCR-main/data/raw")
data_raw_files = sorted([f.name for f in data_raw.iterdir() if f.is_file()])
print(f"Total files in data/raw: {len(data_raw_files)} (e.g., {data_raw_files[0]} .. {data_raw_files[-1]})")

# Check if data/raw images correspond to stone_kn_000001 .. 39
print(f"data/preprocessed: {len(list(Path('e:/Brahmi-OCR-main/data/preprocessed').iterdir()))}")
print(f"data/episam_binarized: {len(list(Path('e:/Brahmi-OCR-main/data/episam_binarized').iterdir()))}")
print(f"kannada_stones_39_episam_binarized: {len(list(Path('e:/Brahmi-OCR-main/kannada_stones_39_episam_binarized').iterdir()))}")
print(f"kannada_stones_episam_binarized: {len(list(Path('e:/Brahmi-OCR-main/kannada_stones_episam_binarized').iterdir()))}")
