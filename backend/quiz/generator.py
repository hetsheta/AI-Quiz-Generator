# import json
# import random
# import re

# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser

# from core.llm import llm
# from rag.retriever import retrieve_random_context


# # -----------------------------
# # OUTPUT FORMAT
# # -----------------------------
# def build_format(qtype):

#     if qtype == "MCQ":
#         return """
# {
#  "questions":[
#   {
#    "question":"",
#    "options":["A","B","C","D"],
#    "answer":"",
#    "explanation":"",
#    "concept":""
#   }
#  ]
# }
# """

#     if qtype == "True/False":
#         return """
# {
#  "questions":[
#   {
#    "question":"",
#    "options":["True","False"],
#    "answer":"",
#    "explanation":"",
#    "concept":""
#   }
#  ]
# }
# """

#     return """
# {
#  "questions":[
#   {
#    "question":"",
#    "answer":"",
#    "explanation":"",
#    "concept":""
#   }
#  ]
# }
# """


# # -----------------------------
# # GENERATE QUIZ
# # -----------------------------
# async def generate_quiz(request):

#     # ✅ RANDOM CONTEXT FROM WHOLE PDF
#     context = retrieve_random_context()

#     seed = random.randint(1, 999999)

#     prompt = ChatPromptTemplate.from_template("""
# Random Seed: {seed}

# Generate EXACTLY {num_questions}
# {difficulty} {question_type} questions
# STRICTLY from DOCUMENT CONTENT ONLY.

# DO NOT create meta questions.
# DO NOT refer to instructions.
# DO NOT hallucinate.

# Return STRICT JSON ONLY.

# FORMAT:
# {format}

# Explanation rules:
# - explain why answer is correct
# - reference document idea
# - keep concise

# DOCUMENT:
# {context}
# """)

#     chain = prompt | llm | StrOutputParser()

#     raw = await chain.ainvoke({
#         "num_questions": request.num_questions,
#         "difficulty": request.difficulty,
#         "question_type": request.question_type,
#         "format": build_format(request.question_type),
#         "context": context,
#         "seed": seed
#     })

#     # ✅ clean markdown
#     cleaned = re.sub(r"```json|```", "", raw).strip()

#     quiz = json.loads(cleaned)

#     # ✅ shuffle questions every time
#     random.shuffle(quiz["questions"])

#     return quiz

import json
import random
import re
import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from core.llm import llm
from rag.retriever import retrieve_random_context

# Session-level memory: stores question strings already generated this run
# so the LLM is explicitly told not to repeat them
_generated_questions_history: list[str] = []


# -----------------------------
# OUTPUT FORMAT
# -----------------------------
def build_format(qtype):
    if qtype == "MCQ":
        return """
{
 "questions":[
  {
   "question":"...",
   "options":["A) ...", "B) ...", "C) ...", "D) ..."],
   "answer":"A) ...",
   "explanation":"...",
   "concept":"..."
  }
 ]
}
"""
    if qtype == "True/False":
        return """
{
 "questions":[
  {
   "question":"...",
   "options":["True","False"],
   "answer":"True",
   "explanation":"...",
   "concept":"..."
  }
 ]
}
"""
    return """
{
 "questions":[
  {
   "question":"...",
   "answer":"...",
   "explanation":"...",
   "concept":"..."
  }
 ]
}
"""


# -----------------------------
# GENERATE QUIZ
# -----------------------------
async def generate_quiz(request):
    global _generated_questions_history

    # Fresh random context — different chunks every call
    context = retrieve_random_context()

    # Hard entropy: timestamp + random int so every call is unique
    seed = random.randint(100000, 999999)
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")
    entropy_token = f"{seed}-{timestamp}"

    # Build "avoid these questions" block from history
    if _generated_questions_history:
        avoid_block = (
            "IMPORTANT — Do NOT generate any of these previously asked questions "
            "or anything closely similar to them:\n"
            + "\n".join(
                f"- {q}" for q in _generated_questions_history[-30:]  # last 30
            )
        )
    else:
        avoid_block = ""

    prompt = ChatPromptTemplate.from_template("""
Entropy token (use this to vary your output): {entropy_token}

{avoid_block}

Generate EXACTLY {num_questions} {difficulty} {question_type} questions
STRICTLY based on the DOCUMENT CONTENT provided below.

Rules:
- Every question MUST come from a DIFFERENT part of the document.
- DO NOT repeat or rephrase any previously asked question listed above.
- DO NOT create meta questions about the document itself.
- DO NOT refer to "the document" or "the text" in questions.
- DO NOT hallucinate facts not present in the document.
- For MCQ: the answer field MUST be the FULL option text (e.g. "A) When current is high"), NOT just the letter.
- Vary question styles: some factual, some conceptual, some application-based.

Return STRICT JSON ONLY — no markdown, no extra text.

FORMAT:
{format}

DOCUMENT CONTENT:
{context}
""")

    chain = prompt | llm | StrOutputParser()

    raw = await chain.ainvoke({
        "num_questions": request.num_questions,
        "difficulty": request.difficulty,
        "question_type": request.question_type,
        "format": build_format(request.question_type),
        "context": context,
        "entropy_token": entropy_token,
        "avoid_block": avoid_block,
    })

    # Clean markdown fences if present
    cleaned = re.sub(r"```json|```", "", raw).strip()

    quiz = json.loads(cleaned)

    # Shuffle questions
    random.shuffle(quiz["questions"])

    # Store generated questions in history to avoid future repeats
    for q in quiz["questions"]:
        question_text = q.get("question", "")
        if question_text and question_text not in _generated_questions_history:
            _generated_questions_history.append(question_text)

    # Keep history bounded to 100 questions
    if len(_generated_questions_history) > 100:
        _generated_questions_history = _generated_questions_history[-100:]

    return quiz