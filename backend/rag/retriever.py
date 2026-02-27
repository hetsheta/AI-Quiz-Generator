# import random
# from rag.vector_store import get_db


# def retrieve_random_context(k: int = 8):
#     """
#     Retrieve random chunks from entire vector DB
#     """

#     db = get_db()

#     if db is None:
#         print("Vector DB not initialized")
#         return ""

#     # Get large candidate pool
#     docs = db.similarity_search(
#         "important concepts from document",
#         k=40
#     )

#     if not docs:
#         return ""

#     # Random sampling
#     sampled_docs = random.sample(
#         docs,
#         min(k, len(docs))
#     )

#     context = "\n\n".join(
#         doc.page_content for doc in sampled_docs
#     )

#     return context

import random
from rag.vector_store import get_db


# Pool of varied queries to hit different parts of the document each time
_QUERY_POOL = [
    "key definitions and terminology",
    "important concepts and principles",
    "examples and applications",
    "causes and effects",
    "processes and mechanisms",
    "facts and figures",
    "comparisons and differences",
    "rules and exceptions",
    "historical context and background",
    "formulas and equations",
    "advantages and disadvantages",
    "types and classifications",
    "problems and solutions",
    "experimental results and observations",
    "theories and hypotheses",
]


def retrieve_random_context(k: int = 8) -> str:
    """
    Retrieve truly random chunks from the vector DB by using
    different random search queries each call, ensuring different
    content is surfaced every time the quiz is generated.
    """
    db = get_db()

    if db is None:
        print("Vector DB not initialized")
        return ""

    # Pick 4 random distinct queries from the pool
    queries = random.sample(_QUERY_POOL, min(4, len(_QUERY_POOL)))

    seen_contents = set()
    all_docs = []

    for query in queries:
        try:
            docs = db.similarity_search(query, k=12)
            for doc in docs:
                # Deduplicate by first 80 chars of content
                key = doc.page_content[:80]
                if key not in seen_contents:
                    seen_contents.add(key)
                    all_docs.append(doc)
        except Exception as e:
            print(f"Retrieval error for query '{query}': {e}")

    if not all_docs:
        return ""

    # Randomly sample k chunks from the deduplicated pool
    sampled = random.sample(all_docs, min(k, len(all_docs)))

    # Shuffle order so context arrangement differs each time
    random.shuffle(sampled)

    return "\n\n---\n\n".join(doc.page_content for doc in sampled)