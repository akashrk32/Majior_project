import urllib.request
import io
import zipfile
import json
import sys

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
    
    char_jsons = [n for n in namelist if n.endswith('character_polygons.json')]
    print(f"Total character_polygons.json in dataset: {len(char_jsons)}")
    
    total_chars = 0
    all_char_names = set()
    stone_char_counts = {}
    
    for cj in char_jsons[:15]:
        with zf.open(cj) as f:
            data = json.load(f)
            stone_name = cj.split('/')[-2]
            stone_char_counts[stone_name] = len(data)
            total_chars += len(data)
            for k, v in data.items():
                all_char_names.add(v.get('char_name', ''))

    print(f"Sample 15 stones character counts: {stone_char_counts}")
    print(f"Total characters in these 15 stones: {total_chars}")
    print(f"Unique char_names in these 15 stones ({len(all_char_names)}): {sorted(list(all_char_names))[:40]}")

except Exception as e:
    print("Error:", e)
