"""
Phase 1 Diagnostic Experiment for SHILORA Robust Stone Inscription Binarization
================================================================================
Compares model behavior across four input variants:
  Input A: RAW original RGB image
  Input B: V3 preprocessed image (standard 3-channel)
  Input C: Lightly normalized V3 (bounded contrast / smoothed histogram)
  Input D: V3 luminance-preserving / guided fusion with RAW RGB color

Computes all required diagnostic statistics:
  - probability-map mean, max, P90, P95, P99
  - foreground ratio at threshold 0.5
  - connected component count
  - estimated character height (robust IQR)
  - multi-scale agreement
  - blank-image flag
"""

import os
import sys
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "Brahmi-OCR-main" / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from episam_binarizer.unet_model import AttentionUNet

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = BACKEND_DIR / "episam_binarizer" / "binarizer.pth"

def load_model():
    model = AttentionUNet(in_channels=3, out_classes=1, bilinear=False)
    state = torch.load(MODEL_PATH, map_location=DEVICE)
    model.load_state_dict(state)
    model.to(DEVICE)
    model.eval()
    return model

def predict_patchwise(model, image_tensor, patch_size, overlap, in_size=512):
    model.eval()
    c, h, w = image_tensor.shape
    stride = max(1, patch_size - overlap)
    pad_h = (stride - (h - overlap) % stride) % stride
    pad_w = (stride - (w - overlap) % stride) % stride
    image_padded = F.pad(image_tensor, (0, pad_w, 0, pad_h), mode='reflect').unsqueeze(0)
    _, _, H, W = image_padded.shape
    prediction_canvas = torch.zeros((1, 1, H, W), device=DEVICE)
    count_canvas = torch.zeros((1, 1, H, W), device=DEVICE)

    patch_coords = []
    for y in range(0, H - overlap, stride):
        for x in range(0, W - overlap, stride):
            patch_coords.append((y, x))

    batch_size = 4
    for i in range(0, len(patch_coords), batch_size):
        batch_indices = patch_coords[i:i + batch_size]
        patches = [image_padded[:, :, y:y+patch_size, x:x+patch_size] for y, x in batch_indices]
        batch_tensor = torch.cat(patches, dim=0).to(DEVICE)

        with torch.inference_mode():
            batch_in = F.interpolate(batch_tensor, size=(in_size, in_size), mode='bilinear', align_corners=False)
            pred_batch = torch.sigmoid(model(batch_in))
            pred_orig = F.interpolate(pred_batch, size=(patch_size, patch_size), mode='bilinear', align_corners=False)

        for b_idx, (y, x) in enumerate(batch_indices):
            prediction_canvas[:, :, y:y+patch_size, x:x+patch_size] += pred_orig[b_idx:b_idx+1]
            count_canvas[:, :, y:y+patch_size, x:x+patch_size] += 1

    prediction_canvas /= (count_canvas + 1e-8)
    return prediction_canvas[:, :, :h, :w].squeeze().cpu().numpy()

def get_robust_character_height(pred_prob, threshold=0.5):
    pred_bin = (pred_prob > threshold).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(pred_bin, connectivity=8)
    if num_labels <= 1:
        return 0.0, 0
    heights = stats[1:, cv2.CC_STAT_HEIGHT]
    areas = stats[1:, cv2.CC_STAT_AREA]
    valid = (areas >= 10) & (areas <= pred_prob.size * 0.1) # reject tiny speckles & huge background chunks
    h_valid = heights[valid]
    if len(h_valid) == 0:
        return 0.0, 0
    q1, q3 = np.percentile(h_valid, [25, 75])
    iqr = q3 - q1
    inliers = h_valid[(h_valid >= q1 - 1.5 * iqr) & (h_valid <= q3 + 1.5 * iqr)]
    robust_h = float(np.mean(inliers)) if len(inliers) > 0 else float(np.median(h_valid))
    return robust_h, int(np.sum(valid))

def run_multiscale_inference(model, img_rgb):
    # Normalize image to tensor [0, 1]
    tensor = transforms.ToTensor()(img_rgb)
    c, h, w = tensor.shape

    # Scales: 256, 384, 512, 768 bounded by dimensions
    min_dim = min(h, w)
    scales = [256, 384, 512, 768]
    # Filter scales that make sense: if image is smaller than patch, patch is clamped
    actual_scales = []
    for s in scales:
        clamped_s = min(s, min_dim)
        if clamped_s not in actual_scales:
            actual_scales.append(clamped_s)

    scale_preds = {}
    for s in actual_scales:
        overlap = max(16, s // 2)
        pred = predict_patchwise(model, tensor, patch_size=s, overlap=overlap, in_size=512)
        scale_preds[s] = pred

    # Official Stage 1 coarse prediction: max across scales
    preds_list = list(scale_preds.values())
    fused_max = np.maximum.reduce(preds_list)
    
    # Calculate multi-scale agreement: pairwise correlation among scales
    if len(preds_list) > 1:
        corrs = []
        for i in range(len(preds_list)):
            for j in range(i+1, len(preds_list)):
                c_val = np.corrcoef(preds_list[i].flatten(), preds_list[j].flatten())[0, 1]
                if not np.isnan(c_val):
                    corrs.append(c_val)
        ms_agreement = float(np.mean(corrs)) if corrs else 1.0
    else:
        ms_agreement = 1.0

    return fused_max, scale_preds, ms_agreement

def create_input_variants(raw_path, prep_path):
    raw_bgr = cv2.imread(str(raw_path))
    prep_bgr = cv2.imread(str(prep_path))
    if raw_bgr is None or prep_bgr is None:
        raise ValueError(f"Could not load {raw_path} or {prep_path}")
    
    # Ensure same resolution
    h, w = prep_bgr.shape[:2]
    if raw_bgr.shape[:2] != (h, w):
        raw_bgr = cv2.resize(raw_bgr, (w, h), interpolation=cv2.INTER_AREA)

    # Variant A: Original Raw RGB
    var_A = cv2.cvtColor(raw_bgr, cv2.COLOR_BGR2RGB)

    # Variant B: V3 Preprocessed RGB
    var_B = cv2.cvtColor(prep_bgr, cv2.COLOR_BGR2RGB)

    # Variant C: Lightly normalized V3 (bounded contrast stretch preserving natural midtone balance)
    prep_gray = cv2.cvtColor(prep_bgr, cv2.COLOR_BGR2GRAY)
    p2, p98 = np.percentile(prep_gray, (2, 98))
    norm_c = np.clip((prep_gray.astype(np.float32) - p2) / (p98 - p2 + 1e-5) * 255.0, 0, 255).astype(np.uint8)
    var_C = cv2.cvtColor(norm_c, cv2.COLOR_GRAY2RGB)

    # Variant D: V3 luminance-preserving model input adapter
    # Blend raw chromaticity (Lab a, b) with V3 luminance L, with gentle tone compression
    raw_lab = cv2.cvtColor(raw_bgr, cv2.COLOR_BGR2LAB)
    L_raw, A_raw, B_raw = cv2.split(raw_lab)
    
    # Match V3 luminance mean and standard deviation to RAW natural luminance
    v3_L = prep_gray.astype(np.float32)
    v3_norm = (v3_L - v3_L.mean()) / (v3_L.std() + 1e-5)
    matched_L = np.clip(v3_norm * (L_raw.std() * 0.8) + L_raw.mean(), 0, 255).astype(np.uint8)
    
    adapted_lab = cv2.merge([matched_L, A_raw, B_raw])
    adapted_bgr = cv2.cvtColor(adapted_lab, cv2.COLOR_LAB2BGR)
    var_D = cv2.cvtColor(adapted_bgr, cv2.COLOR_BGR2RGB)

    return {"A_RAW": var_A, "B_V3": var_B, "C_LIGHT_V3": var_C, "D_ADAPTED_V3": var_D}

def run_diagnostic():
    model = load_model()
    test_stones = ["stone_005", "stone_006", "stone_010", "stone_027", "stone_034"]
    results = []

    out_diag_dir = PROJECT_ROOT / "scratch" / "phase1_diagnostic"
    out_diag_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("PHASE 1 DIAGNOSTIC EXPERIMENT: RAW vs V3 vs LIGHT_V3 vs ADAPTED_V3")
    print(f"Device: {DEVICE}")
    print("=" * 80)

    for sid in test_stones:
        raw_path = PROJECT_ROOT / "data" / "raw" / f"{sid}.jpg"
        prep_path = PROJECT_ROOT / "data" / "preprocessed" / f"{sid}_preprocessed.png"

        variants = create_input_variants(raw_path, prep_path)

        for v_name, img_rgb in variants.items():
            fused_max, scale_preds, ms_agree = run_multiscale_inference(model, img_rgb)
            
            p_mean = float(np.mean(fused_max))
            p_max = float(np.max(fused_max))
            p90, p95, p99 = [float(x) for x in np.percentile(fused_max, [90, 95, 99])]
            fg_ratio_05 = float(np.mean(fused_max > 0.5))
            char_h, comp_count = get_robust_character_height(fused_max, threshold=0.5)
            is_blank = bool(fg_ratio_05 < 0.005 or comp_count < 3)

            rec = {
                "stone_id": sid,
                "variant": v_name,
                "p_mean": round(p_mean, 4),
                "p_max": round(p_max, 4),
                "p90": round(p90, 4),
                "p95": round(p95, 4),
                "p99": round(p99, 4),
                "fg_ratio_05": round(fg_ratio_05, 4),
                "comp_count": comp_count,
                "robust_char_h": round(char_h, 1),
                "ms_agreement": round(ms_agree, 3),
                "is_blank": is_blank
            }
            results.append(rec)
            print(f"[{sid}] [{v_name:<12}] P_mean: {p_mean:.3f} | P_max: {p_max:.3f} | P95: {p95:.3f} | FG(0.5): {fg_ratio_05*100:.2f}% | CC: {comp_count:3d} | H: {char_h:4.1f} | Blank: {is_blank}")

            # Save preview visualization of fused_max
            preview_bgr = (fused_max * 255).astype(np.uint8)
            cv2.imwrite(str(out_diag_dir / f"{sid}_{v_name}_fused_prob.png"), preview_bgr)
            cv2.imwrite(str(out_diag_dir / f"{sid}_{v_name}_bin05.png"), ((fused_max > 0.5)*255).astype(np.uint8))

    df = pd.DataFrame(results)
    out_csv = PROJECT_ROOT / "scratch" / "phase1_diagnostic_results.csv"
    df.to_csv(out_csv, index=False)
    print("\nDiagnostic Results Saved to:", out_csv)

if __name__ == "__main__":
    run_diagnostic()
