JAILBREAK_PATTERNS = [
    "ignore previous instructions",
    "developer mode",
    "system prompt",
    "act as",
    "pretend you are",
    "forget your role",
    "jailbreak",
]

def detect_jailbreak(text):

    text = text.lower()

    for pattern in JAILBREAK_PATTERNS:

        if pattern in text:
            return True

    return False
