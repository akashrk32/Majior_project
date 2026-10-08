import cv2
import numpy as np

prob = cv2.imread("scratch/prob_256.png", cv2.IMREAD_GRAYSCALE)
print("prob_256 shape:", prob.shape)
print("Min:", prob.min(), "Max:", prob.max(), "Mean:", prob.mean())

for th in [15, 25, 40, 60, 80, 100]:
    mask = (prob > th).astype(np.uint8) * 255
    fg_pct = np.mean(mask == 255) * 100
    n_cc, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    areas = stats[1:, cv2.CC_STAT_AREA] if n_cc > 1 else [0]
    print(f"Th={th:3d} (prob={th/255:.2f}): FG={fg_pct:5.2f}%, CCs={n_cc-1:4d}, MedArea={np.median(areas):4.1f}")
