import csv
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Read our 148 stones
ks_dir = Path("e:/Brahmi-OCR-main/kannada_stones")
pattern_39 = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.jpg$", re.IGNORECASE)
local_148 = [f.name for f in ks_dir.iterdir() if f.is_file() and not pattern_39.match(f.name)]

# Read the parsed mythic society transcriptions
transcription_file = Path("e:/Brahmi-OCR-main/scratch/mythic_society_transcriptions.csv")

inscription_lines = {}
with open(transcription_file, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    cur_name = ""
    for r in reader:
        name = r["Inscription_Name"].strip()
        if name:
            cur_name = name
        reading = r["Expert_Reading"].strip()
        if cur_name and reading and reading != "Expert_Reading":
            if cur_name not in inscription_lines:
                inscription_lines[cur_name] = []
            inscription_lines[cur_name].append({
                "line_reading": reading,
                "our_reading": r["Our_Reading"].strip(),
                "year": r["Year"].strip(),
                "quality": r["Surface_Quality"].strip()
            })

print(f"Total inscriptions with readings in spreadsheet: {len(inscription_lines)}")
total_transcribed_lines = sum(len(lines) for lines in inscription_lines.values())
print(f"Total transcribed lines in spreadsheet: {total_transcribed_lines}")

def norm_str(s):
    s = Path(s).stem.lower()
    return re.sub(r'[^a-z0-9]', '', s)

local_norm = {norm_str(f): f for f in local_148}
spread_norm = {norm_str(k): (k, len(v)) for k, v in inscription_lines.items()}

matched_stones = {}
unmatched_local = []

for k_norm, local_f in local_norm.items():
    # Exact or substring match
    best_match = None
    if k_norm in spread_norm:
        best_match = spread_norm[k_norm]
    else:
        # try fuzzy or prefix
        for s_norm, (orig_name, count) in spread_norm.items():
            if k_norm[:20] in s_norm or s_norm[:20] in k_norm:
                best_match = (orig_name, count)
                break
    if best_match:
        matched_stones[local_f] = best_match
    else:
        unmatched_local.append(local_f)

print(f"\nMatched stones from our 148 dataset with Mythic Society expert readings: {len(matched_stones)} / 148")
matched_lines_count = sum(c[1] for c in matched_stones.values())
print(f"Total verified expert lines for our matched stones: {matched_lines_count}")

print("\nSample 10 matches:")
for l_f, (s_name, count) in list(matched_stones.items())[:10]:
    print(f"  {l_f[:40]:40s} -> '{s_name[:40]:40s}' ({count} lines)")

print(f"\nUnmatched stones count: {len(unmatched_local)}")
if unmatched_local:
    print("Sample unmatched (first 5):", unmatched_local[:5])
