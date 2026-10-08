import os
import sys
from pathlib import Path

sys.path.insert(0, ".")
from scripts.shilora_orchestrator import ShiloraProductionPipeline

pipeline = ShiloraProductionPipeline()
results = {}

print("Testing all 39 stones through ShiloraProductionPipeline:")
for i in range(1, 40):
    img_name = f"stone_kn_{i:06d}.jpg"
    img_path = os.path.join("kannada_stones", img_name)
    if os.path.exists(img_path):
        res = pipeline.process_inscription(img_path, inscription_name=f"stone_{i:03d}")
        p_status = res.get("pipeline_status", "UNKNOWN")
        err_stage = res.get("error_stage", "NONE")
        seg_status = res.get("segmentation_status", "")
        num_lines = len(res.get("lines", []))
        qg = res.get("quality_gate", {})
        results[i] = {
            "status": p_status,
            "error_stage": err_stage,
            "seg_status": seg_status,
            "lines": num_lines,
            "fg_ratio": qg.get("foreground_ratio", 0),
            "valid_ccs": qg.get("valid_character_candidates", 0)
        }
        print(f"Stone {i:02d} ({img_name}): Status={p_status} | ErrorStage={err_stage} | Lines={num_lines} | FG={qg.get('foreground_ratio')} | VCC={qg.get('valid_character_candidates')}")
    else:
        print(f"Stone {i:02d} missing!")

summary = {"SUCCESS": 0, "FAILED": 0}
for k, v in results.items():
    if v["status"] == "SUCCESS":
        summary["SUCCESS"] += 1
    else:
        summary["FAILED"] += 1
print("Summary:", summary)
