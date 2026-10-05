"""
SHILORA - Stone Inscription Image Quality Analysis
Analyzes contrast, noise, gradients, and illumination statistics to adaptively
tune stone preprocessing parameters without human intervention.
"""

from dataclasses import dataclass, asdict
import cv2
import numpy as np


@dataclass
class QualityMetrics:
    image_width: int
    image_height: int
    rms_contrast: float
    tenengrad: float
    local_std: float
    mean_intensity: float
    intensity_std: float
    dynamic_range: float
    estimated_noise: float
    quality_tier: str  # 'LOW', 'MEDIUM', 'HIGH'
    
    # Adaptive parameter recommendations
    illumination_sigma: float
    illumination_scale: float
    clahe_clip_limit: float
    clahe_tile_grid: int
    sharpen_sigma: float
    sharpen_amount: float

    def to_dict(self):
        return asdict(self)


def estimate_image_noise(gray: np.ndarray) -> float:
    """
    Robust noise estimation using Median Absolute Deviation (MAD) of the Laplacian:
    sigma_n = median(|Laplacian(I)|) / (0.6745 * sqrt(30))
    for a 3x3 Laplacian mask [[1, -2, 1], [-2, 4, -2], [1, -2, 1]].
    """
    h, w = gray.shape[:2]
    # Standard Laplacian noise estimation kernel
    kernel = np.array([[1, -2, 1],
                       [-2, 4, -2],
                       [1, -2, 1]], dtype=np.float32)
    lap = cv2.filter2D(gray.astype(np.float32), -1, kernel)
    sigma_n = float(np.median(np.abs(lap))) / (0.6745 * np.sqrt(30.0) + 1e-8)
    return round(sigma_n, 4)


def calculate_local_std(gray: np.ndarray, window_size: int = 15) -> float:
    """
    Computes the mean of local standard deviations across the image
    using fast box filters: std = sqrt(E[X^2] - (E[X])^2).
    """
    gray_f = gray.astype(np.float32)
    ksize = (window_size, window_size)
    mean = cv2.blur(gray_f, ksize)
    sqr_mean = cv2.blur(gray_f * gray_f, ksize)
    variance = np.maximum(sqr_mean - mean * mean, 0.0)
    local_std_map = np.sqrt(variance)
    return round(float(np.mean(local_std_map)), 4)


def calculate_tenengrad(gray: np.ndarray) -> float:
    """
    Computes Tenengrad gradient energy:
    Normalized sum of squared Sobel gradient magnitudes (Gx^2 + Gy^2) / N.
    """
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag_sq = gx * gx + gy * gy
    return round(float(np.mean(grad_mag_sq)), 2)


def analyze_image_quality(image_bgr_or_gray: np.ndarray) -> QualityMetrics:
    """
    Analyzes epigraphical stone image quality and recommends conservative,
    adaptive preprocessing parameters tailored to the stone condition.
    """
    if len(image_bgr_or_gray.shape) == 3:
        h, w = image_bgr_or_gray.shape[:2]
        gray = cv2.cvtColor(image_bgr_or_gray, cv2.COLOR_BGR2GRAY)
    else:
        h, w = image_bgr_or_gray.shape[:2]
        gray = image_bgr_or_gray.copy()

    # 1. Basic intensity statistics
    mean_val = float(np.mean(gray))
    std_val = float(np.std(gray))
    rms_contrast = round(std_val / 255.0, 4)

    # 2. Dynamic range (robust percentile difference)
    p1, p99 = np.percentile(gray, [1, 99])
    dynamic_range = round(float(p99 - p1), 2)

    # 3. Local detail and gradient energy
    local_std = calculate_local_std(gray, window_size=15)
    tenengrad = calculate_tenengrad(gray)

    # 4. Estimated noise
    estimated_noise = estimate_image_noise(gray)

    # 5. Quality classification logic
    # Stones with very low contrast or high noise need careful parameter tuning
    # Stones with strong gradients require moderate handling to avoid haloing
    if rms_contrast < 0.12 or estimated_noise > 8.0 or dynamic_range < 70.0:
        quality_tier = "LOW"
    elif rms_contrast > 0.22 and estimated_noise < 4.0 and dynamic_range > 140.0:
        quality_tier = "HIGH"
    else:
        quality_tier = "MEDIUM"

    # 6. Adaptive parameter determination
    # Base ranges:
    # - Gaussian illumination sigma: 20 – 60 (scaled mildly with image resolution)
    # - CLAHE clipLimit: 1.5 – 3.0
    # - CLAHE tileGridSize: 8x8 – 16x16
    # - Sharpening sigma: 0.7 – 1.5
    # - Unsharp amount: 0.15 – 0.50

    # Scale base sigma with resolution (larger stones need broader illumination estimation)
    diag_res = np.sqrt(h * w)
    res_factor = np.clip(diag_res / 1500.0, 0.7, 1.6)

    if quality_tier == "LOW":
        # Low quality / weathered / noisy:
        # Stronger illumination normalization (flattens murky surfaces)
        # Moderate CLAHE (avoids amplifying grain)
        # Very conservative sharpening (prevents noise spikes)
        illum_sigma = float(np.clip(45.0 * res_factor, 30.0, 60.0))
        illum_scale = 145.0
        clahe_clip = 1.8
        clahe_grid = 12
        sharp_sigma = 1.2
        sharp_amount = 0.20

    elif quality_tier == "HIGH":
        # High quality / clear incision:
        # Mild normalization
        # Mild CLAHE (doesn't wash out existing contrast)
        # Very mild sharpening (glyph edges already crisp)
        illum_sigma = float(np.clip(30.0 * res_factor, 20.0, 45.0))
        illum_scale = 155.0
        clahe_clip = 1.6
        clahe_grid = 10
        sharp_sigma = 0.9
        sharp_amount = 0.25

    else:  # MEDIUM
        # Standard balanced epigraphy settings (matching the successful baseline)
        illum_sigma = float(np.clip(35.0 * res_factor, 25.0, 50.0))
        illum_scale = 150.0
        clahe_clip = 2.2
        clahe_grid = 12
        sharp_sigma = 1.1
        sharp_amount = 0.35

    return QualityMetrics(
        image_width=int(w),
        image_height=int(h),
        rms_contrast=rms_contrast,
        tenengrad=tenengrad,
        local_std=local_std,
        mean_intensity=round(mean_val, 2),
        intensity_std=round(std_val, 2),
        dynamic_range=dynamic_range,
        estimated_noise=estimated_noise,
        quality_tier=quality_tier,
        illumination_sigma=round(illum_sigma, 2),
        illumination_scale=round(illum_scale, 2),
        clahe_clip_limit=round(clahe_clip, 2),
        clahe_tile_grid=int(clahe_grid),
        sharpen_sigma=round(sharp_sigma, 2),
        sharpen_amount=round(sharp_amount, 2)
    )
