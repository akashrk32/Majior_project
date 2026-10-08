import os
import sys
import json
import time
import hashlib
from pathlib import Path
import cv2
import numpy as np

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from scripts.shilora_orchestrator import ShiloraProductionPipeline

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

pipeline = ShiloraProductionPipeline()
audit_results = {}

# ============================================================================
# PART 13: RANDOM / NON-INSCRIPTION IMAGE TEST
# ============================================================================
print("\n" + "=" * 60)
print("PART 13: RANDOM / NON-INSCRIPTION IMAGE TEST")
print("=" * 60)

# Create a random noise / non-inscription image
random_img = np.random.randint(50, 200, (400, 400, 3), dtype=np.uint8)
# Add some geometric non-inscription shapes
cv2.circle(random_img, (200, 200), 80, (10, 20, 30), -1)
cv2.rectangle(random_img, (50, 50), (150, 150), (220, 220, 220), 4)

random_img_path = root / "outputs" / "random_non_inscription_test.png"
random_img_path.parent.mkdir(parents=True, exist_ok=True)
cv2.imwrite(str(random_img_path), random_img)

res_random = pipeline.process_inscription(
    str(random_img_path),
    inscription_name="random_non_inscription_test",
    output_dir="outputs/runtime_audit"
)

print(f"Random Image Status: {res_random.get('pipeline_status')}")
print(f"Error Stage:         {res_random.get('error_stage')}")
print(f"Binarization Status: {res_random.get('binarization_status')}")
print(f"OCR Status:          {res_random.get('ocr_status')}")
print(f"Modern Kannada:      {res_random.get('modern_kannada')!r}")
print(f"English:             {res_random.get('english')!r}")
print(f"Warnings:            {res_random.get('warnings')}")

part13_passed = (
    res_random.get("pipeline_status") == "UNSUPPORTED_OR_UNREADABLE" and
    res_random.get("raw_ocr_text", "") == "" and
    res_random.get("modern_kannada", "") == "" and
    res_random.get("english", "") == ""
)
print(f"Part 13 Anti-Hallucination Result: {'PASSED' if part13_passed else 'FAILED'}")

audit_results["part_13_random_image_test"] = {
    "passed": part13_passed,
    "input_path": str(random_img_path),
    "response": res_random
}

# ============================================================================
# PART 14: IMAGE PERTURBATION TEST
# ============================================================================
print("\n" + "=" * 60)
print("PART 14: IMAGE PERTURBATION TEST")
print("=" * 60)

base_stone = root / "kannada_stones" / "stone_kn_000001.jpg"
base_bgr = cv2.imread(str(base_stone))
h, w = base_bgr.shape[:2]

perturbations = {
    "variant_crop": base_bgr[int(h*0.1):int(h*0.9), int(w*0.1):int(w*0.9)],
    "variant_brightness": np.clip(base_bgr.astype(np.int32) + 35, 0, 255).astype(np.uint8),
    "variant_contrast": np.clip(base_bgr.astype(np.float32) * 1.35, 0, 255).astype(np.uint8),
    "variant_rotation": cv2.warpAffine(base_bgr, cv2.getRotationMatrix2D((w/2, h/2), 3.0, 1.0), (w, h)),
    "variant_resized": cv2.resize(base_bgr, (int(w*0.75), int(h*0.75)), interpolation=cv2.INTER_AREA)
}

perturbation_runs = {}
for p_name, p_img in perturbations.items():
    p_path = root / "outputs" / f"{p_name}.png"
    cv2.imwrite(str(p_path), p_img)
    t0 = time.time()
    p_res = pipeline.process_inscription(
        p_img,
        inscription_name=p_name,
        output_dir="outputs/runtime_audit"
    )
    dt = round(time.time() - t0, 2)
    p_sha = compute_sha256(p_path)
    print(f"Perturbation [{p_name}]: Status={p_res.get('pipeline_status')}, Lines={len(p_res.get('lines', []))}, OCR_chars={len(p_res.get('raw_ocr_text', ''))}, time={dt}s")
    perturbation_runs[p_name] = {
        "input_sha256": p_sha,
        "pipeline_status": p_res.get("pipeline_status"),
        "lines_reconstructed": len(p_res.get("lines", [])),
        "raw_ocr_length": len(p_res.get("raw_ocr_text", "")),
        "execution_time": dt
    }

audit_results["part_14_perturbation_test"] = perturbation_runs

# ============================================================================
# PART 15: NO-CACHED-PREDICTION TEST
# ============================================================================
print("\n" + "=" * 60)
print("PART 15: NO-CACHED-PREDICTION TEST")
print("=" * 60)
# We process a stone with a completely custom unique name to verify zero cache dependency
fresh_name = f"uncached_test_stone_{int(time.time())}"
t0 = time.time()
fresh_res = pipeline.process_inscription(
    str(base_stone),
    inscription_name=fresh_name,
    output_dir="outputs/runtime_audit"
)
dt_fresh = round(time.time() - t0, 2)
out_dir = root / "outputs" / "runtime_audit" / fresh_name
created_files = [f.name for f in out_dir.iterdir()] if out_dir.exists() else []

print(f"Fresh Uncached Run [{fresh_name}]:")
print(f"  Pipeline Status: {fresh_res.get('pipeline_status')}")
print(f"  Execution Time: {dt_fresh}s")
print(f"  Generated Artifacts ({len(created_files)}): {created_files}")

part15_passed = (
    fresh_res.get("pipeline_status") == "SUCCESS" and
    "01_raw.png" in created_files and
    "02_preprocessed.png" in created_files and
    "03_binarized.png" in created_files and
    "analysis_report.json" in created_files
)
print(f"Part 15 Dynamic Generation: {'PASSED' if part15_passed else 'FAILED'}")

audit_results["part_15_no_cached_predictions"] = {
    "passed": part15_passed,
    "unique_name": fresh_name,
    "execution_time": dt_fresh,
    "artifacts_created": created_files
}

# ============================================================================
# PART 12: IMAGE -> FINAL RESULT REAL INFERENCE TEST (5 STONES)
# ============================================================================
print("\n" + "=" * 60)
print("PART 12: REAL INFERENCE TEST (5 STONES)")
print("=" * 60)

test_5_stones = [
    ("stone_kn_000002.jpg", "kannada_stones/stone_kn_000002.jpg"),
    ("stone_kn_000003.jpg", "kannada_stones/stone_kn_000003.jpg"),
    ("stone_kn_000004.jpg", "kannada_stones/stone_kn_000004.jpg"),
    ("stone_kn_000005.jpg", "kannada_stones/stone_kn_000005.jpg"),
    ("Begur_900CE_Tondabbe_Sanyasana", "kannada_stones/Begur_900CE_Tondabbe_Sanyasana_Inscription.png")
]

part12_results = []
for s_name, s_relpath in test_5_stones:
    s_full = root / s_relpath
    if not s_full.exists():
        print(f"Skipping {s_name} - not found.")
        continue
    t0 = time.time()
    res = pipeline.process_inscription(
        str(s_full),
        inscription_name=s_name.replace(".jpg", "").replace(".png", ""),
        output_dir="outputs/runtime_audit/part12"
    )
    dt = round(time.time() - t0, 2)
    print(f"Stone [{s_name}]:")
    print(f"  Pipeline Status:     {res.get('pipeline_status')}")
    print(f"  Binarization Status: {res.get('binarization_status')}")
    print(f"  Segmentation Status: {res.get('segmentation_status')}")
    print(f"  OCR Text:            {res.get('raw_ocr_text')[:40]!r}")
    print(f"  Translation Status:  {res.get('translation_status')}")
    print(f"  Execution Time:      {dt}s")

    part12_results.append({
        "input_image": str(s_relpath),
        "pipeline_status": res.get("pipeline_status"),
        "binarization_status": res.get("binarization_status"),
        "segmentation_status": res.get("segmentation_status"),
        "line_reconstruction_status": res.get("line_reconstruction_status"),
        "ocr_text": res.get("raw_ocr_text"),
        "ocr_confidence": res.get("stage_confidences", {}).get("ocr_confidence", 0.0),
        "translation_status": res.get("translation_status"),
        "modern_kannada": res.get("modern_kannada"),
        "english": res.get("english"),
        "uncertain_tokens": res.get("uncertain_tokens", []),
        "evidence": res.get("evidence", []),
        "warnings": res.get("warnings", []),
        "timings_seconds": res.get("timings_seconds", {})
    })

audit_results["part_12_five_stone_inference"] = part12_results

# Save complete audit json
with open(root / "reports" / "runtime_inference_audit.json", "w", encoding="utf-8") as f:
    json.dump(audit_results, f, indent=2, ensure_ascii=False)
print("\nSaved runtime inference audit to reports/runtime_inference_audit.json")
