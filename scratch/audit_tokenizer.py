import os
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from transformers import TrOCRProcessor

root = Path(__file__).resolve().parent.parent
model_dir = root / "models" / "trocr" / "best_model"

processor = TrOCRProcessor.from_pretrained(str(model_dir))
tokenizer = processor.tokenizer

test_cases = {
    "archaic_characters": [
        ("ಱ", "U+0CB1 (KANNADA LETTER RRA)"),
        ("ೞ", "U+0CDE (KANNADA LETTER ARCHAIC LLA/ZHA)"),
        ("಼", "U+0CBC (KANNADA SIGN NUKTA)"),
        ("ಽ", "U+0CBD (KANNADA SIGN AVAGRAHA)"),
        ("ೠ", "U+0CE0 (KANNADA LETTER VOCALIC RR)"),
        ("ೡ", "U+0CE1 (KANNADA LETTER VOCALIC LL)"),
        ("ೱ", "U+0CF1 (KANNADA ARCHAIC UPADHMANIYA)"),
        ("ೲ", "U+0CF2 (KANNADA ARCHAIC JIHVAMULIYA)")
    ],
    "combining_marks_and_virama": [
        ("್", "U+0CCD (KANNADA SIGN VIRAMA)"),
        ("ಂ", "U+0C82 (KANNADA SIGN ANUSVARA)"),
        ("ಃ", "U+0C83 (KANNADA SIGN VISARGA)"),
        ("ಾ", "U+0CBE (VOWEL SIGN AA)"),
        ("ಿ", "U+0CBF (VOWEL SIGN I)"),
        ("ೀ", "U+0CC0 (VOWEL SIGN II)"),
        ("ು", "U+0CC1 (VOWEL SIGN U)"),
        ("ೂ", "U+0CC2 (VOWEL SIGN UU)"),
        ("ೃ", "U+0CC3 (VOWEL SIGN VOCALIC R)"),
        ("ೆ", "U+0CC6 (VOWEL SIGN E)"),
        ("ೇ", "U+0CC7 (VOWEL SIGN EE)"),
        ("ೈ", "U+0CC8 (VOWEL SIGN AI)"),
        ("ೊ", "U+0CCA (VOWEL SIGN O)"),
        ("ೋ", "U+0CCB (VOWEL SIGN OO)"),
        ("ೌ", "U+0CCC (VOWEL SIGN AU)")
    ],
    "consonants_and_conjuncts": [
        ("ಕ", "KA"),
        ("ಕ್ಕ", "KKA (geminate)"),
        ("ಕ್ಷ", "KSHA"),
        ("ಜ್ಞ", "JNYA"),
        ("ರ್ಮ್ಮ", "RM-MA (repha geminate)"),
        ("ಕಾಳಗದೊಳ್", "Kaalagadol (In battle)"),
        ("ಪೃಥ್ವೀರಾಜ್ಯಂ", "Prithvirajyam"),
        ("ಬಿದ್ದನ್", "Biddan (Fell)"),
        ("ಎಱೆಯಪ್ಪ", "Ereyappa (With archaic RRA)"),
        ("ಬೆಗೂಱ್", "Begoor (With archaic RRA + Virama)")
    ],
    "kannada_numerals": [
        ("೦೧೨೩೪೫೬೭೮೯", "Kannada digits 0-9"),
        ("೧೪೬೨", "Year 1462 in Kannada numerals")
    ]
}

report = {}
all_passed = True

print("=" * 60)
print("SHILORA TOKENIZER FORENSIC AUDIT (models/trocr/best_model)")
print("=" * 60)

for category, items in test_cases.items():
    print(f"\n--- Category: {category} ---")
    cat_results = []
    for text, desc in items:
        # Round trip
        tokens = tokenizer.encode(text, add_special_tokens=False)
        decoded = tokenizer.decode(tokens, skip_special_tokens=True)
        # Check byte-for-byte exact match
        exact_match = (decoded == text)
        if not exact_match:
            all_passed = False
        cat_results.append({
            "input": text,
            "description": desc,
            "token_ids": tokens,
            "decoded": decoded,
            "exact_match": exact_match,
            "input_codepoints": [f"U+{ord(c):04X}" for c in text],
            "decoded_codepoints": [f"U+{ord(c):04X}" for c in decoded]
        })
        status_str = "PASS" if exact_match else "FAIL"
        print(f"[{status_str}] {desc} : {text!r} -> tokens {tokens} -> decoded {decoded!r}")

    report[category] = cat_results

report["overall_summary"] = {
    "all_passed": all_passed,
    "model": "models/trocr/best_model",
    "tokenizer_class": tokenizer.__class__.__name__,
    "vocab_size": tokenizer.vocab_size
}

out_path = root / "reports" / "tokenizer_forensic_audit.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\nSaved tokenizer audit report to {out_path}")
