"""
SHILORA Grounded Epigraphical Translation & Linguistic Engine
=============================================================
Architecture: Deterministic Historical Linguistic Rule Engine & Verified Epigraphical Lexicon.
NOTE: This is NOT a trained AI neural translation model.
Translations are derived from verified external lexical datasets and historical morphological rules.

Components:
1. External Lexicon: data/translation/epigraphical_lexicon.json (Epigraphia Carnatica & Mythic Society)
2. Morphology Rules: data/translation/historical_morphology.json (Halegannada grammar cases)
3. Normalization Rules: data/translation/normalization_rules.json (Archaic RRA/LLA & repha gemination)
4. Unknown Lexeme Guard: Preserves raw unrecognized tokens as [UNKNOWN_HISTORICAL_TERM: <token>]
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TRANSLATION_DATA_DIR = Path("data/translation")
LEXICON_PATH = TRANSLATION_DATA_DIR / "epigraphical_lexicon.json"
MORPHOLOGY_PATH = TRANSLATION_DATA_DIR / "historical_morphology.json"
NORMALIZATION_PATH = TRANSLATION_DATA_DIR / "normalization_rules.json"

class ShiloraTranslationEngine:
    def __init__(self, data_dir: Optional[str] = None):
        base_dir = Path(data_dir) if data_dir else TRANSLATION_DATA_DIR
        lex_path = base_dir / "epigraphical_lexicon.json"
        morph_path = base_dir / "historical_morphology.json"
        norm_path = base_dir / "normalization_rules.json"

        if not lex_path.exists():
            raise FileNotFoundError(f"Missing external lexicon: {lex_path}")
        if not morph_path.exists():
            raise FileNotFoundError(f"Missing morphology rules: {morph_path}")
        if not norm_path.exists():
            raise FileNotFoundError(f"Missing normalization rules: {norm_path}")

        with open(lex_path, "r", encoding="utf-8") as f:
            lex_data = json.load(f)
            self.lexicon = lex_data["entries"]
            self.lexicon_meta = lex_data["metadata"]

        with open(morph_path, "r", encoding="utf-8") as f:
            morph_data = json.load(f)
            self.suffixes = morph_data["suffixes"]
            self.morphology_meta = morph_data["metadata"]

        with open(norm_path, "r", encoding="utf-8") as f:
            norm_data = json.load(f)
            self.archaic_mappings = norm_data["archaic_character_mappings"]
            self.geminate_rules = norm_data["geminate_rules"]
            self.normalization_meta = norm_data["metadata"]

    def normalize_old_kannada(self, text: str) -> str:
        """
        Applies deterministic orthographic normalization to archaic text
        WITHOUT corrupting the raw original transcription.
        """
        if not text:
            return ""
        norm = text
        for rule in self.archaic_mappings:
            norm = norm.replace(rule["source_character"], rule["target_character"])
        for g_rule in self.geminate_rules:
            norm = norm.replace(g_rule["pattern"], g_rule["normalized"])
        return norm

    def lookup_token(self, token: str) -> Dict[str, Any]:
        """
        Looks up an epigraphical token using external resources.
        Returns explicit provenance evidence for every translation decision.
        """
        clean_token = token.strip().strip(",.।॥;:-")
        if not clean_token:
            return None

        # 1. Exact match in external lexicon
        if clean_token in self.lexicon:
            entry = self.lexicon[clean_token].copy()
            entry["token"] = clean_token
            entry["source_type"] = "EXTERNAL_LEXICON_EXACT"
            entry["evidence_source"] = str(LEXICON_PATH)
            entry["is_unknown"] = False
            return entry

        # 2. Normalized match (e.g., archaic RRA/LLA mapped)
        norm_token = self.normalize_old_kannada(clean_token)
        if norm_token in self.lexicon:
            entry = self.lexicon[norm_token].copy()
            entry["token"] = clean_token
            entry["source_type"] = "EXTERNAL_LEXICON_NORMALIZED"
            entry["evidence_source"] = f"{NORMALIZATION_PATH} -> {LEXICON_PATH}"
            entry["is_unknown"] = False
            return entry

        # 3. Morphological suffix decomposition
        for s_rule in self.suffixes:
            s_old = s_rule["old_suffix"]
            if clean_token.endswith(s_old) and len(clean_token) > len(s_old):
                stem = clean_token[:-len(s_old)]
                stem_norm = self.normalize_old_kannada(stem)
                if stem in self.lexicon or stem_norm in self.lexicon:
                    stem_entry = self.lexicon.get(stem) or self.lexicon.get(stem_norm)
                    return {
                        "token": clean_token,
                        "transliteration": f"{stem_entry.get('transliteration', stem)}+{s_old}",
                        "modern_kannada": f"{stem_entry['modern_kannada']} {s_rule['modern_suffix']}",
                        "english": f"{s_rule['english_gloss']} {stem_entry['english']}",
                        "category": f"INFLECTED_{stem_entry.get('category', 'WORD')}",
                        "source_type": "DETERMINISTIC_MORPHOLOGICAL_RULE",
                        "evidence_source": f"{MORPHOLOGY_PATH} (Case: {s_rule['case']}) + {LEXICON_PATH}",
                        "is_unknown": False
                    }

        # 4. Numerals (Kannada / Indo-Arabic digits)
        kannada_digits = "೦೧೨೩೪೫೬೭೮೯"
        if any(ch in kannada_digits for ch in clean_token):
            digit_map = {k: str(v) for v, k in enumerate(kannada_digits)}
            arabic_num = "".join(digit_map.get(ch, ch) for ch in clean_token)
            return {
                "token": clean_token,
                "transliteration": arabic_num,
                "modern_kannada": f"ಸಂಖ್ಯೆ {arabic_num}",
                "english": f"Number / Year {arabic_num}",
                "category": "NUMERAL",
                "source_type": "NUMERAL_PARSER",
                "evidence_source": "KANNADA_NUMERAL_CONVERTER",
                "is_unknown": False
            }

        # 5. Unknown historical term (Tagged explicitly, NEVER hallucinated)
        return {
            "token": clean_token,
            "transliteration": clean_token,
            "modern_kannada": f"[ಅಜ್ಞಾತ ಐತಿಹಾಸಿಕ ಪದ: {clean_token}]",
            "english": f"[UNKNOWN_HISTORICAL_TERM: {clean_token}]",
            "category": "UNKNOWN_TERM",
            "source_type": "UNRECOGNIZED_LEXEME",
            "evidence_source": "NO_MATCHING_LEXICON_OR_MORPHOLOGY",
            "is_unknown": True
        }

    def translate_inscription(self, raw_ocr_text: str) -> Dict[str, Any]:
        """
        Translates raw inscription text into Modern Kannada and English,
        preserving original raw OCR text and attaching transparent linguistic evidence.
        """
        if not raw_ocr_text or not raw_ocr_text.strip():
            return {
                "raw_ocr_text": "",
                "normalized_old_kannada": "",
                "translation_engine_type": "DETERMINISTIC_LINGUISTIC_ENGINE",
                "is_neural_translation_model": False,
                "modern_kannada_translation": "",
                "english_translation": "",
                "total_tokens": 0,
                "recognized_tokens": 0,
                "lexical_coverage_ratio": 0.0,
                "unknown_terms": [],
                "glossary": [],
                "status": "EMPTY_INPUT"
            }

        tokens = raw_ocr_text.split()
        glosses = []
        mod_kannada_chunks = []
        english_chunks = []
        unknown_terms = []

        for token in tokens:
            entry = self.lookup_token(token)
            if not entry:
                continue
            glosses.append(entry)
            if entry["is_unknown"]:
                unknown_terms.append(token)
            mod_kannada_chunks.append(entry["modern_kannada"])
            english_chunks.append(entry["english"])

        mod_kannada_text = " ".join(mod_kannada_chunks)
        english_text = " ".join(english_chunks)


        total_cnt = len(tokens)
        rec_cnt = total_cnt - len(unknown_terms)
        coverage = round(rec_cnt / total_cnt, 4) if total_cnt > 0 else 0.0

        # Grounded factual summary based ONLY on evidenced tokens
        if rec_cnt > 0:
            identified_categories = set(g.get("category", "") for g in glosses if not g.get("is_unknown"))
            summary = f"Factual epigraphical reading: {rec_cnt}/{total_cnt} tokens grounded in verified historical lexicons. Identified semantic elements: {', '.join(sorted(identified_categories))}. No rulers, dates, land grants, or events have been invented beyond verified words."
        else:
            summary = "Fragmentary inscription: No recognized epigraphical terms identified in current OCR transcription. Historical interpretation withheld to prevent hallucination."

        return {
            "raw_ocr_text": raw_ocr_text,
            "normalized_old_kannada": self.normalize_old_kannada(raw_ocr_text),
            "translation_engine_type": "DETERMINISTIC_LINGUISTIC_ENGINE",
            "is_neural_translation_model": False,
            "provenance_statement": "Translation generated via verified epigraphical lexicons and deterministic Halegannada morphology rules. No AI translation model was trained.",
            "modern_kannada_translation": mod_kannada_text,
            "english_translation": english_text,
            "inscription_summary": summary,
            "total_tokens": total_cnt,
            "recognized_tokens": rec_cnt,
            "lexical_coverage_ratio": coverage,
            "unknown_terms": unknown_terms,
            "glossary": glosses,
            "status": "TRANSLATED" if rec_cnt > 0 else "UNKNOWN_HISTORICAL_TEXT"
        }

if __name__ == "__main__":
    engine = ShiloraTranslationEngine()
    print("ShiloraTranslationEngine initialized successfully:")
    print(f"  Lexicon entries loaded: {len(engine.lexicon)}")
    print(f"  Morphology suffixes loaded: {len(engine.suffixes)}")
    print(f"  Normalization rules loaded: {len(engine.archaic_mappings)}")

