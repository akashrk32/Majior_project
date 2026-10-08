from pathlib import Path
import json
import re

DATA_FILE = Path("pdf_dataset/old_kannada_dictionary.json")

data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

INDEX = {}


for item in data:
    word = item["word"].strip()

    if word not in INDEX:
        INDEX[word] = []

    INDEX[word].append(item)


def normalize(text):
    text = text.strip()
    text = re.sub(r"\s+", "", text)
    return text


def search_word(word):
    word = normalize(word)

    # Exact match
    if word in INDEX:
        return INDEX[word]

    # Partial match
    results = []

    for key, items in INDEX.items():
        if word in key:
            results.extend(items)

    return results[:20]