# SHILORA FORENSIC AUDIT & FINAL SYSTEM VALIDATION REPORT
**Project:** SHILORA — System for Historical Inscription Layout, Optical Recognition & Archaic Translation  
**Audit Date:** 2026-10-07  
**Auditor:** Antigravity Forensic Epigraphical AI Audit Team  
**Evaluation Standard:** Zero-Tolerance Hardcoding, Real Runtime Inference Verification, Strict Data Separation, Anti-Hallucination Epigraphical Validation  

---

## 1. OVERALL SYSTEM VERDICT

```
========================================================================================
FINAL PRODUCTION READINESS DECISION: NOT_PRODUCTION_READY
========================================================================================
Reasoning:
1. TrOCR OCR Model Quality: Test Character Error Rate (CER) is 1.0275 (102.75%), and 
   Exact Line Accuracy is 0.00% across 95 evaluated test lines from 11 unseen stones.
2. Tokenizer Architecture Defect: The underlying RoBERTa byte-level BPE tokenizer was never 
   expanded to include the full Kannada Unicode block (U+0C80–U+0CFF), mapping archaic Kannada 
   letters (ಱ U+0CB1, ೞ U+0CDE), Kannada numerals (೦-೯), and most consonants to <unk> (token ID 3).
3. Segmentation Limitations: 5 out of 187 stone inscriptions fail segmentation due to 
   over-saturated binarization masks or severe surface erosion.
========================================================================================
Integrity Statement:
- Zero Brahmi contamination in training, validation, testing, or active inference models.
- Zero hardcoded OCR strings, zero canned translations, and zero filename-based shortcuts.
- All pipeline stages execute genuine runtime neural and linguistic inference.
========================================================================================
```

---

## 2. DATASET INVENTORY & PROVENANCE

A complete, ground-truth filesystem recount was conducted across all image directories, ground truth sets, and line crops.

| Dataset / Artifact | Exact File Count | Provenance | Ground Truth Status | Prediction Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **kannada_stones/** | **187 images** | Mythic Society Inscriptions 3D Conservation (148) + SHILORA Field Collection (39) | Ground Truth Stone Photos | Input Image | Contains 2 exact duplicate pairs |
| **data/raw/** | **39 images** | Local target stones (`stone_001.jpg` to `stone_039.jpg`) | Ground Truth Raw Photos | Input Image | Matches `stone_kn_000001` - `039` |
| **data/preprocessed/** | **39 images** | Output of `ShiloraStonePreprocessor` (Stage 1) | Derived Artifact | Model Prediction | 1:1 scale relief-amplified images |
| **data/binarized/** | **187 masks** | Output of `ShilaLekhya AttentionUNet` (Stage 2) | Derived Artifact | Model Prediction | Attention U-Net binarization |
| **data/episam/ground_truth/** | **148 sets** | Official EpiSAM epigraphical dataset (IIIT Hyderabad) | Verified Ground Truth | Reference Baseline | Polygons, centroids, line masks |
| **data/episam/predictions/** | **183 stones** | Dynamically generated character instance masks | Derived Artifact | Model Prediction | 5 stones failed candidates |
| **data/episam/lines/** | **2,450 crops** | Reconstructed reading-order text line crops across 183 stones | Derived Artifact | Model Prediction | Average 13.4 lines per stone |
| **data/trocr/metadata.csv** | **513 lines** | Aligned expert readings from Mythic Society / Epigraphia Carnatica | Verified Ground Truth Text | Reference Baseline | Split: 368 train, 50 val, 95 test |
| **data/trocr/train/** | **368 crops** | Line crop images for TrOCR training across 45 stones | Ground Truth Visual Crops | Training Split | Zero overlap with val or test |
| **data/trocr/validation/** | **50 crops** | Line crop images for validation across 9 stones | Ground Truth Visual Crops | Validation Split | Zero overlap with train or test |
| **data/trocr/test/** | **95 crops** | Line crop images for test benchmark across 11 stones | Ground Truth Visual Crops | Test Benchmark | Zero overlap with train or val |

### Duplicate Image Detection Audit
Exact SHA256 hashing across `kannada_stones/` revealed 2 identical duplicate image pairs:
1. `Mutkur_1500CE_Donation_Inscription_Not_Documented_Before.png` == `Mutkur_1400CE_Agrahara_Inscription_Not_Documented_Before.png`  
   *SHA256: `a935bebbdd2f5670f5e13b41d40c74900a893c52a953a74ef81ec0a187b22a0a`*
2. `stone_kn_000036.jpg` == `stone_kn_000035.jpg`  
   *SHA256: `65be304cf5eecf45f94b150935d259c6c4ba014b2d18feeaef92b7204f146a48`*

---

## 3. MODEL REGISTRY & CHECKPOINT TRACEABILITY

Every neural model and resource loaded during inference was inspected, hashed, and traced to its training provenance:

### 1. ShilaLekhya Attention U-Net Epigraphical Binarizer
- **Checkpoint Path:** [models/shilalekhya/binarizer.pth](file:///e:/Brahmi-OCR-main/models/shilalekhya/binarizer.pth)
- **File Size:** 126,381,147 bytes (~120.5 MB)
- **SHA256:** `1f111bcf21fe9b0723ee4a0fe513422c2f3969b1445ddfba7c383ed648e85e3d`
- **Architecture:** `AttentionUNet` (3 input channels, 1 output channel, attention-gated skip connections)
- **Provenance:** IIIT Hyderabad / IHDIA research paper: *"Unveiling Text in Challenging Stone Inscriptions: A Character-Context-Aware Patching Strategy for Binarization"* (Jena et al.)
- **Execution Mode:** Batched 512x512 sliding-window patchwise prediction with sliding overlap.

### 2. Official EpiSAM Character Segmentation Model
- **Checkpoint Path:** [models/episam/episam.pth](file:///e:/Brahmi-OCR-main/models/episam/episam.pth)
- **File Size:** 376,190,596 bytes (~358.8 MB)
- **SHA256:** `395e79e8d8997a29ee6f379ca2b2d957d64ded9f2495624344fe3528be546fd3`
- **Architecture:** `SAM ViT-B` (ViT-B image encoder, prompt encoder with centroid prompts, 6-token mask decoder, neighbor-aware head)
- **Provenance:** Official EpiSAM Epigraphical Benchmark checkpoint fine-tuned on historical stone inscriptions.
- **Execution Mode:** Zero-shot prompt-guided inference guided by connected-component candidates.

### 3. SHILORA TrOCR Line Transcription Model
- **Checkpoint Path:** [models/trocr/best_model/model.safetensors](file:///e:/Brahmi-OCR-main/models/trocr/best_model/model.safetensors)
- **File Size:** 246,430,696 bytes (~235.0 MB)
- **SHA256:** `6439b7c9d6f2ed8e02f2da096e27bd2862ef4e506eb5494820758362c64b5a93`
- **Base Architecture:** `VisionEncoderDecoderModel` based on `microsoft/trocr-small-stage1`
  - **Encoder:** Pretrained DeiT visual transformer (frozen during fine-tuning)
  - **Decoder:** 6-layer RoBERTa epigraphical text decoder (fine-tuned)
- **Training Dataset:** `data/trocr/metadata.csv` (Mythic Society Inscription Line Crops)
- **Training Samples:** 368 lines across 45 unique stones
- **Validation Samples:** 50 lines across 9 unique stones
- **Test Samples:** 95 lines across 11 unique stones

---

## 4. TRAINING EVIDENCE & REPRODUCIBILITY

The training script [scripts/train_trocr.py](file:///e:/Brahmi-OCR-main/scripts/train_trocr.py) was audited for legitimate loss convergence and checkpoint saving.

### Training Hyperparameters
- **Optimizer:** `AdamW(lr=5e-5, weight_decay=0.01)`
- **Batch Size:** 8
- **Epochs:** 2 (Native CPU execution)
- **Max Target Length:** 64 tokens
- **Loss Function:** CrossEntropyLoss with padding mask (`ignore_index = -100`)

### Training Loss Progression
- **Epoch 1:** Train Loss = 3.9725 | Val Loss = 1.9679 | Val CER = 1.0517
- **Epoch 2:** Train Loss = 1.9715 | Val Loss = 1.8269 | Val CER = 1.0128
- **Checkpoint Selection Criterion:** Lowest validation CER. Saved to `models/trocr/best_model/`.

---

## 5. ACTUAL TEST METRICS & SCIENTIFIC EVALUATION

A strict runtime evaluation of the 95 test line images was conducted using Levenshtein edit distance and CER metrics. **Training loss decrease is rejected as proof of OCR quality.**

| Metric | Measured Value | Standard Required | Audit Status |
| :--- | :--- | :--- | :--- |
| **Character Error Rate (CER)** | **1.0275 (102.75%)** | < 0.20 (20%) | **FAILED** |
| **Exact Line Accuracy** | **0.00% (0 / 95 lines)** | > 70% | **FAILED** |
| **Average Edit Distance** | **29.87 characters/line** | < 3 characters | **FAILED** |
| **Word Accuracy** | **0.00%** | > 80% | **FAILED** |
| **Evaluated Lines** | **95 lines** | All test lines | **VERIFIED** |
| **Evaluated Stones** | **11 unique stones** | Unseen stones | **VERIFIED** |

### Typical Prediction Examples from Test Evaluation
1. Ground Truth: `"ವೆಳಚಿಗವುಣ್ಡನ ಪಟ್ಟದಳ ಪೊನ್ನ ಚರಿ"`  
   Prediction: `""` (Empty string) — CER: 1.0000
2. Ground Truth: `"ವೆಳಚಿಗವುಣ್ಡನ ಪಟ್ಟದಳ ಪೊನ್ನ ಚರಿ"`  
   Prediction: `"್್್್್್್್್್್್"` (Repeated virama marks) — CER: 0.8966
3. Ground Truth: `"ಹ ಕೇಕ್ರಿತಯುಗೇ ಭ್ರುಗುಮನೇ ತ್ರೇತಾಯುಗೇ"`  
   Prediction: `""` — CER: 1.0000

---

## 6. DATA LEAKAGE AUDIT (STONE-LEVEL PARTITIONING)

A cross-split set intersection analysis was executed to verify that no line crop, visual variant, or stone leaked between splits:

```
Train Stones:      45 unique stones (368 lines)
Validation Stones: 9 unique stones  (50 lines)
Test Stones:       11 unique stones (95 lines)
-----------------------------------------------------------------------------
Leakage Train <-> Validation: 0 stones (EMPTY SET)
Leakage Train <-> Test:       0 stones (EMPTY SET)
Leakage Validation <-> Test:  0 stones (EMPTY SET)
Direct Image File Overlap:    0 images (EMPTY SET)
-----------------------------------------------------------------------------
DATA LEAKAGE AUDIT RESULT: PASSED (ZERO STONE LEAKAGE)
```

Every inscription stone and all its reconstructed lines remain strictly confined to exactly one split.

---

## 7. BRAHMI DATA QUARANTINE AUDIT

A complete audit of all datasets, checkpoints, and scripts was performed to guarantee that legacy Brahmi data is completely quarantined:

```json
{
  "BRAHMI_TRAINING_CONTAMINATION": false,
  "BRAHMI_VALIDATION_CONTAMINATION": false,
  "BRAHMI_TEST_CONTAMINATION": false,
  "BRAHMI_CHECKPOINT_USAGE": false,
  "BRAHMI_LABEL_CONTAMINATION": false,
  "BRAHMI_INFERENCE_CONTAMINATION": false
}
```

- **Training/Validation/Test Splits:** Contain 0% Brahmi characters, 0% Brahmi labels, and 0% Brahmi images.
- **Active Model Weights:** `models/shilalekhya/`, `models/episam/`, and `models/trocr/` contain solely Kannada epigraphical models.
- **Quarantined Artifacts:** Legacy Brahmi models (`brahmi_model_resnet50_new`, `brahmi_model_mobilenet_v2`, `brahmi_model_efficientnetb0_new`) and test images reside strictly within `Brahmi-OCR-main/` and are never loaded or referenced by the SHILORA pipeline.
- Occurrences of the string "Brahmi" in `scripts/` are exclusively filesystem directory path resolutions (`PROJECT_ROOT / "Brahmi-OCR-main" / "backend"`) required to import the local `episam_binarizer` Python module.

---

## 8. TOKENIZER FORENSIC AUDIT (ROOT CAUSE OF HIGH CER)

A dedicated round-trip test (`text -> tokenizer.encode -> tokenizer.decode`) was executed across the full Unicode range of historical and classical Kannada using [reports/tokenizer_forensic_audit.json](file:///e:/Brahmi-OCR-main/reports/tokenizer_forensic_audit.json).

### Critical Findings
1. **Archaic Characters Discarded:**
   - `ಱ` (U+0CB1, Archaic Alveolar RRA) -> Encoded as `[190, 3]` -> Decoded as `""` (Empty string).
   - `ೞ` (U+0CDE, Archaic Retroflex LLA / ZHA) -> Encoded as `[190, 3]` -> Decoded as `""`.
   - `಼` (U+0CBC, Nukta), `ಽ` (U+0CBD, Avagraha) -> Encoded as `<unk>` -> Decoded as `""`.
2. **Kannada Numerals Discarded:**
   - Digits `೦೧೨೩೪೫೬೭೮೯` -> Encoded as `[190, 3]` -> Decoded as `""`.
3. **Consonants & Matras:**
   - Base consonants such as `ಕ` (KA), `ಖ` (KHA), `ಗ` (GA) map to `<unk>` token ID `3`.
   - Only isolated vowel matras (`ಿ` token 63710, `ು` token 63539, `ೆ` token 63711) and the virama `್` (token 63470) exist in the inherited English RoBERTa vocabulary.

### Conclusion on Tokenizer
The high CER (1.0275) is not caused by the visual encoder failing to see strokes, but by the language decoder tokenizer being unable to represent Kannada characters. **Retraining without expanding the tokenizer vocabulary was an architectural flaw.**

---

## 9. CRITICAL ANTI-HARDCODING & FALLBACK AUDIT

All Python, JavaScript, and Vue files in the repository were scanned for hardcoded outputs, sample mock predictions, and filename shortcuts:

1. **Filename-Conditional Shortcuts:**
   - Search for `if filename == ...`, `if "stone_" in ...`, `if image == ...` returned **0 matches** in the inference path.
2. **Canned Prediction Strings:**
   - No hardcoded OCR strings or expected transcriptions exist in [scripts/shilora_orchestrator.py](file:///e:/Brahmi-OCR-main/scripts/shilora_orchestrator.py).
3. **Translation Engine Hardcoding Fix:**
   - An ad-hoc phrase replacement rule in `scripts/translation_engine.py` (lines 190–196: `re.sub(r"May there be auspiciousness / well-being Sacred / Glorious", ...)`) was **flagged and removed**.
   - All vocabulary, morphology cases, and character mappings were strictly externalized to [data/translation/](file:///e:/Brahmi-OCR-main/data/translation/).
4. **Fallback Handling:**
   - If a stage fails (e.g. Quality Gate rejection or 0 character candidates), the system outputs explicit failure statuses (`QUALITY_GATE_FAILED`, `UNSUPPORTED_OR_UNREADABLE`, `NO_VALID_CHARACTERS`) with empty strings, rather than returning a "demo" or "sample" output.

---

## 10. TRANSLATION ENGINE ARCHITECTURE & PROVENANCE

### Classification
- **Classification:** **CATEGORY B (EXTERNAL VERIFIED RESOURCE) + CATEGORY C (DETERMINISTIC LINGUISTIC RULE)**.
- **Is it a Trained AI Model?** **NO.**
- **Provenance Statement:** Translation is produced via verified epigraphical lexicons and deterministic Halegannada morphology rules applied to the OCR transcription. **No AI translation model was trained on the dataset.**

### Externalized Resource Manifest
1. [data/translation/epigraphical_lexicon.json](file:///e:/Brahmi-OCR-main/data/translation/epigraphical_lexicon.json)
   - 416 lines, 60+ historical epigraphical terms covering Kadamba, Western Ganga, and Vijayanagara inscriptions.
   - Grounded in *Epigraphia Carnatica Vol IX* and *Mythic Society Conservation Records*.
2. [data/translation/historical_morphology.json](file:///e:/Brahmi-OCR-main/data/translation/historical_morphology.json)
   - 101 lines, Old Kannada case suffixes (locative *-dolu*, past verbal *-dan*, plural *-dar*, etc.).
   - Sourced from *Kittel Kannada Grammar*.
3. [data/translation/normalization_rules.json](file:///e:/Brahmi-OCR-main/data/translation/normalization_rules.json)
   - Orthographic normalization mapping archaic `ಱ -> ರ`, `ೞ -> ಳ`, and repha gemination without modifying raw OCR strings.

### Anti-Hallucination Policy
Any unrecognized token is tagged as `[ಅಜ್ಞಾತ ಐತಿಹಾಸಿಕ ಪದ: <token>]` in Modern Kannada and `[UNKNOWN_HISTORICAL_TERM: <token>]` in English. The system **never invents names, kings, places, dates, or historical events**.

---

## 11. RUNTIME INFERENCE AUDIT (PARTS 12, 13, 14, 15)

A comprehensive suite of runtime tests was executed to prove that predictions are dynamically computed at runtime:

### Part 13: Random / Non-Inscription Image Test (Anti-Hallucination)
- **Input:** 400x400 synthetic noise image with geometric shapes.
- **Pipeline Result:**
  - `pipeline_status`: `"UNSUPPORTED_OR_UNREADABLE"`
  - `error_stage`: `"QUALITY_GATE"`
  - `binarization_status`: `"QUALITY_GATE_FAILED"`
  - `raw_ocr_text`: `""`
  - `modern_kannada`: `""`
  - `english`: `""`
- **Result:** **PASSED.** System rejected the unreadable image without fabricating characters or translations.

### Part 14: Image Perturbation Test (Anti-Lookup Verification)
Perturbations of `stone_kn_000001.jpg` were processed through the full pipeline:

| Variant | Input Image SHA256 | Reconstructed Lines | Timing | Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Variant Crop** (Central 80%) | `c131d25d0c...` | 9 lines | 81.2s | Dynamic inference executed |
| **Variant Brightness** (+35) | `26b8b2e35a...` | 10 lines | 84.7s | Dynamic inference executed |
| **Variant Contrast** (x1.35) | `96a79ee059...` | 10 lines | 86.1s | Dynamic inference executed |
| **Variant Rotation** (+3°) | `83df4a9381...` | 9 lines | 83.5s | Dynamic inference executed |
| **Variant Resized** (0.75x) | `8f56e301d4...` | 8 lines | 72.4s | Dynamic inference executed |

Every perturbation yielded distinct intermediate hashes and dynamic execution times, proving results are not looked up by filename.

### Part 15: No-Cached-Prediction Test
- A uniquely timestamped job (`uncached_test_stone_1775536420`) was executed from scratch.
- The pipeline created `01_raw.png`, `02_preprocessed.png`, `03_binarized.png`, line crops, and `analysis_report.json` on the fly without relying on any pre-generated directory.
- **Result:** **PASSED.**

---

## 12. 184 / 187 SEGMENTATION ISSUE INVESTIGATION

The previous report claimed 184 / 187 stones segmented. A forensic check revealed the actual numbers:
- **Total Inscription Stones:** 187 stones
- **Successfully Segmented Stones:** **182 unique stones** (148 Mythic Society + 34 SHILORA stones)
- **Failed Stones:** **5 stones** (`stone_006`, `stone_007`, `stone_010`, `stone_011`, `stone_019`)

### Detailed Breakdown of Failed Stones

| Stone ID | Image Path | Failure Stage | Failure Reason & Mechanism | Final System Handling |
| :--- | :--- | :--- | :--- | :--- |
| **stone_006** | `kannada_stones/stone_kn_000006.jpg` | `QUALITY_GATE` | Binarized foreground ratio = 0.9990. Severely eroded surface caused Attention U-Net to output inverted white mask. | Rejected with `QUALITY_GATE_FAILED` |
| **stone_007** | `kannada_stones/stone_kn_000007.jpg` | `QUALITY_GATE` | Binarized foreground ratio = 1.0000. Low lighting caused solid white saturation. | Rejected with `QUALITY_GATE_FAILED` |
| **stone_010** | `kannada_stones/stone_kn_000010.jpg` | `QUALITY_GATE` | Solid white binarization mask (`fg_ratio = 1.0000`). Zero valid connected components. | Rejected with `QUALITY_GATE_FAILED` |
| **stone_011** | `kannada_stones/stone_kn_000011.jpg` | `QUALITY_GATE` | Saturated mask (`fg_ratio = 0.9995`). Zero valid character candidate boxes found. | Rejected with `QUALITY_GATE_FAILED` |
| **stone_019** | `kannada_stones/stone_kn_000019.jpg` | `QUALITY_GATE` | Severe planar lighting gradient resulting in mask saturation (`fg_ratio = 1.0000`). | Rejected with `QUALITY_GATE_FAILED` |

**Production Handling:** The system cleanly flags these stones as `UNSUPPORTED_OR_UNREADABLE` without crashing, returning mock characters, or fabricating translations.

---

## 13. FRONTEND & HTTP API FLOW AUDIT

The backend endpoint `/api/shilora/analyze` in [Brahmi-OCR-main/backend/app.py](file:///e:/Brahmi-OCR-main/Brahmi-OCR-main/backend/app.py) was audited across 4 test scenarios:

1. **Known Test Inscription (`stone_kn_000001.jpg`):**
   - Status: HTTP 200, `pipeline_status = SUCCESS`
   - Real model execution: 10 lines segmented, TrOCR evaluated, translation glossed.
2. **Unseen Kannada Inscription (`Begur_900CE_Tondabbe_Sanyasana_Inscription.png`):**
   - Status: HTTP 200, `pipeline_status = SUCCESS`
   - Real model execution: 7 lines segmented dynamically.
3. **Low-Quality Inscription (`stone_kn_000006.jpg`):**
   - Status: HTTP 200, `pipeline_status = UNSUPPORTED_OR_UNREADABLE`, `error_stage = QUALITY_GATE`
   - Clean fail-safe handling with zero hallucinated text.
4. **Non-Inscription Image (`random_non_inscription_test.png`):**
   - Status: HTTP 200, `pipeline_status = UNSUPPORTED_OR_UNREADABLE`
   - Rejected at Quality Gate stage.

---

## 14. REMAINING ARCHITECTURAL LIMITATIONS

1. **TrOCR Tokenizer Vocabulary Mismatch:**  
   The baseline RoBERTa tokenizer vocabulary lacks the Kannada Unicode range (`U+0C80`–`U+0CFF`), preventing the model from predicting anything other than virama marks (`್`) or `<unk>`. To achieve functional OCR, the tokenizer vocabulary must be expanded by ~100 Kannada epigraphical tokens and the embedding matrix resized (`resize_token_embeddings()`).
2. **CPU Execution Throughput:**  
   On CPU, a full stone analysis takes 75–90 seconds (Attention U-Net ~16s, EpiSAM ~30s, TrOCR ~40s). Real-time interactive use requires GPU execution or ONNX FP16 quantization.
3. **5 Saturated Stone Inscriptions:**  
   Stones 6, 7, 10, 11, and 19 require multi-scale contrast-adaptive binarization thresholds to prevent inverted mask saturation.

---

## 15. FINAL DECISION

```
========================================================================================
SYSTEM STATUS: NOT_PRODUCTION_READY
========================================================================================
Summary:
SHILORA successfully demonstrates an authentic, un-hardcoded, and scientifically sound 
epigraphical AI pipeline with zero Brahmi contamination and genuine runtime execution. 
However, due to the TrOCR test CER of 1.0275 resulting from tokenizer vocabulary limitations, 
and the 5 segmentation failures out of 187 stones, the system cannot be declared 
production-ready for reliable historical inscription reading.
========================================================================================
```
