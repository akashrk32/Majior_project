import os
import sys
import json
import io
from pathlib import Path

root = Path(__file__).resolve().parent.parent
backend_dir = root / "Brahmi-OCR-main" / "backend"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(root))

from app import app

client = app.test_client()

print("=" * 60)
print("PART 21: FRONTEND / HTTP API UPLOAD PIPELINE TEST")
print("=" * 60)

test_scenarios = [
    {
        "type": "KNOWN_TEST_INSCRIPTION",
        "image_path": root / "kannada_stones" / "stone_kn_000001.jpg",
        "name": "api_test_known_stone_001"
    },
    {
        "type": "UNSEEN_KANNADA_INSCRIPTION",
        "image_path": root / "kannada_stones" / "Begur_900CE_Tondabbe_Sanyasana_Inscription.png",
        "name": "api_test_unseen_begur"
    },
    {
        "type": "LOW_QUALITY_INSCRIPTION",
        "image_path": root / "kannada_stones" / "stone_kn_000006.jpg",
        "name": "api_test_low_quality_stone_006"
    },
    {
        "type": "NON_INSCRIPTION_IMAGE",
        "image_path": root / "outputs" / "random_non_inscription_test.png",
        "name": "api_test_non_inscription"
    }
]

api_results = []

for sc in test_scenarios:
    p = sc["image_path"]
    print(f"\nTesting Scenario: {sc['type']} ({p.name})")
    if not p.exists():
        print(f"File {p} does not exist.")
        continue

    with open(p, "rb") as f:
        img_bytes = f.read()

    data = {
        'image': (io.BytesIO(img_bytes), p.name),
        'inscription_name': sc["name"]
    }

    resp = client.post('/api/shilora/analyze', data=data, content_type='multipart/form-data')
    print(f"HTTP Status: {resp.status_code}")
    res_json = resp.get_json()
    
    print(f"Pipeline Status:     {res_json.get('pipeline_status')}")
    print(f"Binarization Status: {res_json.get('binarization_status')}")
    print(f"Segmentation Status: {res_json.get('segmentation_status')}")
    print(f"OCR Status:          {res_json.get('ocr_status')}")
    print(f"Modern Kannada:      {res_json.get('modern_kannada')[:50]!r}...")
    print(f"English:             {res_json.get('english')[:50]!r}...")
    print(f"Warnings:            {res_json.get('warnings')}")

    api_results.append({
        "scenario": sc["type"],
        "input_image": str(p),
        "http_status": resp.status_code,
        "pipeline_status": res_json.get("pipeline_status"),
        "error_stage": res_json.get("error_stage"),
        "raw_ocr_length": len(res_json.get("raw_ocr_text", "")),
        "translation_status": res_json.get("translation_status"),
        "warnings": res_json.get("warnings", []),
        "stage_confidences": res_json.get("stage_confidences", {})
    })

out_file = root / "reports" / "frontend_api_upload_audit.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(api_results, f, indent=2, ensure_ascii=False)
print(f"\nSaved API test results to {out_file}")
