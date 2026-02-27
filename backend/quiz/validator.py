import re
from sklearn.metrics.pairwise import cosine_similarity
from quiz.semantic import semantic_similarity
from core.llm import embeddings


# =====================================
# TEXT CLEANING
# =====================================

def clean_text(text: str):

    if not text:
        return ""

    text = text.lower()

    # remove prefixes LLM may add
    text = re.sub(r"correct answer[:\-]*", "", text)

    # remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    return " ".join(text.split())


# =====================================
# SEMANTIC SIMILARITY
# =====================================

def semantic_similarity(a: str, b: str):

    try:
        emb_a = embeddings.embed_query(a)
        emb_b = embeddings.embed_query(b)

        similarity = cosine_similarity(
            [emb_a],
            [emb_b]
        )[0][0]

        return similarity

    except Exception as e:
        print("Embedding error:", e)
        return 0


# =====================================
# MAIN VALIDATOR
# =====================================

def validate_answer(user, correct, qtype):

    if not user:
        return False

    # ------------------
    # MCQ / TRUE FALSE
    # ------------------
    if qtype in ["MCQ", "True/False"]:
        return bool(
            user.strip().lower()
            == correct.strip().lower()
        )

    # ------------------
    # SHORT ANSWER
    # ------------------
    similarity = semantic_similarity(user, correct)

    print("Similarity:", similarity)

    # ⭐ FORCE PYTHON BOOL
    return bool(similarity >= 0.65)