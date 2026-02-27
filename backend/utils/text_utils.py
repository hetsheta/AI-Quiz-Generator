import re

def normalize_answer(text: str):
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())