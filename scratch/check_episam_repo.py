import urllib.request
import json
import os

try:
    req = urllib.request.Request('https://raw.githubusercontent.com/ihdia/episam/main/README.md', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        readme = resp.read().decode('utf-8')
    print('=== README ===')
    print(readme)
except Exception as e:
    print('README ERR:', e)

try:
    print('=== REPO TREE ===')
    req_tree = urllib.request.Request('https://api.github.com/repos/ihdia/episam/git/trees/main?recursive=1', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_tree) as resp:
        tree = json.loads(resp.read().decode('utf-8'))
        for item in tree.get('tree', []):
            print(f"{item['path']} ({item['type']})")
except Exception as e:
    print('TREE ERR:', e)
