import re

from backend.dictionary_search import INDEX, search_word
from backend.web_search import web_search


CURRENT_KEYWORDS = [
    "current",
    "today",
    "latest",
    "now",
    "recent",
    "news",
    "currently",
    "ಈಗಿನ",
    "ಪ್ರಸ್ತುತ",
    "ಇತ್ತೀಚಿನ",
    "ಇಂದು",
    "ಸುದ್ದಿ",
]


DICTIONARY_PATTERNS = [
    r"(.+?)\s+ಪದದ\s+ಅರ್ಥ",
    r"(.+?)\s+ಎಂದರೇನು",
    r"(.+?)\s+ಎಂದರೆ\s+ಏನು",
    r"(.+?)\s+ಅರ್ಥ\s+ಏನು",
    r"(.+?)\s+ಅರ್ಥವೇನು",
]


def extract_dictionary_word(message):
    for pattern in DICTIONARY_PATTERNS:
        match = re.search(pattern, message)

        if match:
            candidate = match.group(1).strip()

            candidate = re.sub(
                r"(ಹಳೆಗನ್ನಡ|ಹಳೆಯಗನ್ನಡ|ಪದ)\s*$",
                "",
                candidate
            ).strip()

            if candidate in INDEX:
                return candidate

    if message.strip() in INDEX:
        return message.strip()

    return None


def classify_question(message):
    """
    Returns:
    dictionary
    current
    general
    """

    dictionary_word = extract_dictionary_word(message)

    if dictionary_word:
        return "dictionary"

    lower_message = message.lower()

    for keyword in CURRENT_KEYWORDS:
        if keyword.lower() in lower_message:
            return "current"

    return "general"


def route_question(message):
    question_type = classify_question(message)

    if question_type == "dictionary":
        word = extract_dictionary_word(message)

        return {
            "type": "dictionary",
            "word": word,
            "results": search_word(word)
        }

    if question_type == "current":
        return {
            "type": "current",
            "results": web_search(message)
        }

    return {
        "type": "general",
        "results": []
    }