import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

for p in [
    "e:/Brahmi-OCR-main/Brahmi-OCR-main/backend/transliteration_mapping.json",
    "e:/Brahmi-OCR-main/Brahmi-OCR-main/backend/brahmi_model_mobilenet_v2/vocab.json",
    "e:/Brahmi-OCR-main/Brahmi-OCR-main/backend/brahmi_model_resnet50_new/class_names.json"
]:
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f:
            data = json.load(f)
            print(f"\n=== {p} ===")
            if isinstance(data, list):
                print(f"List length: {len(data)}, sample: {data[:10]}")
            elif isinstance(data, dict):
                print(f"Dict length: {len(data)}, sample keys/items: {list(data.items())[:10]}")
    except Exception as e:
        print(f"Error {p}: {e}")
