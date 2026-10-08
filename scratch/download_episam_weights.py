import urllib.request
import time
from pathlib import Path

dest = Path("e:/Brahmi-OCR-main/models/episam/episam.pth")
if dest.exists() and dest.stat().st_size > 300 * 1024 * 1024:
    print(f"episam.pth already exists ({dest.stat().st_size / (1024*1024):.2f} MB)")
else:
    url = "https://huggingface.co/keyfinder08/EpiSAM_Inscriptions_Project/resolve/main/episam.pth"
    print(f"Downloading episam.pth from {url} to {dest}...")
    t0 = time.time()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
        total = int(resp.headers.get('Content-Length', 0))
        downloaded = 0
        chunk_size = 1024 * 1024 * 2 # 2MB
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            pct = (downloaded / total * 100) if total else 0
            if downloaded % (1024 * 1024 * 20) < chunk_size: # print every ~20MB
                print(f"Progress: {downloaded / (1024*1024):.1f}/{total / (1024*1024):.1f} MB ({pct:.1f}%)")
    dt = time.time() - t0
    print(f"Download complete: {dest.stat().st_size / (1024*1024):.2f} MB in {dt:.1f}s")
