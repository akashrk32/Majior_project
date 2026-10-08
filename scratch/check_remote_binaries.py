import urllib.request
import io
import zipfile
import re
from pathlib import Path
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

remote_io = RemoteZipFile(url)
zf = zipfile.ZipFile(remote_io)
namelist = zf.namelist()

bin_entries = [n for n in namelist if 'episam_dataset/binary_images/' in n and not n.endswith('/')]
print(f"Total binary image entries in zip: {len(bin_entries)}")
for b in bin_entries[:10]:
    print(" ", b)
