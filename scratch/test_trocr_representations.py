import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("Brahmi-OCR-main/backend").resolve()))

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from preprocessing import ShiloraStonePreprocessor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

img_path = r"C:\Users\TEJAS M G\.gemini\antigravity-ide\brain\7d098130-659d-4128-b0cf-2785df3a7db0\.user_uploaded\media_1791384734075.jpg"
img_bgr = cv2.imread(img_path)
h, w = img_bgr.shape[:2]

preproc_res = ShiloraStonePreprocessor().process(img_bgr)
gray_natural = preproc_res.final_natural # enhanced grayscale

# Load TrOCR
trocr_dir = "models/trocr/best_model"
processor = TrOCRProcessor.from_pretrained(trocr_dir)
model = VisionEncoderDecoderModel.from_pretrained(trocr_dir)
model.eval()

def transcribe(img):
    if len(img.shape) == 2:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    else:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    pixel_values = processor(pil_img, return_tensors="pt").pixel_values
    with torch.no_grad():
        generated_ids = model.generate(
            pixel_values,
            max_length=64,
            num_beams=3,
            decoder_start_token_id=processor.tokenizer.cls_token_id,
            eos_token_id=processor.tokenizer.sep_token_id,
            pad_token_id=processor.tokenizer.pad_token_id
        )
    return processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

# Let's take line 1: y from 25 to 65, x from 30 to 730 (the first clearly inscribed line at top)
y1, y2 = 25, 68
x1, x2 = 30, 730

# 1. Raw grayscale crop
raw_crop = cv2.cvtColor(img_bgr[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)

# 2. Enhanced grayscale crop
enh_crop = gray_natural[y1:y2, x1:x2]

# 3. Previous broken binary crop (white bg, black dots)
clean_ocr_old = cv2.imread("outputs/pipeline_results/user_uploaded_slab/line_001.png")

# 4. Stroke-preserving adaptive binary:
# Invert so black strokes on white bg or vice versa
# TrOCR was trained on black text on white background and natural stone crops.
th_crop = cv2.adaptiveThreshold(enh_crop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, 5)

print("Transcription on Line 1:")
if clean_ocr_old is not None:
    print("  [Previous Broken Binary]:", transcribe(clean_ocr_old))
print("  [Raw Grayscale]:", transcribe(raw_crop))
print("  [Enhanced Grayscale]:", transcribe(enh_crop))
print("  [Adaptive Threshold]:", transcribe(th_crop))

# Let's also test on Line 2: y from 68 to 110
y1, y2 = 68, 110
raw_crop2 = cv2.cvtColor(img_bgr[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
enh_crop2 = gray_natural[y1:y2, x1:x2]
th_crop2 = cv2.adaptiveThreshold(enh_crop2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, 5)

print("\nTranscription on Line 2:")
print("  [Raw Grayscale]:", transcribe(raw_crop2))
print("  [Enhanced Grayscale]:", transcribe(enh_crop2))
print("  [Adaptive Threshold]:", transcribe(th_crop2))
