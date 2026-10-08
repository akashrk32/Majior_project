"""
SHILORA TrOCR Kannada Tokenizer Repair & Forensic Round-Trip Audit
==================================================================
Repairs the XLM-RoBERTa / RoBERTa byte-level BPE tokenizer to natively
support all Kannada Unicode characters, archaic letters, numerals,
vowel signs, viramas, and epigraphical glyphs without mapping to <unk>.

Outputs:
- reports/trocr_kannada_tokenizer_audit.json
- models/trocr/repaired_tokenizer/ (saved tokenizer & processor)
"""

import os
import sys
import json
import pandas as pd
from transformers import TrOCRProcessor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPORT_PATH = "reports/trocr_kannada_tokenizer_audit.json"
SAVED_TOKENIZER_DIR = "models/trocr/repaired_tokenizer"
METADATA_PATH = "data/trocr/metadata.csv"

def build_and_audit_repaired_tokenizer():
    print("=" * 70)
    print("SHILORA TOKENIZER REPAIR & FORENSIC AUDIT")
    print("=" * 70)

    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-stage1")
    tokenizer = processor.tokenizer
    orig_vocab_size = len(tokenizer)
    print(f"Original Tokenizer Vocab Size: {orig_vocab_size}")

    # 1. Collect all characters in metadata
    df = pd.read_csv(METADATA_PATH)
    metadata_chars = set()
    for text in df["text"].dropna():
        metadata_chars.update(list(str(text)))

    # 2. Kannada Unicode Block (U+0C80 to U+0CFF)
    kannada_block_chars = {chr(cp) for cp in range(0x0C80, 0x0D00)}

    # 3. Archaic / Historical / Epigraphical signs
    archaic_chars = {"ಱ", "ೞ", "಼", "ಽ", "ೠ", "ೡ", "ೲ", "ೱ", "॥", "।", "ᳲ", "ᳳ"}

    all_target_chars = sorted(list(metadata_chars.union(kannada_block_chars).union(archaic_chars)))

    # Find chars that tokenize to unk or split into multiple tokens
    tokens_to_add = []
    for ch in all_target_chars:
        enc = tokenizer(ch, add_special_tokens=False)["input_ids"]
        if len(enc) == 1 and enc[0] != tokenizer.unk_token_id:
            continue
        tokens_to_add.append(ch)

    print(f"Candidate characters to register: {len(tokens_to_add)}")
    added_count = tokenizer.add_tokens(tokens_to_add)
    new_vocab_size = len(tokenizer)
    print(f"Successfully added tokens: {added_count}")
    print(f"New Repaired Vocab Size:  {new_vocab_size}")

    # Save repaired processor/tokenizer
    os.makedirs(SAVED_TOKENIZER_DIR, exist_ok=True)
    processor.save_pretrained(SAVED_TOKENIZER_DIR)
    print(f"Repaired processor saved to: {SAVED_TOKENIZER_DIR}")

    # 4. Mandatory Test Suites
    test_suites = {
        "standard_consonants": [
            "ಕ", "ಖ", "ಗ", "ಘ", "ಙ",
            "ಚ", "ಛ", "ಜ", "ಝ", "ಞ",
            "ಟ", "ಠ", "ಡ", "ಢ", "ಣ",
            "ತ", "ಥ", "ದ", "ಧ", "ನ",
            "ಪ", "ಫ", "ಬ", "ಭ", "ಮ",
            "ಯ", "ರ", "ಲ", "ವ", "ಶ",
            "ಷ", "ಸ", "ಹ", "ಳ"
        ],
        "historical_archaic_characters": [
            "ಱ",  # Archaic Ra (Rre)
            "ೞ",  # Archaic Lla (Zha)
            "಼",  # Nukta
            "ಽ",  # Avagraha
            "ೠ",  # Vocalic Rr
            "ೡ",  # Vocalic Ll
            "ೲ",  # Upadhmaniya
            "ೱ"   # Jihvamuliya
        ],
        "kannada_numerals": [
            "೦", "೧", "೨", "೩", "೪", "೫", "೬", "೭", "೮", "೯"
        ],
        "vowel_signs_and_combining_marks": [
            "ಾ", "ಿ", "ೀ", "ು", "ೂ", "ೃ", "ೄ", "ೆ", "ೇ", "ೈ", "ೊ", "ೋ", "ೌ",
            "್",  # Virama
            "ಂ",  # Anusvara
            "ಃ"   # Visarga
        ],
        "compound_aksharas_and_ligatures": [
            "ಶ್ರೀ", "ಸ್ವಸ್ತಿ", "ಕ್ಷ", "ಜ್ಞ", "ತ್ರ್ಯ", "ರ್ದ್ಧ", "ರ್ಮ್ಮ", "ರ್ವ್ವ"
        ],
        "epigraphical_phrases": [
            "ಸ್ವಸ್ತಿ ಶ್ರೀ ಪೃಥ್ವೀರಾಜ್ಯಂಗೆಯ್ಯುತ್ತಮಿರೆ",
            "ಕಾಳಗದೊಳ್ ಬಿದ್ದನ್",
            "ಸಾಸಿರ್ವ್ವರ್ ಬ್ರಾಹ್ಮಣರ್",
            "ವಿಕ್ರಮಾದಿತ್ಯ ದೇವರ್",
            "ಧರ್ಮಕ್ಕೆ ಸಾಕ್ಷಿ"
        ]
    }

    test_results = {}
    overall_passed = True
    total_samples = 0
    total_preserved = 0

    print("\n--- RUNNING FORENSIC ROUND-TRIP AUDIT ---")
    for category, items in test_suites.items():
        cat_results = []
        for text in items:
            total_samples += 1
            encoded_ids = tokenizer(text, add_special_tokens=False)["input_ids"]
            unk_present = (tokenizer.unk_token_id in encoded_ids)
            decoded_text = tokenizer.decode(encoded_ids, skip_special_tokens=True)
            
            # Check preservation
            exact_match = (text == decoded_text)
            match_ignoring_spaces = (text.replace(" ", "") == decoded_text.replace(" ", ""))
            passed = (not unk_present) and (exact_match or match_ignoring_spaces)

            if passed:
                total_preserved += 1
            else:
                overall_passed = False

            cat_results.append({
                "original_text": text,
                "token_ids": encoded_ids,
                "unk_count": encoded_ids.count(tokenizer.unk_token_id),
                "decoded_text": decoded_text,
                "exact_match": exact_match,
                "passed": passed
            })
        test_results[category] = cat_results

    # Test all 95 test split lines from metadata
    test_split_lines = df[df["split"] == "test"]["text"].dropna().tolist()
    metadata_test_audit = []
    meta_unks = 0
    for line in test_split_lines:
        enc = tokenizer(line, add_special_tokens=False)["input_ids"]
        dec = tokenizer.decode(enc, skip_special_tokens=True)
        unk_count = enc.count(tokenizer.unk_token_id)
        if unk_count > 0:
            meta_unks += 1
        metadata_test_audit.append({
            "line": line,
            "unk_count": unk_count,
            "match": (line.replace(" ", "") == dec.replace(" ", ""))
        })

    audit_report = {
        "audit_name": "SHILORA TrOCR Kannada Tokenizer Forensic Audit",
        "timestamp": "2026-10-07T10:30:00Z",
        "original_vocab_size": orig_vocab_size,
        "tokens_added": added_count,
        "repaired_vocab_size": new_vocab_size,
        "archaic_ra_token_id": tokenizer("ಱ", add_special_tokens=False)["input_ids"],
        "archaic_lla_token_id": tokenizer("ೞ", add_special_tokens=False)["input_ids"],
        "total_audit_samples": total_samples,
        "total_preserved": total_preserved,
        "round_trip_preservation_rate": f"{(total_preserved / total_samples) * 100:.2f}%",
        "metadata_test_lines_evaluated": len(test_split_lines),
        "metadata_test_lines_with_unk": meta_unks,
        "metadata_test_unk_rate": f"{(meta_unks / max(1, len(test_split_lines))) * 100:.2f}%",
        "overall_status": "PASSED" if overall_passed and meta_unks == 0 else "FAILED",
        "test_categories": test_results
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2, ensure_ascii=False)

    print(f"\nAudit complete! Overall Status: {audit_report['overall_status']}")
    print(f"Preservation Rate: {audit_report['round_trip_preservation_rate']}")
    print(f"Test split UNK lines: {meta_unks} / {len(test_split_lines)}")
    print(f"Report saved to: {REPORT_PATH}")
    return audit_report

if __name__ == "__main__":
    build_and_audit_repaired_tokenizer()
