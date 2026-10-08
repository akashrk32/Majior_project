import sys

from backend.main import (
    general_answer,
    current_answer,
    dictionary_answer,
    clean_history
)
from backend.dictionary_resolver import resolve_dictionary_word
from backend.question_analyzer import analyze_question


def print_bot(text):
    print("\nAI:", text)
    print()


def main():

    print("=" * 60)
    print("                    AI CHATBOT")
    print("=" * 60)
    print()
    print("Type your question normally.")
    print("Type 'exit' or 'quit' to close.")
    print()

    history = []

    while True:

        try:
            message = input("You: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\n\nAI: Goodbye!")
            break

        if not message:
            continue

        if message.lower() in {
            "exit",
            "quit"
        }:
            print("\nAI: Goodbye!")
            break

        try:

            # ------------------------------------------------
            # DICTIONARY
            # ------------------------------------------------

            dictionary_word = resolve_dictionary_word(
                message
            )

            if dictionary_word:

                result = dictionary_answer(
                    message,
                    history
                )

                if result:

                    answer = result["answer"]

                    print_bot(answer)

                    history.append({
                        "role": "user",
                        "content": message
                    })

                    history.append({
                        "role": "assistant",
                        "content": answer
                    })

                    history = clean_history(
                        history
                    )

                    continue

            # ------------------------------------------------
            # INTENT ANALYSIS
            # ------------------------------------------------

            try:

                category = analyze_question(
                    message
                )

            except Exception:

                category = "GENERAL"

            # ------------------------------------------------
            # CURRENT
            # ------------------------------------------------

            if category == "CURRENT":

                result = current_answer(
                    message,
                    history
                )

                answer = result["answer"]

            # ------------------------------------------------
            # GENERAL
            # ------------------------------------------------

            else:

                answer = general_answer(
                    message,
                    history
                )

            # ------------------------------------------------
            # DISPLAY
            # ------------------------------------------------

            print_bot(answer)

            # ------------------------------------------------
            # SAVE CONVERSATION
            # ------------------------------------------------

            history.append({
                "role": "user",
                "content": message
            })

            history.append({
                "role": "assistant",
                "content": answer
            })

            history = clean_history(
                history
            )

        except Exception as error:

            print()
            print("AI: Sorry, something went wrong.")
            print(
                "    Error:",
                str(error)
            )
            print()


if __name__ == "__main__":
    main()