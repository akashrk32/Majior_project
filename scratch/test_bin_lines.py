import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

mask = cv2.imread("scratch/test_bin_256.png", cv2.IMREAD_GRAYSCALE)
h, w = mask.shape

# Horizontal projection profile of the binary mask
# Summing binary pixels along rows
horiz_proj = np.sum(mask > 0, axis=1)

# Smooth horizontal projection
smooth_proj = gaussian_filter1d(horiz_proj.astype(np.float32), sigma=4.0)

# Detect line peaks
peaks, props = find_peaks(smooth_proj, distance=18, prominence=50)
print(f"Detected lines from Attention U-Net binary mask: {len(peaks)}")
print("Peak rows (y):", peaks)

# Let's inspect bounding boxes for each peak
line_bands = []
for i in range(len(peaks)):
    cy = int(peaks[i])
    # Line height estimated between peaks
    if i > 0 and i < len(peaks) - 1:
        lh = int((peaks[i+1] - peaks[i-1]) / 2.0)
    elif i < len(peaks) - 1:
        lh = int(peaks[i+1] - peaks[i])
    elif i > 0:
        lh = int(peaks[i] - peaks[i-1])
    else:
        lh = 30
        
    lh = max(18, min(45, lh))
    y1 = max(0, int(cy - lh * 0.55))
    y2 = min(h, int(cy + lh * 0.55))
    
    # In each row band, find the actual left and right extent of inscription characters
    row_crop = mask[y1:y2, :]
    col_proj = np.sum(row_crop > 0, axis=0)
    col_indices = np.where(col_proj > 0)[0]
    
    if len(col_indices) > 20: # Must have at least a few characters
        x1 = max(0, int(col_indices[0]) - 5)
        x2 = min(w, int(col_indices[-1]) + 5)
        bw = x2 - x1
        bh = y2 - y1
        if bw > int(w * 0.25): # Genuine inscription line spans across the stone
            line_bands.append({
                "line_index": len(line_bands) + 1,
                "bbox": [x1, y1, bw, bh],
                "char_pixels": int(np.sum(row_crop > 0))
            })

print(f"Valid continuous inscription lines: {len(line_bands)}")
for lb in line_bands:
    print(f"Line {lb['line_index']:02d}: bbox={lb['bbox']}, px={lb['char_pixels']}")
