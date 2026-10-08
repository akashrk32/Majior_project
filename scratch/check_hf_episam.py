import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_hf_repo(repo_id, repo_type='dataset'):
    endpoint = f"https://huggingface.co/api/{'datasets/' if repo_type=='dataset' else 'models/'}{repo_id}"
    req = urllib.request.Request(endpoint, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"=== HF {repo_type.upper()}: {repo_id} ===")
            print("ID:", data.get('id'))
            print("Last Modified:", data.get('lastModified'))
            print("Siblings/Files:")
            for s in data.get('siblings', []):
                print(" -", s.get('rfilename'))
    except Exception as e:
        print(f"Error querying {repo_id}: {e}")

check_hf_repo("keyfinder08/EpiSAM_Inscriptions_Dataset", "dataset")
check_hf_repo("keyfinder08/EpiSAM_Inscriptions_Project", "model")
