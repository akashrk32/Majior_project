import sys
import json
import pandas as pd
from transformers import TrOCRProcessor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-stage1")
tokenizer = processor.tokenizer

print("Initial vocab size:", len(tokenizer))

# Collect all unique characters from metadata
df = pd.read_csv("data/trocr/metadata.csv")
all_chars = set()
for text in df["text"].dropna():
    all_chars.update(list(str(text)))

# Also collect full Kannada Unicode block (0x0C80 to 0x0CFF)
kannada_chars = {chr(cp) for cp in range(0x0C80, 0x0D00)}
# Add specific historical characters if not in block
extra_chars = {"ಱ", "ೞ", "಼", "ಽ", "ೠ", "ೡ", "ೲ", "ೱ", "॥", "।"}
all_chars.update(kannada_chars)
all_chars.update(extra_chars)

# Remove chars already known (excluding unk)
tokens_to_add = []
for ch in sorted(list(all_chars)):
    # Check if single char tokenizes to a non-unk token
    encoded = tokenizer(ch, add_special_tokens=False)["input_ids"]
    if len(encoded) == 1 and encoded[0] != tokenizer.unk_token_id:
        continue
    tokens_to_add.append(ch)

print(f"Tokens to add: {len(tokens_to_add)}")
added_count = tokenizer.add_tokens(tokens_to_add)
print(f"Added tokens count: {added_count}")
print("New vocab size:", len(tokenizer))

# Test round-trip on diverse Kannada strings
test_strings = [
    "ಸ್ವಸ್ತಿ ಶ್ರೀ ಪೃಥ್ವೀರಾಜ್ಯಂಗೆಯ್ಯುತ್ತಮಿರೆ",
    "೧೨೩೪೫೬೭೮೯೦",
    "ಕ ಖ ಗ ಘ ಙ ಚ ಛ ಜ ಝ ಞ",
    "ಟ ಠ ಡ ಢ ಣ ತ ಥ ದ ಧ ನ",
    "ಪ ಫ ಬ ಭ ಮ ಯ ರ ಲ ವ ಶ",
    "ಷ ಸ ಹ ಳ ಱ ೞ",
    "ಕಾ ಕಿ ಕೀ ಕು ಕೂ ಕೃ ಕೆ ಕೇ ಕೈ ಕೊ ಕೋ ಕೌ ಕಂ ಕಃ ಕ್",
    "ಬಿದ್ದನ್ ಕಾಳಗದೊಳ್ ಸಾಸಿರ್ವ್ವರ್"
]

all_passed = True
for s in test_strings:
    ids = tokenizer(s)["input_ids"]
    unk_count = ids.count(tokenizer.unk_token_id)
    decoded = tokenizer.decode(ids, skip_special_tokens=True)
    # Check if decoded matches s (ignoring space differences that sentencepiece might have)
    match = (s == decoded) or (s.replace(" ", "") == decoded.replace(" ", ""))
    print(f"Orig:    {s}")
    print(f"Decoded: {decoded}")
    print(f"Unks:    {unk_count} | Match: {match}")
    if unk_count > 0:
        all_passed = False
    print("-" * 40)

print("All tests passed without UNK:", all_passed)
