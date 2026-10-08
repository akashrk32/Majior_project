import cv2
import numpy as np
from pathlib import Path
import json

failed_stones = [
    "stone_kn_000006",
    "stone_kn_000007",
    "stone_kn_000010",
    "stone_kn_000011",
    "stone_kn_000019"
]

stones_dir = Path("kannada_stones")
bin_dir = Path("data/binarized")
pre_dir = Path("data/preprocessed")

print("=== FORENSIC DIAGNOSIS OF 5 SEGMENTATION FAILURES ===")

for name in failed_stones:
    # Find matching raw image
    img_candidates = list(stones_dir.glob(f"{name}.*"))
    if not img_candidates:
        print(f"Image not found for {name}")
        continue
    img_path = img_candidates[0]
    img = cv2.imread(str(img_path))
    h, w, c = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Calculate image statistics
    mean_val = float(np.mean(gray))
    std_val = float(np.std(gray))
    min_val, max_val = int(np.min(gray)), int(np.max(gray))
    contrast_ratio = (max_val - min_val) / 255.0
    
    # Check existing binarized mask if exists
    # stone_kn_000006 -> stone_006_binarized.png
    num_idx = int(name.split("_")[-1])
    bin_path = bin_dir / f"stone_{num_idx:03d}_binarized.png"
    
    ink_pct = 0.0
    num_components = 0
    if bin_path.exists():
        b_img = cv2.imread(str(bin_path), cv2.IMREAD_GRAYSCALE)
        ink_pixels = np.sum(b_img == 255)
        ink_pct = 100.0 * ink_pixels / b_img.size
        # Connected components
        num_labels, labels_im, stats, centroids = cv2.connectedComponentsWithStats((b_img == 255).astype(np.uint8))
        num_components = num_labels - 1
    
    print(f"\n[{name}] ({w}x{h}):")
    print(f"  Raw Gray Mean: {mean_val:.1f}, Std: {std_val:.1f}, Min: {min_val}, Max: {max_val}, Contrast: {contrast_ratio:.2f}")
    print(f"  Current Binarized Mask: {bin_path.name} (exists={bin_path.exists()})")
    print(f"  Current Ink Percentage: {ink_pct:.3f}%")
    print(f"  Connected Components:   {num_components}")
