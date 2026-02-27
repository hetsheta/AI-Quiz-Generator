from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from core.llm import llm
from rag.retriever import retrieve_random_context


# ==========================================
# EXPLANATION GENERATOR
# ==========================================

async def generate_explanation(
    question,
    correct_answer,
    user_answer,
    difficulty,
    is_correct
):

    # ✅ retrieve document context
    context = retrieve_random_context()

    prompt = ChatPromptTemplate.from_template("""
You are an expert teacher.

Explain the answer using the provided study material.

Difficulty Level: {difficulty}

QUESTION:
{question}

CORRECT ANSWER:
{correct}

USER ANSWER:
{user}

DOCUMENT CONTENT:
{context}

TASK:

1. Explain WHY the correct answer is correct.
2. If user answer is wrong:
   - Explain WHY it is incorrect.
3. Reference related concept from document.
4. Keep explanation suitable for {difficulty} level student.
5. Maximum 120 words.
6. Clear teaching tone.

Return ONLY explanation text.
""")

    chain = prompt | llm | StrOutputParser()

    explanation = await chain.ainvoke({
        "question": question,
        "correct": correct_answer,
        "user": user_answer,
        "difficulty": difficulty,
        "context": context,
    })

    return explanation.strip()