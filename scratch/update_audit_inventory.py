import os
import sys
import json
import csv
import hashlib
from pathlib import Path

def compute_sha256(path):
    if os.path.isdir(path):
        return "DIRECTORY"
    if not os.path.exists(path):
        return "MISSING"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

artifacts = [
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
        "purpose": "Dynamically generated EpiSAM character segmentation masks across 182 stones",
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
        "purpose": "Reconstructed reading-order text line crops (2,450 crops across 182 stones)",
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
        "purpose": "Retrained TrOCR VisionEncoderDecoder model with repaired Kannada vocabulary",
        "source": "scripts/train_trocr.py native fine-tuning",
        "training_inference_usage": "Active runtime inference in ShiloraProductionPipeline",
        "dataset_provenance": "Trained on data/trocr/metadata.csv (train split: 368 lines)",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "models/trocr/repaired_tokenizer/",
        "type": "DIRECTORY / TOKENIZER",
        "purpose": "Repaired XLM-RoBERTa Tokenizer (64,126 tokens, 100% Kannada Unicode roundtrip)",
        "source": "scripts/audit_and_fix_tokenizer.py",
        "training_inference_usage": "Token encoding and decoding across TrOCR training & inference",
        "dataset_provenance": "Complete Kannada Unicode Block + Halegannada Archaic Signs",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "data/translation/epigraphical_lexicon.json",
        "type": "EXTERNAL_LEXICAL_RESOURCE / JSON",
        "purpose": "Epigraphical vocabulary definitions for Kadamba, Ganga, and Vijayanagara epigraphs",
        "source": "Epigraphia Carnatica Vol IX, Mythic Society Conservation, Halmidi Inscription (ASI)",
        "training_inference_usage": "Deterministic lookup during translation (Stage 8)",
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
        "purpose": "Native PyTorch fine-tuning script for TrOCR with repaired Kannada tokenizer",
        "source": "SHILORA Core Development",
        "training_inference_usage": "Model training pipeline",
        "dataset_provenance": "N/A",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "scripts/audit_and_fix_tokenizer.py",
        "type": "PYTHON_SCRIPT / TOKENIZER_AUDIT",
        "purpose": "Forensic audit and vocabulary expansion script for TrOCR Kannada tokenizer",
        "source": "SHILORA Core Development",
        "training_inference_usage": "Tokenizer diagnostic and vocabulary expansion",
        "dataset_provenance": "N/A",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "scripts/run_production_verification_suite.py",
        "type": "PYTHON_SCRIPT / TEST_SUITE",
        "purpose": "End-to-end test suite for uncached inference, API upload, and image perturbations",
        "source": "SHILORA Core Development",
        "training_inference_usage": "Production validation test runner",
        "dataset_provenance": "N/A",
        "is_ground_truth": False,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "reports/trocr_kannada_tokenizer_audit.json",
        "type": "AUDIT_REPORT / JSON",
        "purpose": "Exhaustive Unicode round-trip and unk-rate verification report (100% preservation)",
        "source": "scripts/audit_and_fix_tokenizer.py",
        "training_inference_usage": "Forensic audit record",
        "dataset_provenance": "Kannada Unicode Block + Archaic repertoire",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "reports/preprocessing_provenance.json",
        "type": "AUDIT_REPORT / JSON",
        "purpose": "Formal documentation of 39-stone SHILORA preprocessing vs 148 conserved stones",
        "source": "SHILORA Architecture Governance",
        "training_inference_usage": "Provenance record and production specification",
        "dataset_provenance": "SHILORA & Mythic Society collections",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    },
    {
        "path": "reports/SHILORA_FINAL_PRODUCTION_AUDIT.md",
        "type": "MASTER_REPORT / MARKDOWN",
        "purpose": "Comprehensive 15-section final forensic audit report and production decision",
        "source": "Antigravity Autonomous Epigraphical Forensics Engine",
        "training_inference_usage": "Official project audit record",
        "dataset_provenance": "Complete project audit",
        "is_ground_truth": True,
        "is_prediction": False,
        "is_hardcoded": False
    }
]

for item in artifacts:
    item["sha256"] = compute_sha256(item["path"])

with open("reports/final_system_audit.json", "w", encoding="utf-8") as f:
    json.dump({"inventory": artifacts, "total_artifacts": len(artifacts)}, f, indent=2, ensure_ascii=False)

with open("reports/final_system_audit.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "path", "type", "purpose", "source", "training_inference_usage",
        "dataset_provenance", "is_ground_truth", "is_prediction", "is_hardcoded", "sha256"
    ])
    writer.writeheader()
    writer.writerows(artifacts)

print("Updated reports/final_system_audit.json & reports/final_system_audit.csv successfully!")
