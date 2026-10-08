import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect_hf_files(repo_id, repo_type='dataset'):
    url = f"https://huggingface.co/api/{'datasets/' if repo_type=='dataset' else 'models/'}{repo_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"=== {repo_id} ===")
        for s in data.get('siblings', []):
            fn = s.get('rfilename')
            # get file size via HEAD request
            dl_url = f"https://huggingface.co/{'datasets/' if repo_type=='dataset' else ''}{repo_id}/resolve/main/{fn}"
            head_req = urllib.request.Request(dl_url, headers={'User-Agent': 'Mozilla/5.0'})
            head_req.get_method = lambda: 'HEAD'
            try:
                with urllib.request.urlopen(head_req) as h_resp:
                    size = h_resp.headers.get('Content-Length')
                    size_mb = float(size) / (1024*1024) if size else 0
                    print(f"  {fn}: {size_mb:.2f} MB ({dl_url})")
            except Exception as e:
                print(f"  {fn}: (head error {e})")

inspect_hf_files("keyfinder08/EpiSAM_Inscriptions_Dataset", "dataset")
inspect_hf_files("keyfinder08/EpiSAM_Inscriptions_Project", "model")
