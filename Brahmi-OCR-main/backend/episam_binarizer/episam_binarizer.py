"""
Official EpiSAM / Shilalekhya Inscription Binarizer Pipeline
============================================================
Extracted directly from the official repository:
  Repository: https://github.com/ihdia/shilalekhya-binarization
  Paper: "Unveiling Text in Challenging Stone Inscriptions: A Character-Context-Aware Patching Strategy for Binarization"
  Authors: Pratyush Jena, Amal Joseph, Arnav Sharma, Ravi Kiran Sarvadevabhatla (IHDIA, IIIT Hyderabad)
  Model: AttentionUNet (trained on Mythic Society stone inscriptions)
"""

import os
import random
from pathlib import Path
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image

try:
    from .unet_model import AttentionUNet
except (ImportError, ValueError):
    from unet_model import AttentionUNet

# Maximize CPU multithreading efficiency
num_cores = os.cpu_count() or 4
torch.set_num_threads(min(num_cores, 8))


class EpiSAMBinarizer:
    """
    Official EpiSAM / Shilalekhya Binarizer implementing the Attention U-Net
    model trained on challenging stone inscriptions.
    """
    def __init__(self, model_path=None, device=None, in_size=512, resize_size=1200):
        if model_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "binarizer.pth")
            
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"EpiSAM binarizer weights not found at: {model_path}")

        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.in_size = in_size
        self.resize_size = resize_size

        print(f"[EpiSAM] Loading AttentionUNet from: {model_path} on {self.device} ({torch.get_num_threads()} threads)")
        self.model = AttentionUNet(in_channels=3, out_classes=1, bilinear=False)
        state_dict = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()
        print("[EpiSAM] Model loaded successfully.")

    def predict_full_image_patchwise(self, image_tensor, patch_size, overlap, batch_size=4):
        """
        Batched sliding-window patchwise prediction for high CPU throughput.
        """
        self.model.eval()
        c, h, w = image_tensor.shape
        stride = patch_size - overlap
        pad_h = (stride - (h - overlap) % stride) % stride
        pad_w = (stride - (w - overlap) % stride) % stride
        image_padded = F.pad(image_tensor, (0, pad_w, 0, pad_h), mode='reflect').unsqueeze(0)
        _, _, H, W = image_padded.shape
        prediction_canvas = torch.zeros((1, 1, H, W), device=self.device)
        count_canvas = torch.zeros((1, 1, H, W), device=self.device)

        patch_coords = []
        for y in range(0, H - overlap, stride):
            for x in range(0, W - overlap, stride):
                patch_coords.append((y, x))

        # Process patches in batches
        for i in range(0, len(patch_coords), batch_size):
            batch_indices = patch_coords[i:i + batch_size]
            patches = [image_padded[:, :, y:y+patch_size, x:x+patch_size] for y, x in batch_indices]
            batch_tensor = torch.cat(patches, dim=0)

            with torch.inference_mode():
                batch_in = F.interpolate(batch_tensor, size=(self.in_size, self.in_size), mode='bilinear', align_corners=False)
                pred_batch = torch.sigmoid(self.model(batch_in.to(self.device)))
                pred_orig = F.interpolate(pred_batch, size=(patch_size, patch_size), mode='bilinear', align_corners=False)

            for b_idx, (y, x) in enumerate(batch_indices):
                prediction_canvas[:, :, y:y+patch_size, x:x+patch_size] += pred_orig[b_idx:b_idx+1]
                count_canvas[:, :, y:y+patch_size, x:x+patch_size] += 1

        prediction_canvas /= (count_canvas + 1e-8)
        return prediction_canvas[:, :, :h, :w].squeeze().cpu().numpy()

    def binarize(self, image_bgr, threshold=0.40, fast_single_scale=True, invert_output_for_ocr=True):
        """
        Executes the official EpiSAM / Shilalekhya Binarization pipeline on an image.
        
        Args:
            image_bgr: OpenCV BGR image
            threshold: Sigmoid probability cutoff for text stroke segmentation (default: 0.40)
            fast_single_scale: Uses optimal 512 patch scale for fastest inference.
            invert_output_for_ocr: If True, outputs black text on white background (OCR format).
                                   If False, outputs white text on black background (raw mask).
                                   
        Returns:
            binary_mask: np.ndarray (uint8, 0 or 255)
            clean_bgr: 3-channel image ready for OCR / display
        """
        if image_bgr is None or image_bgr.size == 0:
            raise ValueError("Invalid image input for EpiSAM binarize")

        h_orig, w_orig = image_bgr.shape[:2]

        # Convert to RGB tensor
        img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        
        # Proportional resize if larger than resize_size
        scale = 1.0
        if max(h_orig, w_orig) > self.resize_size:
            scale = self.resize_size / float(max(h_orig, w_orig))
            scaled_w = int(w_orig * scale)
            scaled_h = int(h_orig * scale)
            img_rgb_proc = cv2.resize(img_rgb, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)
        else:
            img_rgb_proc = img_rgb.copy()

        image_tensor = transforms.ToTensor()(Image.fromarray(img_rgb_proc))
        _, h, w = image_tensor.shape

        if fast_single_scale:
            scales = [min(512, max(h, w))]
        else:
            scales = [min(s, max(h, w)) for s in [256, 512]]

        prediction_masks = []
        for patch_size in scales:
            p_size = min(patch_size, min(h, w)) if min(h, w) > 64 else min(h, w)
            if p_size < 32:
                p_size = 32
            overlap = max(16, p_size // 3)
            pred_mask = self.predict_full_image_patchwise(
                image_tensor, patch_size=p_size, overlap=overlap, batch_size=4
            )
            prediction_masks.append(pred_mask)

        # Fuse predictions using max
        fused = np.maximum.reduce(prediction_masks) if len(prediction_masks) > 1 else prediction_masks[0]
        th = 0.40 if (threshold is None or threshold <= 0) else threshold
        pseudo_gt_bin = (fused > th).astype(np.uint8) * 255

        # Resize back to original resolution if needed
        if scale != 1.0:
            final_mask = cv2.resize(pseudo_gt_bin, (w_orig, h_orig), interpolation=cv2.INTER_NEAREST)
        else:
            final_mask = pseudo_gt_bin

        # Format for OCR: Black characters on pure white background
        if invert_output_for_ocr:
            clean_bgr = np.full((h_orig, w_orig, 3), 255, dtype=np.uint8)
            clean_bgr[final_mask == 255] = [0, 0, 0]
        else:
            clean_bgr = np.zeros((h_orig, w_orig, 3), dtype=np.uint8)
            clean_bgr[final_mask == 255] = [255, 255, 255]

        return final_mask, clean_bgr
