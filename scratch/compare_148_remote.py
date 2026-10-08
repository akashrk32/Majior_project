import re
import urllib.request
import io
import zipfile
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Read local 148 filenames
ks_dir = Path("e:/Brahmi-OCR-main/kannada_stones")
pattern_39 = re.compile(r"^stone_kn_0000(0[1-9]|[1-3][0-9])\.jpg$", re.IGNORECASE)
local_148 = sorted([f.name for f in ks_dir.iterdir() if not pattern_39.match(f.name)])

# Read remote zip file names
url = "https://huggingface.co/datasets/keyfinder08/EpiSAM_Inscriptions_Dataset/resolve/main/episam_dataset.zip"

class RemoteZipFile(io.RawIOBase):
    def __init__(self, url):
        self.url = url
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        req.get_method = lambda: 'HEAD'
        with urllib.request.urlopen(req) as resp:
            self.length = int(resp.headers['Content-Length'])
        self.pos = 0

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.pos = offset
        elif whence == io.SEEK_CUR:
            self.pos += offset
        elif whence == io.SEEK_END:
            self.pos = self.length + offset
        return self.pos

    def tell(self):
        return self.pos

    def read(self, size=-1):
        if size == -1:
            size = self.length - self.pos
        if size <= 0:
            return b""
        end = min(self.pos + size - 1, self.length - 1)
        req = urllib.request.Request(self.url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Range': f'bytes={self.pos}-{end}'
        })
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
        self.pos += len(data)
        return data

remote_io = RemoteZipFile(url)
zf = zipfile.ZipFile(remote_io)
namelist = zf.namelist()

# Remote images
remote_images = [Path(n).name for n in namelist if 'episam_dataset/images/' in n and not n.endswith('/')]
print(f"Total local non-39 images in kannada_stones: {len(local_148)}")
print(f"Total remote images in episam_dataset/images: {len(remote_images)}")

def normalize_name(s):
    # normalize spaces, underscores, lowercase, punctuation
    s = Path(s).stem.lower()
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

local_norm = {normalize_name(f): f for f in local_148}
remote_norm = {normalize_name(f): f for f in remote_images}

common = set(local_norm.keys()) & set(remote_norm.keys())
only_local = set(local_norm.keys()) - set(remote_norm.keys())
only_remote = set(remote_norm.keys()) - set(local_norm.keys())

print(f"Exact normalized matches between local 148 and remote EpiSAM: {len(common)}")
print(f"Only local: {len(only_local)}")
for k in list(only_local)[:10]:
    print("  Local:", local_norm[k])

print(f"Only remote: {len(only_remote)}")
for k in list(only_remote)[:10]:
    print("  Remote:", remote_norm[k])
