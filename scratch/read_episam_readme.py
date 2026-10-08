import urllib.request
import json
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def get_file(path):
    url = f"https://raw.githubusercontent.com/ihdia/episam/main/{path}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8')

readme = get_file("README.md")
print("=== README.md ===")
print(readme)
