"""Rule-based chatbot logic (if-elif + functions + loop). Standard library only.

Use it in the console:   python chatbot.py
Or through the web app:  python app.py
"""
import re
from datetime import datetime

EXIT_WORDS = ("bye", "goodbye", "exit", "quit")


def clean(message):
    """Lowercase the text and remove punctuation."""
    return re.sub(r"[^a-z0-9 ]", "", message.lower()).strip()


def is_exit(message):
    return clean(message) in EXIT_WORDS


def get_reply(message):
    """Return a predefined reply for the user's message."""
    text = clean(message)

    if text == "":
        return "Please type something."
    elif text in ("hello", "hi", "hey"):
        return "Hi!"
    elif text in ("how are you", "how are you doing", "how r u"):
        return "I'm fine, thanks!"
    elif text in EXIT_WORDS:
        return "Goodbye!"
    elif "your name" in text or "who are you" in text:
        return "I'm PyBot, a simple rule-based chatbot."
    elif "time" in text:
        return "It's " + datetime.now().strftime("%I:%M %p") + "."
    elif "thank" in text:
        return "You're welcome!"
    elif "help" in text:
        return "Try saying: hello, how are you, what's your name, what time is it, or bye."
    else:
        return "Sorry, I don't understand that. Type 'help' to see what I can do."


def main():
    print("PyBot: Hi! Type 'bye' to quit.")
    while True:
        message = input("You: ")
        print("PyBot:", get_reply(message))
        if is_exit(message):
            break


if __name__ == "__main__":
    main()
