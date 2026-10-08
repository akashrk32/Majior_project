import csv
import json
import re
from pathlib import Path
import unicodedata
import sys

sys.stdout.reconfigure(encoding='utf-8')

root = Path("e:/Brahmi-OCR-main")
reports_dir = root / "reports"
reports_dir.mkdir(parents=True, exist_ok=True)

# 1. Generate reports/dataset_candidates.csv
candidates = [
    {
        "name": "Mythic Society Akshara Bhandara Archive",
        "url": "https://mythicsociety.github.io/AksharaBhandara/",
        "organization": "The Mythic Society Bengaluru (Inscriptions 3D Digital Conservation)",
        "license": "Public Open Research / Cultural Heritage",
        "language": "Kannada / Halegannada",
        "script": "Historical Kannada Epigraphical Script",
        "historical_period": "300 CE - 1850 CE (Kadamba, Ganga, Hoysala, Vijayanagara)",
        "images": "1,500+ 3D photogrammetric stone inscription images",
        "masks": "Character polygons and centroids",
        "transcriptions": "Expert line-level and sentence-level readings",
        "translations": "Select modern Kannada and English summaries",
        "size": "~10 GB (Web Archive)",
        "relevance": "CRITICAL / PRIMARY",
        "allowed_for_training": "TRUE",
        "reason": "Direct provenance of the 148 stone inscription dataset"
    },
    {
        "name": "Mythic Society KannadaTools Transcription Corpus",
        "url": "https://github.com/mythicsociety/KannadaTools",
        "organization": "The Mythic Society Bengaluru",
        "license": "MIT / Open Research",
        "language": "Old Kannada / Medieval Kannada",
        "script": "Kannada Unicode",
        "historical_period": "750 CE - 1850 CE",
        "images": "Referenced by Inscription_Name",
        "masks": "None in repo",
        "transcriptions": "5,397 expert epigraphic reading lines across 160 inscriptions",
        "translations": "Partial word-level glosses",
        "size": "264 KB (.xlsx)",
        "relevance": "CRITICAL / PRIMARY",
        "allowed_for_training": "TRUE",
        "reason": "Direct expert line-level Kannada Unicode ground-truth readings matching our stones"
    },
    {
        "name": "EpiSAM Inscriptions Dataset (ICDAR 2026)",
        "url": "https://huggingface.co/datasets/keyfinder08/EpiSAM_Inscriptions_Dataset",
        "organization": "IHDIA, CVIT, IIIT Hyderabad",
        "license": "Apache 2.0 / CC-BY-4.0",
        "language": "Old Kannada",
        "script": "Historical Kannada & Transliteration",
        "historical_period": "450 CE - 1800 CE",
        "images": "148 original images + 150 binarized images",
        "masks": "148 character polygon sets + 1,314 line masks",
        "transcriptions": "Character-level phonetic labels (char_name)",
        "translations": "None",
        "size": "385 MB (.zip)",
        "relevance": "CRITICAL / PRIMARY",
        "allowed_for_training": "TRUE",
        "reason": "Official character and line instance segmentation ground truth"
    },
    {
        "name": "Sanchaya Classical Kannada Digital Archive",
        "url": "https://sanchaya.net/",
        "organization": "Kannada Sanchaya / Open Knowledge Community",
        "license": "Creative Commons Attribution-ShareAlike",
        "language": "Halegannada / Classical Kannada",
        "script": "Kannada Unicode",
        "historical_period": "9th - 14th Century (Pampa, Ranna, Janna, Ponna)",
        "images": "None (Text corpus)",
        "masks": "None",
        "transcriptions": "Complete classical literature texts (Kavirajamarga, Vikramarjuna Vijaya)",
        "translations": "Partial modern commentaries",
        "size": "50+ MB (Text)",
        "relevance": "HIGH (Language Modeling & Tokenizer Coverage)",
        "allowed_for_training": "TRUE (Tokenizer / Vocabulary only)",
        "reason": "Establishes authoritative Halegannada lexical distribution; not stone ground truth"
    },
    {
        "name": "Epigraphia Carnatica Volumes (I - XII)",
        "url": "https://archive.org/details/epigraphiacarnat00rice",
        "organization": "Mysore Archaeological Department (B. Lewis Rice)",
        "license": "Public Domain",
        "language": "Old Kannada / Sanskrit",
        "script": "Kannada Script / Roman Transliteration",
        "historical_period": "300 CE - 1800 CE",
        "images": "Lithographic plates & stone drawings",
        "masks": "None",
        "transcriptions": "Full text transcriptions of thousands of Karnataka inscriptions",
        "translations": "English epigraphical translations & historical summaries",
        "size": "12 Multi-volume PDFs",
        "relevance": "HIGH (Translation Ground Truth & Verification)",
        "allowed_for_training": "TRUE (Translation Ground Truth)",
        "reason": "Authoritative historical translations of inscriptions matching the Mythic Society collection"
    },
    {
        "name": "Kittel's Kannada-English Dictionary (Historical & Classical)",
        "url": "https://archive.org/details/kannadaenglishdi00kittuoft",
        "organization": "Reverend F. Kittel / Basel Mission Press",
        "license": "Public Domain",
        "language": "Old Kannada, Medieval Kannada, Modern Kannada",
        "script": "Kannada Unicode / Romanized",
        "historical_period": "Classical to 19th Century",
        "images": "None (Lexicon)",
        "masks": "None",
        "transcriptions": "Lexical headwords with etymology",
        "translations": "English and Modern Kannada definitions",
        "size": "1,750+ pages (Digital Lexicon)",
        "relevance": "CRITICAL (Translation Knowledge Base)",
        "allowed_for_training": "TRUE (Lexicon Lookup)",
        "reason": "The foundational dictionary documenting Old Kannada (Halegannada) vocabulary"
    }
]

candidates_csv = reports_dir / "dataset_candidates.csv"
cand_fields = [
    "name", "url", "organization", "license", "language", "script",
    "historical_period", "images", "masks", "transcriptions", "translations",
    "size", "relevance", "allowed_for_training", "reason"
]
with open(candidates_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=cand_fields)
    writer.writeheader()
    writer.writerows(candidates)
print(f"Generated {candidates_csv}")

