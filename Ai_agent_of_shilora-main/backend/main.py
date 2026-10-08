from fastapi import FastAPI
from pydantic import BaseModel, Field
from groq import Groq
import re

from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.question_analyzer import analyze_question
from backend.dictionary_search import search_word
from backend.dictionary_resolver import resolve_dictionary_word
from backend.web_search import web_search


app = FastAPI()

client = Groq(
    api_key=GROQ_API_KEY
)


class ChatRequest(BaseModel):

    message: str

    history: list[dict] = Field(
        default_factory=list
    )


# ---------------------------------------------------------
# HISTORY
# ---------------------------------------------------------

def clean_history(history):

    cleaned = []

    for item in history[-12:]:

        if not isinstance(item, dict):
            continue

        role = item.get("role")
        content = item.get("content")

        if role not in {
            "user",
            "assistant"
        }:
            continue

        if not isinstance(content, str):
            continue

        content = content.strip()

        if not content:
            continue

        cleaned.append({
            "role": role,
            "content": content
        })

    return cleaned


# ---------------------------------------------------------
# LANGUAGE REQUEST
# ---------------------------------------------------------

def detect_kannada_request(message: str):

    text = message.lower()

    english_patterns = [
        r"\bin kannada\b",
        r"\binto kannada\b",
        r"\bto kannada\b",
        r"\bkannada meaning\b",
        r"\bkannada translation\b",
        r"\btranslate.*kannada\b",
        r"\bmeaning.*kannada\b",
    ]

    for pattern in english_patterns:

        if re.search(
            pattern,
            text
        ):
            return True

    kannada_patterns = [
        "ಕನ್ನಡದಲ್ಲಿ",
        "ಕನ್ನಡಕ್ಕೆ",
        "ಕನ್ನಡದ",
        "ಕನ್ನಡ ಅರ್ಥ",
        "ಅನುವಾದಿಸಿ",
        "ಅನುವಾದ",
    ]

    return any(
        pattern in message
        for pattern in kannada_patterns
    )


# ---------------------------------------------------------
# GENERAL ANSWER
# ---------------------------------------------------------

def general_answer(
    message,
    history
):

    messages = [
        {
            "role": "system",
            "content": """
You are a highly capable general-purpose AI assistant.

Understand what the user actually wants.

DEFAULT LANGUAGE:

Answer in ENGLISH by default.

The language used by the user does NOT automatically determine
the answer language.

If the user explicitly asks for Kannada, answer in Kannada.

If the user asks to translate something into Kannada,
provide the Kannada translation.

If the user explicitly requests another language,
answer in that requested language.

RULES:

1. Answer exactly what the user asks.
2. Be concise by default.
3. Do not dump unnecessary information.
4. Match the requested level of detail.
5. Use conversation history for follow-up questions.
6. Do not mention internal tools, routing, APIs, or models.
7. If the user asks for code, provide the requested code.
8. If the user asks for an explanation, explain clearly.
9. Do not add unrelated information.
"""
        }
    ]

    messages.extend(
        clean_history(history)
    )

    messages.append({
        "role": "user",
        "content": message
    })

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.4
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# CURRENT INFORMATION
# ---------------------------------------------------------

def current_answer(
    message,
    history
):

    results = web_search(
        message,
        max_results=5
    )

    if not results:

        return {
            "answer": general_answer(
                message,
                history
            ),
            "sources": []
        }

    web_information = "\n\n".join(
        f"TITLE: {item['title']}\n"
        f"URL: {item['url']}\n"
        f"INFORMATION: {item['snippet']}"
        for item in results
    )

    messages = [
        {
            "role": "system",
            "content": """
You are a general-purpose AI assistant.

The user asked for current information.

Use the supplied web information to answer the
actual question.

DEFAULT LANGUAGE:

Answer in ENGLISH.

If the user explicitly asks for Kannada,
answer in Kannada.

If the user asks for translation into Kannada,
translate into Kannada.

RULES:

- Give one direct answer.
- Be concise.
- Do not dump every search result.
- Do not invent facts.
- If sources disagree, mention it briefly.
- Do not mention internal routing or implementation.
"""
        }
    ]

    messages.extend(
        clean_history(history)
    )

    messages.append({
        "role": "user",
        "content": (
            f"USER QUESTION:\n{message}\n\n"
            f"CURRENT WEB INFORMATION:\n"
            f"{web_information}"
        )
    })

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.2
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": results
    }


# ---------------------------------------------------------
# DICTIONARY ANSWER
# ---------------------------------------------------------

def dictionary_answer(
    message,
    history
):

    # IMPORTANT:
    #
    # ore -> ಒರೆ
    # ankusha -> ಅಂಕುಶ
    # ankush -> ಅಂಕುಶ
    # ಅಂಕುಶ -> ಅಂಕುಶ

    word = resolve_dictionary_word(
        message
    )

    if not word:
        return None

    results = search_word(
        word
    )

    if not results:
        return None

    # Combine meanings from the PDF.
    dictionary_information = "\n".join(
        f"{item['word']}: {item['meaning']}"
        for item in results
    )

    kannada_requested = detect_kannada_request(
        message
    )

    if kannada_requested:

        system_prompt = """
You are an Old Kannada dictionary assistant.

The user explicitly requested a Kannada meaning.

The supplied information is from the user's
Old Kannada dictionary PDF.

RULES:

1. Give ONLY the Kannada dictionary meaning.
2. Do NOT give a long explanation.
3. Do NOT give unrelated information.
4. Do NOT invent meanings.
5. Preserve all important meanings from the dictionary.
6. Do not translate the meaning into English unless the user
   also explicitly asks for English.
7. Keep the answer very concise.

Example:

User:
ankusha meaning in kannada

Answer:
ಆನೆಯನ್ನು ನಿಯಂತ್ರಿಸುವ ಆಯುಧ, ಸೃಣಿ
"""

    else:

        system_prompt = """
You are an Old Kannada dictionary assistant.

The supplied information is from the user's
Old Kannada dictionary PDF.

RULES:

1. Give the Kannada dictionary meaning FIRST.
2. Then give a short English meaning if it can be accurately
   understood from the supplied Kannada meaning.
3. Keep the answer concise.
4. Do not invent meanings.
5. Do not add unrelated information.

Example:

User:
ankusha meaning

Answer:

ಆನೆಯನ್ನು ನಿಯಂತ್ರಿಸುವ ಆಯುಧ, ಸೃಣಿ

English: An instrument used to control an elephant.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # Do NOT send previous conversation into dictionary
    # answer generation because it can cause the model to
    # mix meanings from previous words.

    messages.append({
        "role": "user",
        "content": (
            f"WORD:\n{word}\n\n"
            f"DICTIONARY:\n{dictionary_information}\n\n"
            f"QUESTION:\n{message}"
        )
    })

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.0
    )

    return {
        "word": word,
        "answer": response.choices[0].message.content.strip(),
        "source": results
    }


# ---------------------------------------------------------
# CHAT
# ---------------------------------------------------------

@app.post("/chat")
def chat(
    request: ChatRequest
):

    message = request.message.strip()

    if not message:

        return {
            "type": "error",
            "answer": "Please enter a question."
        }

    history = clean_history(
        request.history
    )

    # -----------------------------------------------------
    # STEP 1:
    # Try local dictionary detection FIRST.
    #
    # This means:
    #
    # ankusha meaning
    # ore meaning
    #
    # do not depend on the LLM analyzer.
    # -----------------------------------------------------

    dictionary_word = resolve_dictionary_word(
        message
    )

    if dictionary_word:

        result = dictionary_answer(
            message,
            history
        )

        if result:

            return {
                "type": "dictionary",
                "word": result["word"],
                "answer": result["answer"],
                "source": result["source"]
            }

    # -----------------------------------------------------
    # STEP 2:
    # Use LLM intent analyzer for everything else.
    # -----------------------------------------------------

    try:

        category = analyze_question(
            message
        )

    except Exception:

        category = "GENERAL"

    if category not in {
        "DICTIONARY",
        "CURRENT",
        "GENERAL"
    }:

        category = "GENERAL"

    # -----------------------------------------------------
    # DICTIONARY FALLBACK
    # -----------------------------------------------------

    if category == "DICTIONARY":

        result = dictionary_answer(
            message,
            history
        )

        if result:

            return {
                "type": "dictionary",
                "word": result["word"],
                "answer": result["answer"],
                "source": result["source"]
            }

        return {
            "type": "general",
            "answer": general_answer(
                message,
                history
            )
        }

    # -----------------------------------------------------
    # CURRENT
    # -----------------------------------------------------

    if category == "CURRENT":

        result = current_answer(
            message,
            history
        )

        return {
            "type": "current",
            "answer": result["answer"],
            "sources": result["sources"]
        }

    # -----------------------------------------------------
    # GENERAL
    # -----------------------------------------------------

    return {
        "type": "general",
        "answer": general_answer(
            message,
            history
        )
    }


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.get("/")
def home():

    return {
        "status": "AI Chatbot backend is running",
        "model": GROQ_MODEL
    }