import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://raw.githubusercontent.com/ihdia/episam/main/dataset_scripts/prepare_dataset.py"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    content = resp.read().decode('utf-8')

lines = content.splitlines()
print(f"prepare_dataset.py total lines: {len(lines)}")
for i, l in enumerate(lines[:120]):
    print(f"{i+1:3d}: {l}")
