import sys, json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("outputs/pipeline_results/user_uploaded_slab/analysis_report.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print("=" * 60)
print("PIPELINE STATUS:", d.get("pipeline_status"))
print("BINARIZATION STATUS:", d.get("binarization_status"))
print("SELECTED CANDIDATE:", d.get("selected_binary_candidate"))
print("FALLBACK TO GRAYSCALE:", d.get("fallback_to_enhanced_grayscale"))
print("STROKE QUALITY SCORE:", d.get("stage_confidences", {}).get("stroke_preservation_score"))
print("TOTAL LINES RECONSTRUCTED:", len(d.get("lines", [])))
print("=" * 60)

for l in d.get("lines", []):
    print(f"Line {l['line_index']:02d} | Repr: {l.get('selected_representation')} | BBox: {l['bbox']} | Text: {l['transcription']}")
