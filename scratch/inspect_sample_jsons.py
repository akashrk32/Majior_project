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
    
    # Read a character_polygons.json
    char_sample = "episam_dataset/chars/train/Jakkur 1000CE Kalnadu Inscription/character_polygons.json"
    with zf.open(char_sample) as f:
        data = json.load(f)
        print("=== Sample character_polygons.json ===")
        print(f"Keys count: {len(data)}")
        first_key = list(data.keys())[0]
        print(f"Sample item '{first_key}':")
        print(json.dumps(data[first_key], indent=2))

    # Read a line_polygons.json
    line_sample = "episam_dataset/lines/train/Jakkur 1000CE Kalnadu Inscription/line_polygons.json"
    with zf.open(line_sample) as f:
        data_line = json.load(f)
        print("\n=== Sample line_polygons.json ===")
        print(f"Keys count: {len(data_line)}")
        first_line_key = list(data_line.keys())[0]
        print(f"Sample line item '{first_line_key}':")
        print(json.dumps(data_line[first_line_key], indent=2))

    # Read an associations.json
    assoc_sample = "episam_dataset/associated_centroids_updated/train/Jakkur 1000CE Kalnadu Inscription_associations.json"
    with zf.open(assoc_sample) as f:
        data_assoc = json.load(f)
        print("\n=== Sample _associations.json ===")
        print(f"Keys count: {len(data_assoc)}")
        if isinstance(data_assoc, dict):
            first_assoc_key = list(data_assoc.keys())[0]
            print(f"Sample assoc item '{first_assoc_key}':")
            print(json.dumps(data_assoc[first_assoc_key], indent=2))
        elif isinstance(data_assoc, list):
            print("Sample assoc item 0:")
            print(json.dumps(data_assoc[0], indent=2))

except Exception as e:
    print("Error:", e)
