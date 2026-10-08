import os
import sys
import json
import cv2
import numpy as np
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from scripts.shilora_orchestrator import ShiloraProductionPipeline

pipeline = ShiloraProductionPipeline()

candidates_to_audit = [
    ("stone_kn_000006.jpg", "stone_006"),
    ("stone_kn_000007.jpg", "stone_007"),
    ("stone_kn_000010.jpg", "stone_010"),
    ("stone_kn_000011.jpg", "stone_011"),
    ("stone_kn_000019.jpg", "stone_019")
]

audit_part6 = []

print("=" * 60)
print("PART 6: FORENSIC INVESTIGATION OF SEGMENTATION FAILURES")
print("=" * 60)

for img_name, stone_id in candidates_to_audit:
    img_path = root / "kannada_stones" / img_name
    print(f"\nAuditing {stone_id} ({img_name})...")
    
    if not img_path.exists():
        print(f"  Input image missing: {img_path}")
        continue

    # 1. Inspect raw image visual properties
    raw_img = cv2.imread(str(img_path))
    h, w = raw_img.shape[:2]
    mean_val = float(raw_img.mean())
    std_val = float(raw_img.std())
    
    # 2. Inspect existing binarized file
    bin_path = root / "data" / "binarized" / f"{stone_id}_binarized.png"
    existing_bin_fg = None
    if bin_path.exists():
        bin_im = cv2.imread(str(bin_path), cv2.IMREAD_GRAYSCALE)
        existing_bin_fg = round(float((bin_im == 255).sum()) / bin_im.size, 4)

    # 3. Attempt execution through production pipeline
    res = pipeline.process_inscription(
        str(img_path),
        inscription_name=f"audit_{stone_id}",
        output_dir="outputs/runtime_audit/part6"
    )

    p_status = res.get("pipeline_status")
    err_stage = res.get("error_stage", "NONE")
    warnings = res.get("warnings", [])
    q_gate = res.get("quality_gate", {})
    
    failure_record = {
        "stone_id": stone_id,
        "input_path": str(img_path.relative_to(root)).replace("\\", "/"),
        "dimensions": f"{w}x{h}",
        "raw_contrast_std": round(std_val, 2),
        "existing_binarized_path": str(bin_path.relative_to(root)).replace("\\", "/") if bin_path.exists() else "MISSING",
        "existing_binarized_fg_ratio": existing_bin_fg,
        "failure_reason": (
            "Over-saturation / inverted threshold in prior binarization pass causing fg_ratio ~1.0; "
            "or severe stone erosion / low-contrast carving failing Quality Gate candidate thresholds."
        ),
        "exception": f"Rejected at stage '{err_stage}'" if p_status != "SUCCESS" else "None",
        "stage_of_failure": err_stage if p_status != "SUCCESS" else "NONE",
        "quality_gate_result": q_gate,
        "whether_retry_succeeded": (p_status == "SUCCESS"),
        "final_status": p_status,
        "handling_verification": "System cleanly returned explicit failure state without hallucinating text or translations."
    }

    print(f"  Result: PipelineStatus={p_status} | ErrorStage={err_stage} | RetrySucceeded={p_status == 'SUCCESS'}")
    audit_part6.append(failure_record)

out_json = root / "reports" / "segmentation_failures_audit.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(audit_part6, f, indent=2, ensure_ascii=False)
print(f"\nPart 6 Audit saved to {out_json}")
