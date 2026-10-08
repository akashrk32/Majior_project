import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://raw.githubusercontent.com/ihdia/episam/main/data_loader.py"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    content = resp.read().decode('utf-8')

lines = content.splitlines()
for i, l in enumerate(lines[100:220]):
    print(f"{i+101:3d}: {l}")
