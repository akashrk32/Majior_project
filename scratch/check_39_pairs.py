import hashlib
import cv2
from pathlib import Path

raw_dir = Path("e:/Brahmi-OCR-main/data/raw")
ks_dir = Path("e:/Brahmi-OCR-main/kannada_stones")

print("Checking correspondence between data/raw (stone_001.jpg ..) and kannada_stones (stone_kn_000001.png ..):")

for i in range(1, 40):
    raw_name = f"stone_{i:03d}.jpg"
    ks_name = f"stone_kn_{i:06d}.png"
    raw_path = raw_dir / raw_name
    ks_path = ks_dir / ks_name
    
    if not raw_path.exists() or not ks_path.exists():
        print(f"Missing pair: {raw_name} or {ks_name}")
        continue
    
    img_raw = cv2.imread(str(raw_path))
    img_ks = cv2.imread(str(ks_path))
    
    raw_h, raw_w = img_raw.shape[:2]
    ks_h, ks_w = img_ks.shape[:2]
    
    is_exact_dim = (raw_h == ks_h and raw_w == ks_w)
    if not is_exact_dim:
        print(f"Dim mismatch for {raw_name} ({raw_w}x{raw_h}) vs {ks_name} ({ks_w}x{ks_h})")

print("Finished checking all 39 pairs.")
