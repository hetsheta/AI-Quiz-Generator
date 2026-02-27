import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ✅ Load once globally
model = SentenceTransformer("all-MiniLM-L6-v2")


def normalize(text: str) -> str:
    """
    Normalize answers before comparison
    """

    if not text:
        return ""

    text = text.lower().strip()

    # remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # remove filler words
    text = re.sub(
        r"\b(from|the|a|an|is|are|was|were|to|of)\b",
        "",
        text
    )

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def semantic_similarity(ans1: str, ans2: str) -> float:
    """
    Returns cosine similarity between answers
    """

    ans1 = normalize(ans1)
    ans2 = normalize(ans2)

    if not ans1 or not ans2:
        return 0.0

    emb1 = model.encode([ans1])[0]
    emb2 = model.encode([ans2])[0]

    score = cosine_similarity(
        [emb1],
        [emb2]
    )[0][0]

    return float(score)


def is_semantically_correct(
    user_answer: str,
    correct_answer: str,
    threshold: float = 0.50
):
    """
    Final validation logic
    """

    similarity = semantic_similarity(
        user_answer,
        correct_answer
    )

    return similarity >= threshold, similarity