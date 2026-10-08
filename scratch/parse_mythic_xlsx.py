import zipfile
import xml.etree.ElementTree as ET
import sys
import json
import csv

sys.stdout.reconfigure(encoding='utf-8')

with zipfile.ZipFile("scratch/mythic_society.xlsx") as zf:
    # 1. Parse shared strings
    sst_tree = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    shared_strings = []
    for si in sst_tree.findall(f"{ns}si"):
        t_el = si.find(f"{ns}t")
        if t_el is not None and t_el.text:
            shared_strings.append(t_el.text)
        else:
            # might have multiple text runs <r><t>...</t></r>
            runs = [r.find(f"{ns}t").text for r in si.findall(f"{ns}r") if r.find(f"{ns}t") is not None and r.find(f"{ns}t").text]
            shared_strings.append("".join(runs))

    print(f"Total shared strings: {len(shared_strings)}")

    # 2. Parse sheet1
    sheet_tree = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))
    rows_data = []
    for row in sheet_tree.iter(f"{ns}row"):
        row_cells = {}
        for c in row.iter(f"{ns}c"):
            r_coord = c.attrib.get('r', '')
            t_type = c.attrib.get('t', '')
            v_el = c.find(f"{ns}v")
            val = ""
            if v_el is not None and v_el.text:
                if t_type == 's':
                    val = shared_strings[int(v_el.text)]
                else:
                    val = v_el.text
            row_cells[r_coord] = val
        rows_data.append(row_cells)

print(f"Total rows in sheet1: {len(rows_data)}")

# Let's inspect the headers and rows
# Map column letters A, B, C, D...
parsed_rows = []
for r in rows_data:
    cols = {}
    for coord, val in r.items():
        col_letter = "".join(filter(str.isalpha, coord))
        cols[col_letter] = val
    if any(cols.values()):
        parsed_rows.append(cols)

print(f"Non-empty rows: {len(parsed_rows)}")
print("Header row (row 0):", parsed_rows[0])

# Check how many distinct inscriptions are in the file
inscription_names = set()
for r in parsed_rows[1:]:
    name = r.get('A', '').strip()
    if name:
        inscription_names.add(name)

print(f"Distinct Inscription Names in file: {len(inscription_names)}")
for name in sorted(list(inscription_names))[:20]:
    print(" -", name)

# Save parsed rows as CSV
with open("scratch/mythic_society_transcriptions.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Row", "Inscription_Name", "Expert_Reading", "Our_Reading", "Diff_Aksharas_1", "Diff_Aksharas_2", "Year", "Surface_Quality"])
    for idx, r in enumerate(parsed_rows[1:], start=1):
        writer.writerow([
            idx,
            r.get('A', ''),
            r.get('B', ''),
            r.get('C', ''),
            r.get('D', ''),
            r.get('E', ''),
            r.get('F', ''),
            r.get('G', '')
        ])

print("Saved scratch/mythic_society_transcriptions.csv")
