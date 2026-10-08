import urllib.request
import struct
import io
import zipfile
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
    print(f"Connecting to remote zip: {url} ...")
    remote_io = RemoteZipFile(url)
    print(f"File size: {remote_io.length / (1024*1024):.2f} MB")
    zf = zipfile.ZipFile(remote_io)
    namelist = zf.namelist()
    print(f"Total entries in episam_dataset.zip: {len(namelist)}")
    print("\nFirst 30 files in zip:")
    for n in namelist[:30]:
        print(" ", n)
    
    # Analyze directory structure in zip
    dirs = set()
    extensions = {}
    for n in namelist:
        ext = n.split('.')[-1].lower() if '.' in n else 'dir'
        extensions[ext] = extensions.get(ext, 0) + 1
        parts = n.split('/')
        if len(parts) > 1:
            dirs.add(parts[0] + '/' + (parts[1] if len(parts) > 2 else ''))

    print("\nTop directories in zip:")
    for d in sorted(dirs)[:25]:
        print(" ", d)

    print("\nExtensions in zip:")
    for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ext}: {count}")

except Exception as e:
    print("Error inspecting remote zip:", e)
