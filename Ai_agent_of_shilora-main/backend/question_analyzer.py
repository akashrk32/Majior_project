from groq import Groq

from backend.config import GROQ_API_KEY, GROQ_MODEL


client = Groq(api_key=GROQ_API_KEY)


def analyze_question(message):

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
You are the intent analyzer for a general-purpose AI assistant.

Understand the user's INTENT, not simply the language they typed.

Return ONLY ONE:

DICTIONARY
CURRENT
GENERAL


DICTIONARY:

Use DICTIONARY when the user is asking for the meaning,
definition, or explanation of an Old Kannada dictionary word.

The user can write the word in:

- Kannada script
- English/Roman letters
- mixed Kannada + English
- informal Romanized Kannada

Examples:

ಒರೆ ಪದದ ಅರ್ಥ ಏನು?
ಒರೆ meaning
ore meaning
ore meaning in Kannada
what is the meaning of ore?
Tell me ore meaning
ಅಂಕುಶ meaning
ankusha meaning
ankusha meaning in Kannada
what does ankusha mean?
ankusha andre enu?
ankusha endare enu?


CURRENT:

Use CURRENT when the answer depends on information that can change.

Examples:

Who is the current PM of India?
Who is the current CM of Karnataka?
latest news
latest AI news
current price of gold
who won yesterday?
recent developments


GENERAL:

Everything else.

Examples:

What is AI?
Explain machine learning.
Write Python code.
Give me a project idea.
Solve this equation.
How does a car engine work?
Tell me a story.
Help me plan my project.
What is photosynthesis?


IMPORTANT:

The language of the question does NOT determine the category.

A Kannada question can be GENERAL.

An English question can be DICTIONARY.

A Romanized Kannada question can be DICTIONARY.

Return ONLY:

DICTIONARY
CURRENT
GENERAL
"""
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0
    )

    result = (
        response.choices[0]
        .message
        .content
        .strip()
        .upper()
    )

    if result not in {
        "DICTIONARY",
        "CURRENT",
        "GENERAL"
    }:
        return "GENERAL"

    return result