import urllib.request
import os
import time
from pathlib import Path

dest = Path("e:/Brahmi-OCR-main/data/episam/episam_dataset.zip")
dest.parent.mkdir(parents=True, exist_ok=True)
url = "https://huggingface.co/datasets/keyfinder08/EpiSAM_Inscriptions_Dataset/resolve/main/episam_dataset.zip"

req_head = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
req_head.get_method = lambda: 'HEAD'
with urllib.request.urlopen(req_head) as resp:
    total_size = int(resp.headers.get('Content-Length', 0))

print(f"Target: {dest}")
print(f"Total size: {total_size / (1024*1024):.2f} MB")

while True:
    cur_size = dest.stat().st_size if dest.exists() else 0
    if cur_size >= total_size:
        print(f"Download complete: {cur_size / (1024*1024):.2f} MB")
        break
    
    print(f"Downloading from byte {cur_size} ({cur_size/(1024*1024):.2f} / {total_size/(1024*1024):.2f} MB)...")
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Range': f'bytes={cur_size}-{total_size-1}'
    })
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp, open(dest, "ab") as f:
            chunk_size = 1024 * 1024 * 2 # 2MB
            last_report = cur_size
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                cur_size += len(chunk)
                if cur_size - last_report >= 1024 * 1024 * 25:
                    pct = (cur_size / total_size * 100)
                    print(f"Progress: {cur_size / (1024*1024):.1f}/{total_size / (1024*1024):.1f} MB ({pct:.1f}%)")
                    last_report = cur_size
    except Exception as e:
        print(f"Connection retry: {e}. Waiting 2s...")
        time.sleep(2)
