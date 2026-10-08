import sys
sys.path.insert(0, ".")
from scripts.shilora_orchestrator import ShiloraProductionPipeline

pipeline = ShiloraProductionPipeline()
for i in [1, 6, 7, 10, 11, 19]:
    p = f"kannada_stones/stone_kn_{i:06d}.jpg"
    res = pipeline.process_inscription(p, inscription_name=f"stone_{i:03d}")
    print(f"Stone {i}: status={res.get('pipeline_status')}, error_stage={res.get('error_stage')}, warnings={res.get('warnings')}")
