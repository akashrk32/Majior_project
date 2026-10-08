from pathlib import Path
import json
import re

src = Path("pdf_dataset/kannada_converted.json")
data = json.loads(src.read_text(encoding="utf-8"))

entries = []
current = None

for item in data:
    text = item["text"].replace("\\n", "\n").strip()

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        # New dictionary entry: WORD - MEANING
        match = re.match(r"^(.+?)\s+-\s+(.+)$", line)

        if match:
            if current:
                entries.append(current)

            word = match.group(1).strip()
            meaning = match.group(2).strip()

            current = {
                "word": word,
                "meaning": meaning,
                "page": item["page"]
            }

        elif current:
            # Continuation of previous meaning
            current["meaning"] += " " + line

if current:
    entries.append(current)

# Remove obvious section headings
entries = [
    x for x in entries
    if len(x["word"]) > 1
    and x["word"] not in {"ಹಳಗನ್ನಡ", "ಪದಸಂಪದ"}
]

Path("pdf_dataset/old_kannada_dictionary.json").write_text(
    json.dumps(entries, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Dictionary entries:", len(entries))
print("Saved: pdf_dataset/old_kannada_dictionary.json")