import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

files_to_inspect = [
    "dataset_scripts/prepare_dataset.py",
    "data_loader.py",
    "evaluate.py",
    "neighbor_metrics_inference.py",
    "2_hop_graphs_lines.py"
]

for fpath in files_to_inspect:
    url = f"https://raw.githubusercontent.com/ihdia/episam/main/{fpath}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            print(f"\n{'='*20} {fpath} (Lines: {len(content.splitlines())}) {'='*20}")
            # print first 100 lines
            lines = content.splitlines()
            for i, l in enumerate(lines[:60]):
                print(f"{i+1:3d}: {l}")
            if len(lines) > 60:
                print(f"    ... and {len(lines)-60} more lines")
    except Exception as e:
        print(f"Error fetching {fpath}: {e}")
