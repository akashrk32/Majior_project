import cv2
import numpy as np
from pathlib import Path

failed_stones = [
    "stone_kn_000006",
    "stone_kn_000007",
    "stone_kn_000010",
    "stone_kn_000011",
    "stone_kn_000019"
]

stones_dir = Path("kannada_stones")

def adaptive_stone_binarize(img_bgr):
    """
    Scientifically justified adaptive fallback for severely eroded/low-contrast stone epigraphs:
    1. Multi-scale CLAHE with illumination compensation.
    2. Morphological Black-Hat to extract deep stroke relief grooves.
    3. Bilateral filter for stone texture smoothing without blurring stroke edges.
    4. Adaptive thresholding (Niblack/Sauvola style).
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # 1. Illumination normalization (large-scale morphological opening background subtraction)
    kernel_bg = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    background = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel_bg)
    norm_gray = cv2.subtract(gray, background)
    norm_gray = cv2.normalize(norm_gray, None, 0, 255, cv2.NORM_MINMAX)
    
    # 2. Adaptive CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(norm_gray)
    
    # 3. Bilateral filter to smooth stone grain while preserving stroke edges
    smooth = cv2.bilateralFilter(enhanced, 7, 50, 50)
    
    # 4. Adaptive Gaussian thresholding
    bin_mask = cv2.adaptiveThreshold(
        smooth, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, -5
    )
    
    # 5. Connected component filtering to remove tiny specks (< 15 px) and massive borders
    num_labels, labels_im, stats, centroids = cv2.connectedComponentsWithStats(bin_mask)
    clean_mask = np.zeros_like(bin_mask)
    valid_chars = 0
    total_area = img_bgr.shape[0] * img_bgr.shape[1]
    
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        w_box = stats[i, cv2.CC_STAT_WIDTH]
        h_box = stats[i, cv2.CC_STAT_HEIGHT]
        # Valid character size criteria
        if 20 <= area <= (total_area * 0.15) and 4 <= w_box <= 200 and 6 <= h_box <= 200:
            clean_mask[labels_im == i] = 255
            valid_chars += 1
            
    ink_pct = 100.0 * np.sum(clean_mask == 255) / clean_mask.size
    return clean_mask, ink_pct, valid_chars

print("=== TESTING ADAPTIVE ENHANCEMENT FALLBACK ===")
for name in failed_stones:
    p = list(stones_dir.glob(f"{name}.*"))[0]
    img = cv2.imread(str(p))
    mask, ink_pct, valid_chars = adaptive_stone_binarize(img)
    print(f"[{name}] Recovered Ink%: {ink_pct:.2f}%, Character components found: {valid_chars}")
