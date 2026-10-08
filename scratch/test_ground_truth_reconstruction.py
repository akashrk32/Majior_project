import sys
import json
import re
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

vowels_indep = {
    'a': 'ಅ', 'ā': 'ಆ', 'i': 'ಇ', 'ī': 'ಈ', 'u': 'ಉ', 'ū': 'ಊ', 'ṛ': 'ಋ', 'ṝ': 'ೠ',
    'ĕ': 'ಎ', 'e': 'ಏ', 'ē': 'ಏ', 'ai': 'ಐ', 'ŏ': 'ಒ', 'o': 'ಓ', 'ō': 'ಓ', 'au': 'ಔ'
}
matras = {
    'a': '', 'ā': 'ಾ', 'i': 'ಿ', 'ī': 'ೀ', 'u': 'ು', 'ū': 'ೂ', 'ṛ': 'ೃ', 'ṝ': 'ೄ',
    'ĕ': 'ೆ', 'e': 'ೇ', 'ē': 'ೇ', 'ai': 'ೈ', 'ŏ': 'ೊ', 'o': 'ೋ', 'ō': 'ೋ', 'au': 'ೌ'
}
consonants = {
    'kh': 'ಖ', 'k': 'ಕ', 'gh': 'ಘ', 'g': 'ಗ', 'ṅ': 'ಙ',
    'ch': 'ಛ', 'c': 'ಚ', 'jh': 'ಝ', 'j': 'ಜ', 'ñ': 'ಞ',
    'ṭh': 'ಠ', 'ṭ': 'ಟ', 'ḍh': 'ಢ', 'ḍ': 'ಡ', 'ṇa': 'ಣ', 'ṇ': 'ಣ',
    'th': 'ಥ', 't': 'ತ', 'dh': 'ಧ', 'd': 'ದ', 'na': 'ನ', 'n': 'ನ',
    'ph': 'ಫ', 'p': 'ಪ', 'bh': 'ಭ', 'b': 'ಬ', 'm': 'ಮ',
    'y': 'ಯ', 'ṟ': 'ಱ', 'r': 'ರ', 'l̤': 'ೞ', 'ḷ': 'ಳ', 'l': 'ಲ', 'v': 'ವ',
    'ś': 'ಶ', 'ṣ': 'ಷ', 's': 'ಸ', 'h': 'ಹ', 'ḻ': 'ೞ', 'zh': 'ೞ'
}
digits = {'0':'೦','1':'೧','2':'೨','3':'೩','4':'೪','5':'೫','6':'೬','7':'೭','8':'೮','9':'೯'}

def iast_to_kannada(tok):
    tok = tok.strip()
    if not tok or tok in ['NaNl', 'NaN', 'None', '?']:
        return '[?]'
    if tok in digits:
        return digits[tok]
    if tok in vowels_indep:
        return vowels_indep[tok]
    has_anusvara = tok.endswith('ṃ') or tok.endswith('ṃ') or tok.endswith('ṁ')
    if has_anusvara:
        tok = tok[:-1]
    has_visarga = tok.endswith('ḥ') or tok.endswith('ḥ')
    if has_visarga:
        tok = tok[:-1]
        
    vowel_found, vowel_str = None, ''
    for v in sorted(matras.keys(), key=lambda x: len(x), reverse=True):
        if tok.endswith(v):
            vowel_found = matras[v]
            vowel_str = v
            break
            
    if vowel_found is not None:
        cons_part = tok[:-len(vowel_str)]
    else:
        cons_part = tok
        vowel_found = '್'
        
    if not cons_part:
        res = vowels_indep.get(vowel_str, vowel_str)
    else:
        parts, rem = [], cons_part
        while rem:
            matched = False
            for c in sorted(consonants.keys(), key=lambda x: len(x), reverse=True):
                if rem.startswith(c):
                    parts.append(consonants[c])
                    rem = rem[len(c):]
                    matched = True
                    break
            if not matched:
                parts.append(rem[0])
                rem = rem[1:]
        if len(parts) == 1:
            res = parts[0] + vowel_found
        else:
            res = '್'.join(parts[:-1]) + '್' + parts[-1] + vowel_found
    if has_anusvara:
        res += 'ಂ'
    if has_visarga:
        res += 'ಃ'
    return res

chars_dir = Path('data/episam/ground_truth/episam_dataset/chars')
reconstructed_lines = []
stones_count = 0

for cf in chars_dir.rglob('character_polygons.json'):
    stones_count += 1
    st_name = cf.parent.name
    with open(cf, encoding='utf-8') as f:
        data = json.load(f)
    lines_dict = {}
    for k, v in data.items():
        ln = v.get('line_number')
        cn = v.get('char_number', 0)
        cname = v.get('char_name', '')
        if ln is not None and cname:
            if ln not in lines_dict:
                lines_dict[ln] = []
            lines_dict[ln].append((cn, cname))
    for ln in sorted(lines_dict.keys()):
        chars_sorted = sorted(lines_dict[ln], key=lambda x: x[0])
        kn_text = ''.join(iast_to_kannada(c[1]) for c in chars_sorted if c[1])
        reconstructed_lines.append({
            'stone': st_name,
            'line': ln,
            'num_chars': len(chars_sorted),
            'text': kn_text
        })

print(f"Total stones processed: {stones_count}")
print(f"Total reconstructed lines from character ground truth: {len(reconstructed_lines)}")
print(f"Total characters represented: {sum(r['num_chars'] for r in reconstructed_lines)}")

print("\nSample 15 Reconstructed Ground Truth Lines:")
for r in reconstructed_lines[:15]:
    st_short = r['stone'][:32]
    print(f"  {st_short:32s} L{r['line']:02d} ({r['num_chars']:2d} chars): {r['text'][:40]}")
