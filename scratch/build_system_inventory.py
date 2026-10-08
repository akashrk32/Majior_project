import os
import sys
import csv
import json
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parent.parent

def compute_sha256(filepath):
    try:
        p = Path(filepath)
        if not p.exists() or p.is_dir():
            return "N/A_DIRECTORY_OR_MISSING"
        # For large files (> 500MB), skip or hash in chunks
        h = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "ERROR_COMPUTING"

artifacts = [
    # 1. Datasets & Raw Images
    {
        "path": "kannada_stones/",
        "type": "DIRECTORY / IMAGE_DATASET",
        "purpose": "Primary repository of 187 Kannada stone inscription images (39 SHILORA + 148 Mythic Society)",
        "source": "Mythic Society 3D Inscriptions Conservation Project & SHILORA Field Collection",
        "training_inference_usage": "Raw inputs for Preprocessing, Binarization, and Segmentation",
        "dataset_provenance": "Ancient & Medieval Kannada stone epigraphs (Karnataka)",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "data/raw/",
        "type": "DIRECTORY / RAW_IMAGES",
        "purpose": "Local storage of the 39 target SHILORA inscription images",
        "source": "SHILORA Stone Collection",
        "training_inference_usage": "Test and diagnostic inputs",
        "dataset_provenance": "Kannada stone inscriptions",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "data/preprocessed/",
        "type": "DIRECTORY / PREPROCESSED_IMAGES",
        "purpose": "Relief-amplified, illumination-normalized 1:1 scale images of 39 stones",
        "source": "ShiloraStonePreprocessor (Stage 1)",
        "training_inference_usage": "Input to ShilaLekhya binarizer",
        "dataset_provenance": "Processed from data/raw/ and kannada_stones/",
        "is_ground_truth": False,
        "is_prediction": True,
        "is_hardcoded": False
    },
    {
        "path": "data/binarized/",
        "type": "DIRECTORY / BINARIZED_MASKS",
        "purpose": "Attention U-Net neural binarization masks for all 187 stone inscriptions",
        "source": "ShilaLekhya AttentionUNet (Stage 2)",
        "training_inference_usage": "Input to Quality Gate and EpiSAM segmentation",
        "dataset_provenance": "Generated dynamically by AttentionUNet",
        "is_ground_truth": False,
        "is_prediction": True,
        "is_hardcoded": False
    },
    {
        "path": "data/episam/ground_truth/",
        "type": "DIRECTORY / GROUND_TRUTH_ANNOTATIONS",
        "purpose": "Ground-truth character polygons, line masks, and verified centroid annotations",
        "source": "EpiSAM Official Research Dataset (IIIT Hyderabad)",
        "training_inference_usage": "Reference evaluation benchmark and line crop creation",
        "dataset_provenance": "Mythic Society 3D scanned stone inscriptions",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "data/episam/predictions/",
        "type": "DIRECTORY / PREDICTED_MASKS",
        "purpose": "Dynamically generated EpiSAM character segmentation masks across 183 stones",
        "source": "EpiSAM ViT-B Segmentation Model",
        "training_inference_usage": "Model predictions storage",
        "dataset_provenance": "Derived from data/binarized/",
        "is_ground_truth": False,
        "is_prediction": True,
        "is_hardcoded": False
    },
    {
        "path": "data/episam/lines/",
        "type": "DIRECTORY / RECONSTRUCTED_LINES",
        "purpose": "Reconstructed reading-order text line crops (2,450 crops across 183 stones)",
        "source": "EpiSAM Line Clustering Algorithm",
        "training_inference_usage": "Input to TrOCR line recognition",
        "dataset_provenance": "Reconstructed lines from segmented characters",
        "is_ground_truth": False,
        "is_prediction": True,
        "is_hardcoded": False
    },
    {
        "path": "data/trocr/metadata.csv",
        "type": "METADATA / CSV",
        "purpose": "Paired image-text ground truth dataset for TrOCR (513 lines across 65 unique stones)",
        "source": "Mythic Society Epigraphical Readings aligned with Ground Truth Line Crops",
        "training_inference_usage": "Training (368), Validation (50), Test (95)",
        "dataset_provenance": "Epigraphia Carnatica & Mythic Society Volumes",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "data/trocr/train/",
        "type": "DIRECTORY / LINE_CROPS",
        "purpose": "368 verified line crop training images from 45 unique stones",
        "source": "data/episam/ground_truth/line_crops/",
        "training_inference_usage": "TrOCR fine-tuning training set",
        "dataset_provenance": "Mythic Society Kannada stone inscriptions",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "data/trocr/validation/",
        "type": "DIRECTORY / LINE_CROPS",
        "purpose": "50 verified line crop validation images from 9 unique stones",
        "source": "data/episam/ground_truth/line_crops/",
        "training_inference_usage": "TrOCR validation set",
        "dataset_provenance": "Mythic Society Kannada stone inscriptions",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "data/trocr/test/",
        "type": "DIRECTORY / LINE_CROPS",
        "purpose": "95 verified line crop test images from 11 unique stones (Zero stone leakage)",
        "source": "data/episam/ground_truth/line_crops/",
        "training_inference_usage": "TrOCR test benchmark",
        "dataset_provenance": "Mythic Society Kannada stone inscriptions",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },

    # 2. Model Checkpoints
    {
        "path": "models/shilalekhya/binarizer.pth",
        "type": "MODEL_CHECKPOINT / PYTORCH",
        "purpose": "Attention U-Net neural binarizer weights for carved stone inscriptions",
        "source": "IIIT Hyderabad Shilalekhya / EpiSAM Binarization Model",
        "training_inference_usage": "Active runtime inference in ShiloraProductionPipeline",
        "dataset_provenance": "Mythic Society Stone Inscriptions Dataset",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "models/episam/episam.pth",
        "type": "MODEL_CHECKPOINT / PYTORCH",
        "purpose": "EpiSAM ViT-B prompt-guided character segmentation model weights",
        "source": "Official EpiSAM Release (IIIT Hyderabad / IHDIA)",
        "training_inference_usage": "Active runtime inference in ShiloraProductionPipeline",
        "dataset_provenance": "EpiSAM Epigraphical Dataset",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "models/trocr/best_model/model.safetensors",
        "type": "MODEL_CHECKPOINT / SAFETENSORS",
        "purpose": "Fine-tuned TrOCR VisionEncoderDecoder model for Kannada inscription lines",
        "source": "scripts/train_trocr.py native fine-tuning",
        "training_inference_usage": "Active runtime inference in ShiloraProductionPipeline",
        "dataset_provenance": "Trained on data/trocr/metadata.csv (train split: 368 lines)",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },

    # 3. Tokenizer & Configurations
    {
        "path": "models/trocr/best_model/tokenizer.json",
        "type": "TOKENIZER / JSON",
        "purpose": "RoBERTa byte-level BPE tokenizer mapping for Kannada text decoding",
        "source": "Hugging Face / microsoft/trocr-small-stage1 fine-tuned checkpoint",
        "training_inference_usage": "Token encoding during training and decoding during inference",
        "dataset_provenance": "Standard TrOCR vocabulary with byte-level Unicode preservation",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "models/trocr/best_model/config.json",
        "type": "CONFIGURATION / JSON",
        "purpose": "VisionEncoderDecoderModel architecture configuration",
        "source": "TrOCR architecture spec",
        "training_inference_usage": "Model loading",
        "dataset_provenance": "N/A",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },

    # 4. Translation Resources
    {
        "path": "data/translation/epigraphical_lexicon.json",
        "type": "EXTERNAL_LEXICAL_RESOURCE / JSON",
        "purpose": "Epigraphical vocabulary definitions for Kadamba, Ganga, and Vijayanagara epigraphs",
        "source": "Epigraphia Carnatica Vol IX, Mythic Society Conservation, Halmidi Inscription (ASI)",
        "training_inference_usage": "Deterministic lookup during translation (Stage 7/8)",
        "dataset_provenance": "Verified historical Karnataka epigraphy corpora",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "data/translation/historical_morphology.json",
        "type": "LINGUISTIC_RULE_TABLE / JSON",
        "purpose": "Old Kannada case endings (locative -dolu, verbal -dan, etc.) for grammatical analysis",
        "source": "Kittel Kannada Grammar & Classical Halegannada epigraphical morphology",
        "training_inference_usage": "Deterministic morphological decomposition during translation",
        "dataset_provenance": "Halegannada grammatical corpus",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "data/translation/normalization_rules.json",
        "type": "ORTHOGRAPHIC_RULES / JSON",
        "purpose": "Archaic character normalization rules (ಱ -> ರ, ೞ -> ಳ, repha gemination)",
        "source": "Historical Kannada Epigraphical Orthography",
        "training_inference_usage": "Normalized matching in ShiloraTranslationEngine",
        "dataset_provenance": "Historical phonological shift rules",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },

    # 5. Core Scripts & Orchestrators
    {
        "path": "scripts/shilora_orchestrator.py",
        "type": "PYTHON_SCRIPT / ORCHESTRATOR",
        "purpose": "Unified end-to-end production orchestrator and analyze_inscription API entrypoint",
        "source": "SHILORA Core Development",
        "training_inference_usage": "Main runtime inference engine",
        "dataset_provenance": "N/A",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "scripts/translation_engine.py",
        "type": "PYTHON_SCRIPT / LINGUISTIC_ENGINE",
        "purpose": "Deterministic linguistic translation and epigraphical glossing engine",
        "source": "SHILORA Core Development",
        "training_inference_usage": "Runtime translation without hallucination",
        "dataset_provenance": "N/A",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "scripts/train_trocr.py",
        "type": "PYTHON_SCRIPT / TRAINING",
        "purpose": "Native PyTorch fine-tuning script for TrOCR on stone-partitioned Kannada lines",
        "source": "SHILORA Core Development",
        "training_inference_usage": "Model training pipeline",
        "dataset_provenance": "N/A",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "preprocessing/adaptive_preprocessor.py",
        "type": "PYTHON_SCRIPT / PREPROCESSING",
        "purpose": "Adaptive relief amplification, illumination flattening, and CLAHE contrast enhancement",
        "source": "SHILORA Core Development",
        "training_inference_usage": "Stage 1 preprocessing",
        "dataset_provenance": "N/A",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "Brahmi-OCR-main/backend/app.py",
        "type": "PYTHON_SCRIPT / API_SERVER",
        "purpose": "Flask REST API serving /api/shilora/analyze and legacy endpoints",
        "source": "SHILORA Backend",
        "training_inference_usage": "HTTP API interface for frontend uploads",
        "dataset_provenance": "N/A",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    }
]

# Calculate SHA256 where practical
for a in artifacts:
    p = root / a["path"]
    if p.is_file():
        a["sha256"] = compute_sha256(p)
    elif p.is_dir():
        a["sha256"] = "DIRECTORY"
    else:
        a["sha256"] = "NOT_FOUND"

out_json = root / "reports" / "final_system_audit.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump({"inventory": artifacts, "total_artifacts": len(artifacts)}, f, indent=2, ensure_ascii=False)

out_csv = root / "reports" / "final_system_audit.csv"
fieldnames = [
    "path", "type", "purpose", "source", "training_inference_usage",
    "dataset_provenance", "is_ground_truth", "is_prediction", "is_hardcoded", "sha256"
]
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(artifacts)

print(f"Generated {out_json} and {out_csv} with {len(artifacts)} audit entries.")
