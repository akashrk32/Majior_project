"""
Brahmi OCR Backend - Python Flask API
Usage:
  1. Install dependencies: pip install -r requirements.txt
  2. Run: python app.py
  3. Backend will run at: http://127.0.0.1:5000
"""

import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import io
import base64
import os
import cv2
import onnxruntime as ort
import torch
import torch.nn as nn

try:
    import h5py
except ImportError:
    h5py = None
    print("WARNING: h5py not installed. MobileNetV2 .keras weights cannot be loaded. Run: pip install h5py")

# Import segmentation, GAN restorer, and official EpiSAM stone binarizer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from segmentation import detect_characters, sort_boxes, clean_image_noise, remove_background_noise
from gan_restorer import GANRestorer
from episam_binarizer.episam_binarizer import EpiSAMBinarizer

_episam_binarizer = None

def get_episam_binarizer():
    global _episam_binarizer
    if _episam_binarizer is None:
        _episam_binarizer = EpiSAMBinarizer()
    return _episam_binarizer


# ============================================================================
# COLOR IMAGE DETECTION & BINARIZATION
# ============================================================================

def is_color_image(image_bgr, saturation_threshold=18):
    """
    Returns True if the image is a genuine color photo.

    Checks mean HSV saturation. Grayscale images (including those with grey
    crack/erosion masks) will have near-zero saturation and return False.
    Black-and-white scans, grey-mask images, and already-binarized images
    are all correctly identified as NOT color and are left completely alone.
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    mean_saturation = float(hsv[:, :, 1].mean())
    print(f"[color_check] Mean HSV saturation = {mean_saturation:.2f} "
          f"(threshold={saturation_threshold}) -> "
          f"{'COLOR' if mean_saturation > saturation_threshold else 'GRAYSCALE/BW'}")
    return mean_saturation > saturation_threshold


def color_to_binary_inscription(image_bgr, max_proc_dim=1600):
    """
    Converts a COLOR stone inscription photo to a clean black-on-white binary.
    Primary: Uses official EpiSAM / Shilalekhya Attention U-Net binarizer model.
    Fallback: Multi-scale contrast & adaptive morphological filtering.
    
    Returns BGR image: clean black strokes on pure white background.
    """
    try:
        binarizer = get_episam_binarizer()
        _, clean_bgr = binarizer.binarize(image_bgr, threshold=0.40, fast_single_scale=True, invert_output_for_ocr=True)
        print("[color_binarize] Successfully binarized with official EpiSAM Attention U-Net")
        return clean_bgr
    except Exception as e:
        print(f"[color_binarize] EpiSAM inference failed: {e}. Falling back to heuristic pipeline.")
    h_orig, w_orig = image_bgr.shape[:2]

    # ── Stage 1: Resolution Normalization for Safe Processing ─────────────────
    scale = 1.0
    if max(h_orig, w_orig) > max_proc_dim:
        scale = max_proc_dim / float(max(h_orig, w_orig))
        proc_img = cv2.resize(image_bgr, (int(w_orig * scale), int(h_orig * scale)), 
                              interpolation=cv2.INTER_AREA)
    else:
        proc_img = image_bgr.copy()

    h, w = proc_img.shape[:2]

    # ── Stage 2: Bilateral Smooth & Grayscale ─────────────────────────────────
    smoothed = cv2.bilateralFilter(proc_img, d=7, sigmaColor=50, sigmaSpace=50)
    gray = cv2.cvtColor(smoothed, cv2.COLOR_BGR2GRAY)

    # ── Stage 3: Illumination Correction (Flatten uneven rock lighting) ───────
    bg_k = int(max(h, w) * 0.08) | 1
    bg_k = max(31, min(bg_k, 151))
    background = cv2.GaussianBlur(gray, (bg_k, bg_k), 0)
    illum_flat = np.clip((gray.astype(np.float32) / (background.astype(np.float32) + 1e-5)) * 200, 0, 255).astype(np.uint8)

    # ── Stage 4: CLAHE (Enhance low-contrast engraved grooves) ────────────────
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(illum_flat)

    # ── Stage 5: Adaptive Local Thresholding ──────────────────────────────────
    block_sz = int(max(h, w) * 0.035) | 1
    block_sz = max(15, min(block_sz, 51))
    stroke_mask = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, block_sz, 5
    )

    # Clean small 1-2px pepper noise
    k_noise = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    stroke_mask = cv2.morphologyEx(stroke_mask, cv2.MORPH_OPEN, k_noise)

    # ── Stage 6: Connected Components & Border/Shadow Rejection ──────────────
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(stroke_mask, connectivity=8)

    # Flag large components touching image edges (camera frame, shadow, pedestal)
    border_labels = set()
    for i in range(1, num_labels):
        bx = stats[i, cv2.CC_STAT_LEFT]
        by = stats[i, cv2.CC_STAT_TOP]
        bw = stats[i, cv2.CC_STAT_WIDTH]
        bh = stats[i, cv2.CC_STAT_HEIGHT]
        barea = stats[i, cv2.CC_STAT_AREA]
        if (bx <= 1 or by <= 1 or (bx + bw) >= (w - 2) or (by + bh) >= (h - 2)) and (barea > 0.02 * (w * h)):
            border_labels.add(i)

    # ── Stage 7: Percentile-based Character Component Filtering ───────────────
    valid_areas = [stats[i, cv2.CC_STAT_AREA] for i in range(1, num_labels) if i not in border_labels]
    clean_mask = np.zeros_like(stroke_mask)
    kept = 0

    if valid_areas:
        median_area = float(np.median(valid_areas))
        min_char_area = max(20, int(median_area * 0.15))
        max_char_area = int(w * h * 0.25)

        kept_labels = [i for i in range(1, num_labels)
                       if i not in border_labels and min_char_area <= stats[i, cv2.CC_STAT_AREA] <= max_char_area]
        lut = np.zeros(num_labels, dtype=np.uint8)
        if kept_labels:
            lut[kept_labels] = 255
        clean_mask = lut[labels]
        kept = len(kept_labels)

    # Reconnect delicate character strokes with gentle close
    k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    clean_mask = cv2.morphologyEx(clean_mask, cv2.MORPH_CLOSE, k_close)

    # Produce black strokes on pure white
    result = np.full((h, w, 3), 255, dtype=np.uint8)
    result[clean_mask == 255] = [0, 0, 0]

    # Restore to original resolution if scaled
    if scale != 1.0:
        result = cv2.resize(result, (w_orig, h_orig), interpolation=cv2.INTER_NEAREST)

    ink_pct = 100.0 * np.sum(clean_mask == 255) / clean_mask.size
    print(f"[color_binarize] kept_components={kept} ink_coverage={ink_pct:.2f}%")
    return result


def is_inverted_image(image_bgr,
                      dark_pct_threshold=60,
                      dark_bg_threshold=128,
                      max_saturation=60):
    """
    Returns True if the image has a DARK background with LIGHT characters.
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    hsv  = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    dark_pct        = 100.0 * float(np.sum(gray < dark_bg_threshold)) / gray.size
    median_pixel    = float(np.median(gray))
    mean_saturation = float(hsv[:, :, 1].mean())

    inverted = (dark_pct        > dark_pct_threshold and
                median_pixel    < dark_bg_threshold  and
                mean_saturation < max_saturation)

    print(f"[invert_check] dark={dark_pct:.1f}% median={median_pixel:.0f} "
          f"sat={mean_saturation:.1f} -> "
          f"{'INVERTED (will flip)' if inverted else 'normal polarity'}")
    return inverted


def invert_to_black_on_white(image_bgr):
    """
    Converts a polarity-inverted image (light chars on dark background) to
    clean BLACK characters on a PURE WHITE background.
    """
    gray     = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blurred  = cv2.GaussianBlur(gray, (3, 3), 0)
    inverted = cv2.bitwise_not(blurred)
    otsu_val, ink_mask = cv2.threshold(inverted, 0, 255,
                                       cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    k_open   = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    ink_mask = cv2.morphologyEx(ink_mask, cv2.MORPH_OPEN, k_open)
    result   = np.full_like(image_bgr, 255)
    result[ink_mask == 255] = [0, 0, 0]
    ink_pct = 100.0 * float(np.sum(ink_mask == 255)) / ink_mask.size
    print(f"[invert_binarize] otsu_threshold={otsu_val:.0f} "
          f"ink_coverage={ink_pct:.2f}%")
    return result


# ============================================================================
# SHARED PREPROCESSING HELPER
# ============================================================================

def preprocess_image(image_bgr):
    """
    Shared preprocessing pipeline used by all three routes:
      1. Inversion check + fix  (highest priority)
      2. Color binarization     (color stone photos only)
      3. Background noise removal

    Returns:
        cleaned_bgr        — processed OpenCV BGR image ready for segmentation
        image_was_inverted — bool
        image_was_color    — bool
        binary_image_b64   — base64 JPEG of the binarized image when a visual
                             transform was applied (invert / color), else None
    """
    image_was_inverted = is_inverted_image(image_bgr)
    binary_image_b64   = None

    if image_was_inverted:
        print("[preprocess] Inverted image detected -> flipping polarity")
        image_bgr = invert_to_black_on_white(image_bgr)
        pil = Image.fromarray(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
        buf = io.BytesIO()
        pil.save(buf, format="JPEG")
        binary_image_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    image_was_color = (not image_was_inverted) and is_color_image(image_bgr)
    if image_was_color:
        print("[preprocess] Color image detected -> applying local-contrast binarization")
        image_bgr = color_to_binary_inscription(image_bgr)
        pil = Image.fromarray(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
        buf = io.BytesIO()
        pil.save(buf, format="JPEG")
        binary_image_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    if image_was_inverted or image_was_color:
        cleaned_bgr = image_bgr
    else:
        cleaned_bgr = remove_background_noise(image_bgr, min_dot_area=60)

    return cleaned_bgr, image_was_inverted, image_was_color, binary_image_b64


# ============================================================================
# MODEL LOADING
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Model accuracy reference (used for ensemble weighting) ────────────────────
# Ensemble uses EXCESS-ABOVE-90% weighting:  weight = accuracy - 90.0
# This amplifies real differences between high-accuracy models so that
# tiny gaps (e.g. 99.91 vs 99.73) produce a clear weight ordering.
#
#   EfficientNetB0: 99.91 - 90 = 9.91  → ~40.5%  ← highest priority
#   ResNet50      : 99.73 - 90 = 9.73  → ~39.8%  ← second
#   MobileNetV2   : 94.82 - 90 = 4.82  → ~19.7%  ← third
MODEL_ACCURACIES = {
    'EfficientNetB0': 99.91,
    'ResNet50':       99.73,
    'MobileNetV2':    94.82,
}

MODEL_PATHS = {
    'ResNet50':       os.path.join(BASE_DIR, 'brahmi_model_resnet50_new',       'resnet50_brahmi.pth'),
    'EfficientNetB0': os.path.join(BASE_DIR, 'brahmi_model_efficientnetb0_new', 'model_weights.pth'),
    'MobileNetV2':    os.path.join(BASE_DIR, 'brahmi_model_mobilenet_v2',       'best_model.keras'),
}

CONFIG_PATHS = {
    'ResNet50':       os.path.join(BASE_DIR, 'brahmi_model_resnet50_new',       'class_names.json'),
    'EfficientNetB0': os.path.join(BASE_DIR, 'brahmi_model_efficientnetb0_new', 'model_config_efficientnetb0_new.json'),
    'MobileNetV2':    os.path.join(BASE_DIR, 'brahmi_model_mobilenet_v2',       'brahmi_mobilenet_v2_config.json'),
}

models           = {}
configs          = {}
translit_mapping = {}

for model_name, config_path in CONFIG_PATHS.items():
    try:
        print(f"Loading configuration for {model_name} from {config_path}...")
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        if isinstance(config_data, list):
            configs[model_name] = {
                'class_names': config_data,
                'num_classes': len(config_data),
                'image_height': 224,
                'image_width':  224
            }
        else:
            configs[model_name] = config_data

        cfg         = configs[model_name]
        class_names = cfg.get('class_names', [])

        if 'idx2label' in cfg:
            idx2label   = cfg['idx2label']
            max_id      = max(int(k) for k in idx2label.keys())
            class_names = [idx2label.get(str(i), '<UNK>') for i in range(max_id + 1)]
            cfg['class_names'] = class_names
        elif 'idx2char' in cfg:
            idx2char    = cfg['idx2char']
            max_id      = max(int(k) for k in idx2char.keys())
            class_names = [idx2char.get(str(i), '<UNK>') for i in range(max_id + 1)]
            cfg['class_names'] = class_names
        elif 'id2char' in cfg:
            id2char     = cfg['id2char']
            max_id      = max(int(k) for k in id2char.keys())
            class_names = [id2char.get(str(i), '<UNK>') for i in range(max_id + 1)]
            cfg['class_names'] = class_names

        if not cfg.get('num_classes'):
            cfg['num_classes'] = len(class_names)

        print(f"OK Configuration loaded for {model_name}: {len(class_names)} classes")

    except FileNotFoundError:
        print(f"ERROR: Configuration file not found at {config_path}.")
    except Exception as e:
        print(f"ERROR loading configuration for {model_name}: {e}")

print("Loading Brahmi OCR models...")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize GAN Restorer
gan_restorer = None
try:
    gan_path = os.path.join(BASE_DIR, 'Brahmi_Model_Export', 'epoch_0250.pth')
    if os.path.exists(gan_path):
        gan_restorer = GANRestorer(gan_path, device=device)
    else:
        print(f"WARNING: GAN model not found at {gan_path}")
except Exception as e:
    print(f"ERROR loading GAN Restorer: {e}")

# ── MobileNetV2 architecture (mirrors brahmi_ocr.py) for .keras HDF5 loading ──
class _MobileNetV2Classifier(nn.Module):
    """
    Minimal MobileNetV2 classifier that mirrors BrahmiOCRModel in brahmi_ocr.py.
    Used to load the .keras (HDF5) checkpoint produced by the training script.
    """
    def __init__(self, num_classes: int):
        super().__init__()
        import torchvision.models as tv_models
        base      = tv_models.mobilenet_v2(weights=None)
        self.cnn  = base.features
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.head = nn.Sequential(
            nn.Linear(1280, 256),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        return self.head(self.pool(self.cnn(x)).flatten(1))


def _load_keras_hdf5(model: nn.Module, path: str):
    """Load weights from .keras HDF5 file produced by brahmi_ocr.py save_keras_format()."""
    if h5py is None:
        raise ImportError("h5py is required to load .keras weights. Run: pip install h5py")
    with h5py.File(str(path), 'r') as f:
        state = {}
        for name, ds in f['model_weights'].items():
            state[name] = torch.tensor(np.array(ds))
    model.load_state_dict(state, strict=True)


for model_name, model_path in MODEL_PATHS.items():
    try:
        print(f"Loading {model_name} from {model_path}...")
        if model_path.endswith('.onnx'):
            models[model_name] = ort.InferenceSession(model_path)
            print(f"OK {model_name} ONNX session loaded successfully!")
        elif model_path.endswith('.keras'):
            # MobileNetV2 — load from HDF5 .keras checkpoint
            num_classes = configs.get(model_name, {}).get('num_classes', 214)
            pt_model    = _MobileNetV2Classifier(num_classes=num_classes)
            _load_keras_hdf5(pt_model, model_path)
            pt_model.to(device)
            pt_model.eval()
            models[model_name] = pt_model
            print(f"OK {model_name} loaded from .keras (HDF5) on {device}!  "
                  f"[Best val accuracy: {MODEL_ACCURACIES.get(model_name, '?')}%]")
        elif model_path.endswith('.pth'):
            checkpoint  = torch.load(model_path, map_location=device, weights_only=False)
            num_classes = checkpoint.get("num_classes") or configs.get(model_name, {}).get("num_classes", 214)

            if "resnet50" in model_path.lower():
                from brahmi_model_resnet50_new.model import ResNet50Classifier
                pt_model = ResNet50Classifier(num_classes=num_classes)
            else:
                from brahmi_model_efficientnetb0_new.model import EfficientNetB0Classifier
                pt_model = EfficientNetB0Classifier(num_classes=num_classes)

            pt_model.load_state_dict(checkpoint["model_state_dict"], strict=False)
            pt_model.to(device)
            pt_model.eval()

            models[model_name] = pt_model
            print(f"OK {model_name} PyTorch model loaded successfully on {device}!")

    except FileNotFoundError:
        print(f"ERROR: Model file not found at {model_path}.")
    except Exception as e:
        print(f"ERROR loading {model_name}: {e}")
        import traceback
        traceback.print_exc()

try:
    mapping_path = os.path.join(BASE_DIR, 'transliteration_mapping.json')
    if os.path.exists(mapping_path):
        with open(mapping_path, 'r', encoding='utf-8') as f:
            translit_mapping = json.load(f)
        print(f"OK Transliteration mapping loaded: {len(translit_mapping)} entries")
    else:
        print("WARNING: transliteration_mapping.json not found. Run generate_mapping.py first.")
except Exception as e:
    print(f"ERROR loading transliteration mapping: {e}")


# ============================================================================
# FLASK API
# ============================================================================

app = Flask(__name__)
CORS(app)


def apply_gan_single_pass(composite_img, sorted_boxes):
    """
    Single-pass GAN restore: run each box through the GAN once if it needs
    restoration, then clean and paste back. No re-segmentation, no looping.

    Args:
        composite_img — PIL RGB image (full inscription)
        sorted_boxes  — list of (x, y, w, h)
    Returns:
        new PIL RGB image with restored crops pasted in
    """
    new_composite = composite_img.copy()
    for (x, y, w, h) in sorted_boxes:
        crop = composite_img.crop((x, y, x + w, y + h))
        if gan_restorer and gan_restorer.needs_restoration(crop):
            restored_crop = gan_restorer.restore(crop)
        else:
            restored_crop = crop.convert('RGB')
        restored_cv  = np.array(restored_crop)[:, :, ::-1].copy()
        cleaned_cv   = clean_image_noise(restored_cv, min_dot_area=10)
        cleaned_pil  = Image.fromarray(cleaned_cv[:, :, ::-1])
        new_composite.paste(cleaned_pil.resize((w, h), Image.Resampling.LANCZOS), (x, y))
    return new_composite


def resize_with_padding(img, target_width, target_height, padding_percent=0.15):
    """Resizes image to target dimensions using padding-to-square method."""
    original_w, original_h = img.size
    max_dim    = max(original_w, original_h)
    padding    = int(max_dim * padding_percent)
    new_dim    = max_dim + 2 * padding
    square_img = Image.new("RGB", (new_dim, new_dim), (255, 255, 255))
    square_img.paste(img, ((new_dim - original_w) // 2, (new_dim - original_h) // 2))
    return square_img.resize((target_width, target_height), Image.Resampling.LANCZOS)


def roman_to_devanagari(label):
    val = translit_mapping.get(label, label)
    return val.get('devanagari', label) if isinstance(val, dict) else val


def roman_to_brahmi(label):
    val = translit_mapping.get(label, label)
    return val.get('brahmi', label) if isinstance(val, dict) else val


# ============================================================================
# ROUTE: /predict
# ============================================================================

@app.route('/predict', methods=['POST'])
def predict():
    """Predict Brahmi character from uploaded image."""
    try:
        # --- 1. Load image ---
        if 'image' in request.files:
            img = Image.open(request.files['image'].stream)
        elif request.json and 'image' in request.json:
            img = Image.open(io.BytesIO(base64.b64decode(request.json['image'])))
        else:
            return jsonify({'success': False, 'error': 'No image provided.'}), 400

        if img.mode != 'RGB':
            img = img.convert('RGB')

        model_name = (request.form.get('model')
                      or (request.json and request.json.get('model'))
                      or 'ResNet50')

        # --- 2. Preprocess ---
        image_bgr = np.array(img)[:, :, ::-1].copy()
        cleaned_bgr, image_was_inverted, image_was_color, binary_image_b64 = \
            preprocess_image(image_bgr)

        original_pil = Image.fromarray(cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB))

        # --- 3. Segmentation ---
        custom_boxes = (request.json and request.json.get('boxes')) \
                       or request.form.get('boxes')

        if custom_boxes:
            sorted_boxes = (json.loads(custom_boxes)
                            if isinstance(custom_boxes, str) else custom_boxes)
            sorted_boxes = sort_boxes(sorted_boxes)
            print(f"[predict] Using {len(sorted_boxes)} custom/manual boxes (re-sorted).")
        else:
            detection_image = clean_image_noise(cleaned_bgr, min_dot_area=50)
            boxes, _        = detect_characters(detection_image)
            if len(boxes) <= 1:
                sorted_boxes = [[0, 0, cleaned_bgr.shape[1], cleaned_bgr.shape[0]]]
            else:
                sorted_boxes = sort_boxes(boxes)
            print(f"[predict] Auto-detected {len(sorted_boxes)} boxes.")

        # --- 4. Single-pass GAN restore ---
        composite_img = apply_gan_single_pass(original_pil, sorted_boxes)

        # --- 5. Crop characters from restored image ---
        pil_crops = [composite_img.crop((x, y, x + w, y + h)).convert('RGB')
                     for (x, y, w, h) in sorted_boxes]

        # Encode restored image for frontend
        buf = io.BytesIO()
        composite_img.save(buf, format="JPEG")
        restored_image_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        # --- 6. Model inference ---
        IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        IMAGENET_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

        def get_model_preds(model_key, crop_images):
            model_obj  = models[model_key]
            
            # ALL three PyTorch models (ResNet, EfficientNet, MobileNet) 
            # were trained with transforms.Resize((224, 224)) which SQUEEZES the image.
            # They also all use ImageNet normalisation.
            h = 224
            w = 224
            model_path = MODEL_PATHS.get(model_key, "")
            is_onnx    = model_path.endswith('.onnx')

            batch_arr = []
            for c_img in crop_images:
                # MATCH PyTorch Training: direct resize (squeeze), NOT padded!
                c_resized = c_img.resize((w, h), Image.Resampling.BILINEAR)
                
                c_arr = np.array(c_resized, dtype=np.float32) / 255.0
                c_arr = (c_arr - IMAGENET_MEAN) / IMAGENET_STD
                
                if is_onnx:
                    c_arr = np.transpose(c_arr, (2, 0, 1))
                batch_arr.append(c_arr)

            batch_input = np.array(batch_arr)

            if is_onnx:
                logits = model_obj.run(None, {'image': batch_input})[0]
                return logits / 0.2   # temperature scaling T=0.2
            else:
                # PyTorch models (.pth and .keras) — input is NCHW
                batch_tensor = torch.from_numpy(batch_input)
                if batch_tensor.ndim == 4 and batch_tensor.shape[-1] == 3:
                    # HWC → CHW if needed (shouldn't happen now but guard)
                    batch_tensor = batch_tensor.permute(0, 3, 1, 2)
                batch_tensor = batch_tensor.to(device)
                with torch.no_grad():
                    logits = model_obj(batch_tensor)
                return logits.cpu().numpy()

        label_model = (model_name if model_name in configs
                       else (list(configs.keys())[0] if configs else None))
        if not label_model:
            return jsonify({'success': False, 'error': 'No model configurations loaded.'}), 500
        class_names = configs[label_model].get('class_names', [])

        if model_name == 'Ensemble':
            if not models:
                return jsonify({'success': False, 'error': 'No models for Ensemble.'}), 500

            num_crops       = len(pil_crops)
            num_classes     = len(class_names)
            all_model_probs = []   # list of (weight, probs_array)
            ensemble_errors = {}

            print(f"[predict] Ensemble (accuracy-weighted): {num_crops} chars × {len(models)} models")

            for m_key in models.keys():
                try:
                    preds = get_model_preds(m_key, pil_crops)
                    probs = torch.nn.functional.softmax(
                        torch.from_numpy(preds), dim=-1).numpy()
                    if probs.shape[1] == num_classes:
                        # Excess-above-90% weight: amplifies real accuracy gaps
                        # so 99.91 vs 99.73 produce a clearly different share.
                        raw_acc = MODEL_ACCURACIES.get(m_key, 85.0)
                        weight  = max(0.1, raw_acc - 90.0)
                        all_model_probs.append((weight, probs))
                        print(f"  → {m_key}: acc={raw_acc:.2f}%  excess_weight={weight:.2f}")
                    else:
                        msg = (f"Shape mismatch for {m_key}: "
                               f"{probs.shape[1]} vs {num_classes}")
                        print(msg)
                        ensemble_errors[m_key] = msg
                except Exception as e:
                    msg = str(e)
                    print(f"Error in Ensemble for {m_key}: {msg}")
                    ensemble_errors[m_key] = msg

            if not all_model_probs:
                return jsonify({'success': False,
                                'error': 'Ensemble failed completely.',
                                'details': ensemble_errors}), 500

            # ── Excess-above-90% weighted average ────────────────────────────
            # weight = accuracy - 90.0  (so only the "hard-won" accuracy counts)
            # Final shares (approx):  EfficientNetB0 ~40.5% | ResNet50 ~39.8% | MobileNetV2 ~19.7%
            # EfficientNet clearly leads, ResNet50 second, MobileNetV2 third.
            total_weight = sum(w for w, _ in all_model_probs)
            final_probabilities = np.zeros((num_crops, num_classes))
            for weight, probs in all_model_probs:
                final_probabilities += (weight / total_weight) * probs

        elif model_name in models:
            preds               = get_model_preds(model_name, pil_crops)
            final_probabilities = torch.nn.functional.softmax(
                torch.from_numpy(preds), dim=-1).numpy()
        else:
            return jsonify({'success': False,
                            'error': f"Model '{model_name}' not found."}), 400

        # --- 7. Decode results ---
        # Low-confidence characters are flagged and their bounding boxes will
        # be highlighted red in the UI so the user can reshape them.
        # They are NOT added to the displayed text — only high-confidence
        # characters appear in the transliteration output.
        results              = []
        full_text_latin      = []
        full_text_devanagari = []
        full_text_brahmi     = []
        CONF_THRESHOLD       = 20.0

        for i, probs in enumerate(final_probabilities):
            top_idx = np.argmax(probs)
            conf    = float(probs[top_idx] * 100)

            if conf < CONF_THRESHOLD:
                print(f"[predict] Low-confidence box {i} ({conf:.2f}%) → '?' placeholder")
                full_text_latin.append('?')
                full_text_devanagari.append('?')
                full_text_brahmi.append('?')
                results.append({
                    'character':            '?',
                    'character_devanagari': '?',
                    'character_brahmi':     '?',
                    'confidence':           conf,
                    'box':                  sorted_boxes[i],
                    'low_confidence':       True
                })
                continue

            char_name_latin      = class_names[top_idx] if top_idx < len(class_names) else 'Unknown'
            char_name_devanagari = roman_to_devanagari(char_name_latin)
            char_name_brahmi     = roman_to_brahmi(char_name_latin)

            full_text_latin.append(char_name_latin)
            full_text_devanagari.append(char_name_devanagari)
            full_text_brahmi.append(char_name_brahmi)

            results.append({
                'character':            char_name_latin,
                'character_devanagari': char_name_devanagari,
                'character_brahmi':     char_name_brahmi,
                'confidence':           conf,
                'box':                  sorted_boxes[i],
                'low_confidence':       False
            })

        high_conf          = [r for r in results if not r.get('low_confidence')]
        low_conf           = [r for r in results if r.get('low_confidence')]
        top_conf           = (sum(r['confidence'] for r in high_conf) / len(high_conf)
                              if high_conf else 0.0)
        all_above_threshold = len(low_conf) == 0

        response = {
            'success':                   True,
            'top_prediction':            " ".join(full_text_latin),
            'top_prediction_devanagari': " ".join(full_text_devanagari),
            'top_prediction_brahmi':     "".join(str(x) for x in full_text_brahmi if x),
            'top_confidence':            top_conf,
            'predictions':               results,
            'low_confidence_count':      len(low_conf),
            'all_above_threshold':       all_above_threshold,
            'conf_threshold':            CONF_THRESHOLD,
            'model_used':                model_name,
            'restored_image_b64':        restored_image_b64,
            'image_was_color':           image_was_color,
            'image_was_inverted':        image_was_inverted
        }
        if binary_image_b64:
            response['binary_image_b64'] = binary_image_b64

        return jsonify(response)

    except Exception as e:
        print(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f"Internal Error: {str(e)}"}), 500


# ============================================================================
# ROUTE: /process
# ============================================================================

@app.route('/process', methods=['POST'])
def process():
    """Image preprocessing, GAN restore (single pass), and segmentation."""
    try:
        if 'image' in request.files:
            img = Image.open(request.files['image'].stream)
        elif request.json and 'image' in request.json:
            img = Image.open(io.BytesIO(base64.b64decode(request.json['image'])))
        else:
            return jsonify({'success': False, 'error': 'No image provided.'}), 400

        if img.mode != 'RGB':
            img = img.convert('RGB')

        image_bgr = np.array(img)[:, :, ::-1].copy()
        cleaned_bgr, image_was_inverted, image_was_color, binary_image_b64 = \
            preprocess_image(image_bgr)

        source_pil = Image.fromarray(cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB))

        # Encode cleaned original for frontend
        buf_orig = io.BytesIO()
        source_pil.save(buf_orig, format="JPEG")
        original_image_b64 = base64.b64encode(buf_orig.getvalue()).decode('utf-8')

        # Segmentation
        custom_boxes_data = ((request.json and request.json.get('boxes'))
                             or request.form.get('boxes'))

        if custom_boxes_data:
            sorted_boxes = (json.loads(custom_boxes_data)
                            if isinstance(custom_boxes_data, str)
                            else custom_boxes_data)
            sorted_boxes = sort_boxes(sorted_boxes)
            print(f"[process] Using {len(sorted_boxes)} custom/manual boxes (re-sorted).")
        else:
            detection_image = clean_image_noise(cleaned_bgr, min_dot_area=50)
            boxes, _        = detect_characters(detection_image)
            sorted_boxes    = sort_boxes(boxes) if boxes else []
            print(f"[process] Auto-detected {len(sorted_boxes)} boxes.")

        # Single-pass GAN restore
        composite_img = apply_gan_single_pass(source_pil, sorted_boxes)

        # Encode restored image for frontend
        buf_out = io.BytesIO()
        composite_img.save(buf_out, format="JPEG")
        restored_image_b64 = base64.b64encode(buf_out.getvalue()).decode('utf-8')

        response = {
            'success':            True,
            'restored_image_b64': restored_image_b64,
            'original_image_b64': original_image_b64,
            'boxes':              sorted_boxes,
            'image_was_color':    image_was_color,
            'image_was_inverted': image_was_inverted
        }
        if binary_image_b64:
            response['binary_image_b64'] = binary_image_b64

        return jsonify(response)

    except Exception as e:
        print(f"Processing error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ROUTE: /segment
# ============================================================================

@app.route('/segment', methods=['POST', 'OPTIONS'])
def segment_only():
    """Segmentation only — no GAN, no prediction. Returns boxes for review."""
    if request.method == 'OPTIONS':
        return '', 200
    try:
        if 'image' in request.files:
            img = Image.open(request.files['image'].stream)
        elif request.json and 'image' in request.json:
            img = Image.open(io.BytesIO(base64.b64decode(request.json['image'])))
        else:
            return jsonify({'success': False, 'error': 'No image provided.'}), 400

        if img.mode != 'RGB':
            img = img.convert('RGB')

        image_bgr = np.array(img)[:, :, ::-1].copy()
        cleaned_bgr, image_was_inverted, image_was_color, binary_image_b64 = \
            preprocess_image(image_bgr)

        detection_image = clean_image_noise(cleaned_bgr, min_dot_area=50)
        boxes, _        = detect_characters(detection_image)
        sorted_boxes    = sort_boxes(boxes) if boxes else []
        print(f"[segment] Found {len(sorted_boxes)} boxes.")

        cleaned_pil = Image.fromarray(cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB))
        buf = io.BytesIO()
        cleaned_pil.save(buf, format="JPEG")
        original_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        response = {
            'success':            True,
            'original_image_b64': original_b64,
            'boxes':              sorted_boxes,
            'image_was_color':    image_was_color,
            'image_was_inverted': image_was_inverted
        }
        if binary_image_b64:
            response['binary_image_b64'] = binary_image_b64

        return jsonify(response)

    except Exception as e:
        print(f"Segment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500




# ============================================================================
# ROUTE: /episam_binarize
# ============================================================================

@app.route('/episam_binarize', methods=['POST'])
def episam_binarize_endpoint():
    """
    Official EpiSAM / Shilalekhya Inscription Binarization (Attention U-Net).
    Paper: "Unveiling Text in Challenging Stone Inscriptions: A Character-Context-Aware Patching Strategy for Binarization"
    """
    try:
        data = request.get_json(silent=True) or {}
        image_b64 = data.get('image')

        if not image_b64 and 'file' in request.files:
            file = request.files['file']
            img_bytes = file.read()
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif image_b64:
            if ',' in image_b64:
                image_b64 = image_b64.split(',', 1)[1]
            img_bytes = base64.b64decode(image_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            return jsonify({'success': False, 'error': 'No image provided'}), 400

        if img is None:
            return jsonify({'success': False, 'error': 'Failed to decode image'}), 400

        threshold = float(data.get('threshold', 0.40)) if 'threshold' in data else 0.40
        fast_mode = bool(data.get('fast_mode', True))

        binarizer = get_episam_binarizer()
        mask, clean_ocr = binarizer.binarize(img, threshold=threshold, fast_single_scale=fast_mode)

        # Encode clean OCR image
        pil_clean = Image.fromarray(cv2.cvtColor(clean_ocr, cv2.COLOR_BGR2RGB))
        buf = io.BytesIO()
        pil_clean.save(buf, format="JPEG")
        clean_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'binarized_image_b64': clean_b64,
            'threshold_used': threshold,
            'ink_coverage_pct': round(100.0 * float(np.sum(mask == 255)) / mask.size, 2)
        })

    except Exception as e:
        print(f"EpiSAM binarization error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ROUTE: /health  &  /
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status':         'healthy',
        'models_loaded':  list(models.keys()),
        'configs_loaded': list(configs.keys())
    })


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service':   'Brahmi OCR & Inscription API',
        'version':   '1.6',
        'model_accuracies': MODEL_ACCURACIES,
        'endpoints': {
            '/health':             'GET  - Health check',
            '/predict':            'POST - Predict characters from image',
            '/process':            'POST - Segment + single-pass GAN restore',
            '/segment':            'POST - Segment only, returns boxes for review',
            '/episam_binarize':    'POST - Official EpiSAM / Shilalekhya Attention U-Net stone binarization'
        }
    })


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Brahmi OCR Backend Server Starting...")
    print("=" * 60)
    print(f"Server running at: http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)