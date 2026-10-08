"""
SHILORA EpiSAM Character Instance Segmentation & Line Reconstruction Pipeline
=============================================================================
Optimized for high-throughput, memory-efficient CPU/GPU execution.
Extracts character masks, bounding boxes, confidences, and reconstructs reading-order lines.
"""

import os
import sys
import json
import csv
import time
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

root_dir = Path(__file__).resolve().parent.parent
episam_dir = root_dir / "episam_official"
if str(episam_dir) not in sys.path:
    sys.path.insert(0, str(episam_dir))

import torch
from segment_anything import sam_model_registry
from segment_anything.utils.transforms import ResizeLongestSide


def extract_character_candidates(binarized_img, min_area=60, max_area_ratio=0.15):
    """
    Extract candidate character centroids and bounding boxes from binarized image.
    """
    if len(binarized_img.shape) == 3:
        gray = cv2.cvtColor(binarized_img, cv2.COLOR_BGR2GRAY)
    else:
        gray = binarized_img.copy()

    white_ratio = np.mean(gray > 127)
    if white_ratio > 0.5:
        binary = (gray < 127).astype(np.uint8) * 255
    else:
        binary = (gray > 127).astype(np.uint8) * 255

    h, w = binary.shape
    max_area = h * w * max_area_ratio

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

    candidates = []
    for label_id in range(1, num_labels):
        area = stats[label_id, cv2.CC_STAT_AREA]
        if area < min_area or area > max_area:
            continue

        x1 = int(stats[label_id, cv2.CC_STAT_LEFT])
        y1 = int(stats[label_id, cv2.CC_STAT_TOP])
        bw = int(stats[label_id, cv2.CC_STAT_WIDTH])
        bh = int(stats[label_id, cv2.CC_STAT_HEIGHT])
        x2 = x1 + bw
        y2 = y1 + bh

        cx, cy = centroids[label_id]

        candidates.append({
            "component_id": int(label_id),
            "bbox": [x1, y1, x2, y2],
            "centroid": [float(cx), float(cy)],
            "area": int(area),
            "width": bw,
            "height": bh
        })

    return binary, candidates


def cluster_into_lines(characters, line_y_tolerance_ratio=0.6):
    """
    Group character instances into lines and sort left-to-right (Kannada reading order).
    """
    if not characters:
        return []

    heights = [c["height"] for c in characters]
    median_h = np.median(heights) if heights else 30
    y_tol = max(15, median_h * line_y_tolerance_ratio)

    sorted_by_y = sorted(characters, key=lambda c: c["centroid"][1])

    lines = []
    for c in sorted_by_y:
        cy = c["centroid"][1]
        placed = False
        for line in lines:
            line_avg_y = np.mean([item["centroid"][1] for item in line])
            if abs(cy - line_avg_y) <= y_tol:
                line.append(c)
                placed = True
                break
        if not placed:
            lines.append([c])

    lines = sorted(lines, key=lambda line: np.mean([c["centroid"][1] for c in line]))

    structured_lines = []
    for line_idx, line in enumerate(lines, start=1):
        line_sorted = sorted(line, key=lambda c: c["centroid"][0])
        for order_idx, c in enumerate(line_sorted, start=1):
            c["line_id"] = line_idx
            c["reading_order"] = order_idx
        structured_lines.append(line_sorted)

    return structured_lines


def fast_bbox_nms(candidates, scores, iou_threshold=0.65):
    """
    Fast Bounding Box NMS to prune duplicate candidate prompts.
    """
    if not candidates:
        return []
    
    order = np.argsort(scores)[::-1]
    keep = []
    suppressed = np.zeros(len(candidates), dtype=bool)

    for i in order:
        if suppressed[i]:
            continue
        keep.append(i)
        x1_i, y1_i, x2_i, y2_i = candidates[i]["bbox"]
        area_i = (x2_i - x1_i) * (y2_i - y1_i)

        for j in order:
            if i == j or suppressed[j]:
                continue
            x1_j, y1_j, x2_j, y2_j = candidates[j]["bbox"]
            area_j = (x2_j - x1_j) * (y2_j - y1_j)

            ix1 = max(x1_i, x1_j)
            iy1 = max(y1_i, y1_j)
            ix2 = min(x2_i, x2_j)
            iy2 = min(y2_i, y2_j)

            if ix1 < ix2 and iy1 < iy2:
                inter = (ix2 - ix1) * (iy2 - iy1)
                iou = inter / (area_i + area_j - inter + 1e-6)
                if iou > iou_threshold:
                    suppressed[j] = True
    return keep


def run_episam_inference(sam, image_rgb, candidates, device="cpu"):
    """
    Run prompt-guided segmentation using EpiSAM with local window extraction.
    """
    transform = ResizeLongestSide(sam.image_encoder.img_size)
    orig_h, orig_w = image_rgb.shape[:2]

    # SAM Image Encoder
    img_resized = transform.apply_image(image_rgb)
    img_tensor = torch.as_tensor(img_resized, device=device).permute(2, 0, 1).contiguous()[None, :, :, :]
    img_norm = (img_tensor - sam.pixel_mean) / sam.pixel_std

    pad_h = sam.image_encoder.img_size - img_norm.shape[2]
    pad_w = sam.image_encoder.img_size - img_norm.shape[3]
    img_padded = torch.nn.functional.pad(img_norm, (0, pad_w, 0, pad_h))

    with torch.no_grad():
        image_embeddings = sam.image_encoder(img_padded)

    segmented_characters = []
    batch_size = 32

    # Process prompts in batches
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i + batch_size]
        boxes_np = np.array([c["bbox"] for c in batch])
        boxes_rescaled = transform.apply_boxes(boxes_np, (orig_h, orig_w))
        box_tensor = torch.as_tensor(boxes_rescaled, dtype=torch.float, device=device)

        points_np = np.array([[c["centroid"]] for c in batch])
        points_rescaled = transform.apply_coords(points_np, (orig_h, orig_w))
        point_tensor = torch.as_tensor(points_rescaled, dtype=torch.float, device=device)
        point_labels = torch.ones((len(batch), 1), dtype=torch.int, device=device)

        with torch.no_grad():
            sparse_embeddings, dense_embeddings = sam.prompt_encoder(
                points=(point_tensor, point_labels),
                boxes=box_tensor,
                masks=None
            )
            low_res_masks, iou_predictions = sam.mask_decoder(
                image_embeddings=image_embeddings,
                image_pe=sam.prompt_encoder.get_dense_pe(),
                sparse_prompt_embeddings=sparse_embeddings,
                dense_prompt_embeddings=dense_embeddings,
                multimask_output=False
            )

        # Extract local mask crop from 256x256 low_res_masks directly
        # Map 1024x1024 image space to 256x256 mask space (factor of 4)
        scale_x = img_resized.shape[1] / orig_w
        scale_y = img_resized.shape[0] / orig_h

        lrm_np = (low_res_masks > 0.0).cpu().numpy().squeeze(1) # shape: (B, 256, 256)
        ious = iou_predictions.cpu().numpy().squeeze(1) # shape: (B,)

        for j, c in enumerate(batch):
            conf = float(ious[j])
            x1, y1, x2, y2 = c["bbox"]
            bw = x2 - x1
            bh = y2 - y1

            # Map bbox to 256x256 grid
            mx1 = int(round((x1 * scale_x) / 4.0))
            my1 = int(round((y1 * scale_y) / 4.0))
            mx2 = int(round((x2 * scale_x) / 4.0)) + 1
            my2 = int(round((y2 * scale_y) / 4.0)) + 1

            mx1 = max(0, min(255, mx1))
            my1 = max(0, min(255, my1))
            mx2 = max(mx1 + 1, min(256, mx2))
            my2 = max(my1 + 1, min(256, my2))

            crop_256 = lrm_np[j, my1:my2, mx1:mx2].astype(np.uint8) * 255
            if crop_256.size > 0 and bw > 0 and bh > 0:
                char_mask = cv2.resize(crop_256, (bw, bh), interpolation=cv2.INTER_NEAREST)
            else:
                char_mask = np.ones((bh, bw), dtype=np.uint8) * 255

            mask_area = int(np.count_nonzero(char_mask > 0))

            if mask_area == 0:
                status = "FAILED_EMPTY"
            elif mask_area < 40:
                status = "QUESTIONABLE_TINY"
            elif mask_area > (orig_h * orig_w * 0.20):
                status = "QUESTIONABLE_HUGE"
            else:
                status = "VALID"

            segmented_characters.append({
                "character_id": len(segmented_characters) + 1,
                "bbox": c["bbox"],
                "centroid": c["centroid"],
                "area": mask_area,
                "width": bw,
                "height": bh,
                "confidence": round(conf, 4),
                "quality_status": status,
                "_local_mask": char_mask
            })

    # Fast Bounding Box NMS
    scores = [c["confidence"] for c in segmented_characters]
    keep_indices = fast_bbox_nms(segmented_characters, scores, iou_threshold=0.65)
    final_characters = [segmented_characters[k] for k in keep_indices]

    for idx, c in enumerate(final_characters, start=1):
        c["character_id"] = idx

    return final_characters


def process_stone_inscription(sam, image_path, binarized_path, output_dirs, device="cpu"):
    """
    Process a single stone inscription: candidate extraction, segmentation, line reconstruction.
    """
    stone_id = Path(image_path).stem
    bin_img = cv2.imread(str(binarized_path))
    if bin_img is None:
        return {"stone_id": stone_id, "status": "FAILED_READ_BINARY"}

    raw_img = cv2.imread(str(image_path))
    if raw_img is not None:
        rgb_img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB)
    else:
        rgb_img = cv2.cvtColor(bin_img, cv2.COLOR_BGR2RGB)

    binary_ink, candidates = extract_character_candidates(bin_img)
    if not candidates:
        return {"stone_id": stone_id, "status": "NO_CANDIDATES_FOUND"}

    char_instances = run_episam_inference(sam, rgb_img, candidates, device=device)
    lines = cluster_into_lines(char_instances)

    char_out_dir = output_dirs["characters"] / stone_id
    pred_mask_dir = output_dirs["predictions"] / stone_id
    line_out_dir = output_dirs["lines"] / stone_id
    char_out_dir.mkdir(parents=True, exist_ok=True)
    pred_mask_dir.mkdir(parents=True, exist_ok=True)
    line_out_dir.mkdir(parents=True, exist_ok=True)

    h_img, w_img = bin_img.shape[:2]

    for char in char_instances:
        cid = char["character_id"]
        x1, y1, x2, y2 = char["bbox"]
        mask_crop = char["_local_mask"]

        char_crop = bin_img[y1:y2, x1:x2]
        if char_crop.size > 0:
            cv2.imwrite(str(char_out_dir / f"char_{cid:04d}.png"), char_crop)
            cv2.imwrite(str(pred_mask_dir / f"mask_{cid:04d}.png"), mask_crop)

        del char["_local_mask"]

    for line_idx, line_chars in enumerate(lines, start=1):
        if not line_chars:
            continue
        min_x = max(0, min(c["bbox"][0] for c in line_chars) - 5)
        min_y = max(0, min(c["bbox"][1] for c in line_chars) - 5)
        max_x = min(w_img, max(c["bbox"][2] for c in line_chars) + 5)
        max_y = min(h_img, max(c["bbox"][3] for c in line_chars) + 5)

        line_crop = bin_img[min_y:max_y, min_x:max_x]
        if line_crop.size > 0:
            line_filename = f"{stone_id}_line_{line_idx:03d}.png"
            cv2.imwrite(str(line_out_dir / line_filename), line_crop)

    # Save metadata JSON
    meta_path = output_dirs["metadata"] / f"{stone_id}_instances.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "stone_id": stone_id,
            "total_characters": len(char_instances),
            "total_lines": len(lines),
            "characters": char_instances
        }, f, indent=2)

    return {
        "stone_id": stone_id,
        "total_characters": len(char_instances),
        "total_lines": len(lines),
        "valid_characters": sum(1 for c in char_instances if c["quality_status"] == "VALID"),
        "questionable_characters": sum(1 for c in char_instances if "QUESTIONABLE" in c["quality_status"]),
        "status": "SUCCESS"
    }


def load_episam_model(checkpoint_path="models/episam/episam.pth", device="cpu"):
    """
    Loads official EpiSAM ViT-B model weights onto target device.
    """
    sam = sam_model_registry["vit_b"](checkpoint=str(checkpoint_path))
    sam.to(device=device)
    sam.eval()
    return sam


def segment_single_image(binarized_image, model, device="cpu", stone_id="temp_stone"):
    """
    Direct in-memory segmentation of a binarized numpy array using official EpiSAM.
    """
    h_img, w_img = binarized_image.shape[:2]
    binary_ink, candidates = extract_character_candidates(binarized_image)
    if not candidates:
        return {
            "stone_id": stone_id,
            "total_characters": 0,
            "total_lines": 0,
            "characters": [],
            "lines": [],
            "status": "NO_CANDIDATES"
        }

    if len(binarized_image.shape) == 2:
        rgb_img = cv2.cvtColor(binarized_image, cv2.COLOR_GRAY2RGB)
    else:
        rgb_img = cv2.cvtColor(binarized_image, cv2.COLOR_BGR2RGB)

    char_instances = run_episam_inference(model, rgb_img, candidates, device=device)
    lines = cluster_into_lines(char_instances)

    line_manifests = []
    for l_idx, l_chars in enumerate(lines, start=1):
        if not l_chars:
            continue
        min_x = max(0, min(c["bbox"][0] for c in l_chars) - 5)
        min_y = max(0, min(c["bbox"][1] for c in l_chars) - 5)
        max_x = min(w_img, max(c["bbox"][2] for c in l_chars) + 5)
        max_y = min(h_img, max(c["bbox"][3] for c in l_chars) + 5)
        line_manifests.append({
            "line_index": l_idx,
            "bbox": [min_x, min_y, max_x - min_x, max_y - min_y],
            "character_indices": [c["character_id"] for c in l_chars]
        })

    return {
        "stone_id": stone_id,
        "total_characters": len(char_instances),
        "total_lines": len(lines),
        "valid_characters": sum(1 for c in char_instances if c.get("quality_status") == "VALID"),
        "questionable_characters": sum(1 for c in char_instances if "QUESTIONABLE" in c.get("quality_status", "")),
        "characters": char_instances,
        "lines": line_manifests,
        "status": "SUCCESS"
    }

