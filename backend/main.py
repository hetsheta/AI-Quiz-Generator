from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.cache import get_quiz, store_quiz
from quiz.semantic import is_semantically_correct
from rag.parser import parse_pdf
from quiz.generator import generate_quiz
from models.schemas import QuizRequest, SubmitRequest

app = FastAPI(title="RAG Quiz Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def resolve_full_answer(answer: str, options: list) -> str:
    """
    LLMs often return just a letter like "B" or "B)" as the answer.
    This resolves it to the full matching option text e.g. "B) When current is high."
    Falls back to the raw answer if no match found.
    """
    if not options or not answer:
        return answer

    answer_letter = answer.strip().rstrip(")").rstrip(".").upper()  # "B" or "B)" -> "B"

    for option in options:
        # Match options like "A) ...", "A. ...", "A ..."
        option_stripped = option.strip()
        if option_stripped and option_stripped[0].upper() == answer_letter:
            return option  # Return the full option string

    # If the answer already is a full option text
    if answer in options:
        return answer

    return answer  # Fallback


def normalize_for_comparison(text: str, options: list = None) -> str:
    """
    Reduce both user answer and stored answer to the same letter
    so comparison works regardless of whether text is "B" or "B) full text".
    """
    if not text:
        return ""
    text = text.strip()
    if options:
        # If text matches a full option, extract its leading letter
        for option in options:
            if text == option and option.strip():
                return option.strip()[0].upper()
        # If text is already just a letter (possibly with ) or .)
        cleaned = text.rstrip(")").rstrip(".").strip()
        if len(cleaned) == 1 and cleaned.isalpha():
            return cleaned.upper()
    return text.lower()


@app.post("/parse-document")
async def parse_document(file: UploadFile = File(...)):
    await parse_pdf(file)
    return {"status": "success"}


@app.post("/generate-quiz")
async def generate(request: QuizRequest):
    quiz = await generate_quiz(request)
    quiz_id = store_quiz(quiz)

    # Send questions + options to frontend, but NOT answers/explanations
    questions_for_client = []
    for q in quiz["questions"]:
        client_q = {"question": q["question"]}
        if "options" in q:
            client_q["options"] = q["options"]
        questions_for_client.append(client_q)

    return {
        "quiz_id": quiz_id,
        "questions": questions_for_client
    }


@app.post("/submit-quiz")
async def submit(request: SubmitRequest):
    quiz = get_quiz(request.quiz_id)

    if not quiz:
        return JSONResponse(
            status_code=404,
            content={"error": "Quiz not found or expired. Please generate a new quiz."}
        )

    stored_questions = quiz["questions"]
    score = 0
    results = []

    for item in request.answers:
        i = item.question_index
        if i >= len(stored_questions):
            continue

        stored_q = stored_questions[i]
        raw_correct = stored_q["answer"]        # e.g. "B" or "B) full text"
        user_answer = item.user_answer          # e.g. "B) full option text" (what user clicked)
        options = stored_q.get("options", [])

        # Determine question type
        if options:
            if options == ["True", "False"]:
                question_type = "True/False"
            else:
                question_type = "MCQ"
        else:
            question_type = "Short Answer"

        # Resolve the FULL correct answer text for display
        if question_type == "MCQ":
            full_correct_answer = resolve_full_answer(raw_correct, options)
        else:
            full_correct_answer = raw_correct

        # ─── VALIDATION ───
        if question_type in ["MCQ", "True/False"]:
            user_norm = normalize_for_comparison(user_answer, options)
            correct_norm = normalize_for_comparison(raw_correct, options)

            # Letter match OR direct full-text match
            is_correct = (user_norm == correct_norm) or (
                user_answer.strip().lower() == full_correct_answer.strip().lower()
            )
            similarity = 1.0 if is_correct else 0.0

        else:
            is_correct, similarity = is_semantically_correct(user_answer, raw_correct)

        if is_correct:
            score += 1

        # Explanation from cache — zero extra API calls
        explanation = None
        if not is_correct:
            explanation = stored_q.get("explanation", "No explanation available.")

        results.append({
            "question": stored_q["question"],
            "user_answer": user_answer,
            "correct_answer": full_correct_answer,   # Full text, not just "B"
            "correct": bool(is_correct),
            "similarity_score": round(float(similarity), 3),
            "explanation": explanation,
            "concept": stored_q.get("concept", "")
        })

    return {
        "score": score,
        "total": len(results),
        "results": results
    }