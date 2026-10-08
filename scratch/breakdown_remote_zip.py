import urllib.request
import io
import zipfile
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

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

try:
    remote_io = RemoteZipFile(url)
    zf = zipfile.ZipFile(remote_io)
    namelist = zf.namelist()
    
    counts_by_top_folder = defaultdict(int)
    for n in namelist:
        parts = n.strip('/').split('/')
        if len(parts) >= 2:
            counts_by_top_folder[parts[1]] += 1

    print("Counts by second-level folder:")
    for k, v in counts_by_top_folder.items():
        print(f"  episam_dataset/{k}: {v} items")

    # Let's count images in episam_dataset/images or whole_images
    image_files = [n for n in namelist if any(n.startswith(p) for p in ['episam_dataset/images', 'episam_dataset/whole_images']) and not n.endswith('/')]
    binary_files = [n for n in namelist if n.startswith('episam_dataset/binary_images') and not n.endswith('/')]
    char_files = [n for n in namelist if n.startswith('episam_dataset/chars') and not n.endswith('/')]
    assoc_files = [n for n in namelist if n.startswith('episam_dataset/associated_centroids_updated') and not n.endswith('/')]
    line_files = [n for n in namelist if n.startswith('episam_dataset/lines') and not n.endswith('/')]

    print(f"\nImages count: {len(image_files)}")
    print(f"Binary images count: {len(binary_files)}")
    print(f"Chars annotations count: {len(char_files)}")
    print(f"Associated centroids count: {len(assoc_files)}")
    print(f"Lines annotations count: {len(line_files)}")

    print("\nSample image files (first 10):")
    for f in image_files[:10]:
        print(" ", f)

    print("\nSample binary files (first 10):")
    for f in binary_files[:10]:
        print(" ", f)

    print("\nSample char files (first 10):")
    for f in char_files[:10]:
        print(" ", f)

    print("\nSample line files (first 10):")
    for f in line_files[:10]:
        print(" ", f)

except Exception as e:
    print("Error:", e)
