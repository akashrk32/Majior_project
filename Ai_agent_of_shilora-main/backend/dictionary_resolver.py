from pathlib import Path
import json
import re
import unicodedata

from indic_transliteration import sanscript


DATA_FILE = Path("pdf_dataset/old_kannada_dictionary.json")


# ---------------------------------------------------------
# LOAD DICTIONARY
# ---------------------------------------------------------

DATA = json.loads(
    DATA_FILE.read_text(encoding="utf-8")
)

KANNADA_WORDS = set(
    item["word"].strip()
    for item in DATA
    if item.get("word")
)


# ---------------------------------------------------------
# ROMAN NORMALIZATION
# ---------------------------------------------------------

def normalize_roman(text: str) -> str:

    text = text.lower().strip()

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = "".join(
        ch for ch in text
        if not unicodedata.combining(ch)
    )

    replacements = {
        "sh": "sh",
        "ṣ": "sh",
        "ś": "sh",
        "zh": "j",
        "aa": "a",
        "ee": "i",
        "ii": "i",
        "oo": "u",
        "uu": "u",
        "ou": "au",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"[^a-z0-9]",
        "",
        text
    )

    return text


# ---------------------------------------------------------
# ROMANIZATION VARIANTS
# ---------------------------------------------------------

def generate_roman_forms(word: str):

    forms = set()

    # ITRANS
    try:
        value = sanscript.transliterate(
            word,
            sanscript.KANNADA,
            sanscript.ITRANS
        )

        forms.add(value)

    except Exception:
        pass

    # HK
    try:
        value = sanscript.transliterate(
            word,
            sanscript.KANNADA,
            sanscript.HK
        )

        forms.add(value)

    except Exception:
        pass

    # SLP1
    try:
        value = sanscript.transliterate(
            word,
            sanscript.KANNADA,
            sanscript.SLP1
        )

        forms.add(value)

    except Exception:
        pass

    normalized = set()

    for form in forms:

        value = normalize_roman(form)

        if value:
            normalized.add(value)

    return normalized


# ---------------------------------------------------------
# BUILD ROMAN INDEX
# ---------------------------------------------------------

ROMAN_INDEX = {}


for word in KANNADA_WORDS:

    forms = generate_roman_forms(word)

    for form in forms:

        if form not in ROMAN_INDEX:
            ROMAN_INDEX[form] = set()

        ROMAN_INDEX[form].add(word)


# ---------------------------------------------------------
# MANUAL COMMON ROMAN FORMS
# ---------------------------------------------------------

# These are useful for casual English typing.
#
# They are NOT the meanings.
# They only help locate the Kannada dictionary word.

COMMON_FORMS = {
    "ore": "ಒರೆ",
    "ankusha": "ಅಂಕುಶ",
    "ankush": "ಅಂಕುಶ",
}


for roman, kannada in COMMON_FORMS.items():

    if kannada in KANNADA_WORDS:

        if roman not in ROMAN_INDEX:
            ROMAN_INDEX[roman] = set()

        ROMAN_INDEX[roman].add(kannada)


# ---------------------------------------------------------
# QUESTION CLEANING
# ---------------------------------------------------------

def clean_question(message: str):

    text = message.strip()

    # Remove common English dictionary phrases.
    patterns = [
        r"\bmeaning\s+in\s+kannada\b",
        r"\bmeaning\s+in\s+english\b",
        r"\bmeaning\b",
        r"\bwhat\s+is\s+the\s+meaning\s+of\b",
        r"\bwhat\s+does\b",
        r"\bwhat\s+is\b",
        r"\btell\s+me\b",
        r"\bdefine\b",
        r"\bdefinition\b",
        r"\bin\s+kannada\b",
        r"\bin\s+english\b",
        r"\bkannada\s+meaning\b",
        r"\benglish\s+meaning\b",
    ]

    for pattern in patterns:

        text = re.sub(
            pattern,
            " ",
            text,
            flags=re.IGNORECASE
        )

    # Remove common Kannada dictionary phrases.
    kannada_patterns = [
        "ಪದದ ಅರ್ಥ ಏನು",
        "ಪದದ ಅರ್ಥವೇನು",
        "ಪದದ ಅರ್ಥ",
        "ಅರ್ಥವೇನು",
        "ಅರ್ಥ ಏನು",
        "ಎಂದರೇನು",
        "ಎಂದರೆ ಏನು",
        "ಕನ್ನಡದಲ್ಲಿ",
        "ಕನ್ನಡಕ್ಕೆ",
        "ಕನ್ನಡ",
        "ಹಳೆಗನ್ನಡ",
        "ಹಳೆಯಗನ್ನಡ",
        "ಪದ",
    ]

    for pattern in kannada_patterns:

        text = text.replace(
            pattern,
            " "
        )

    text = re.sub(
        r"[?!.,;:]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ---------------------------------------------------------
# FIND KANNADA WORD
# ---------------------------------------------------------

def find_kannada_word(message: str):

    cleaned = clean_question(message)

    # Exact Kannada word.
    if cleaned in KANNADA_WORDS:
        return cleaned

    # Look through individual Kannada tokens.
    for token in cleaned.split():

        token = token.strip()

        if token in KANNADA_WORDS:
            return token

    return None


# ---------------------------------------------------------
# FIND ROMAN WORD
# ---------------------------------------------------------

def find_roman_word(message: str):

    cleaned = clean_question(message)

    tokens = re.findall(
        r"[A-Za-z]+",
        cleaned
    )

    # First try exact token.
    for token in tokens:

        normalized = normalize_roman(token)

        if normalized in ROMAN_INDEX:

            matches = ROMAN_INDEX[normalized]

            if len(matches) == 1:
                return next(iter(matches))

    # Try longer combinations if necessary.
    for token in sorted(
        tokens,
        key=len,
        reverse=True
    ):

        normalized = normalize_roman(token)

        if normalized in ROMAN_INDEX:

            matches = ROMAN_INDEX[normalized]

            if matches:
                return sorted(matches)[0]

    return None


# ---------------------------------------------------------
# PUBLIC RESOLVER
# ---------------------------------------------------------

def resolve_dictionary_word(message: str):

    # Kannada first.
    kannada_word = find_kannada_word(message)

    if kannada_word:
        return kannada_word

    # Romanized English typing.
    roman_word = find_roman_word(message)

    if roman_word:
        return roman_word

    return None