import uuid

# quiz_id → full quiz data (questions, answers, explanations all stored)
QUIZ_CACHE = {}


def store_quiz(quiz):
    quiz_id = str(uuid.uuid4())
    QUIZ_CACHE[quiz_id] = quiz
    return quiz_id


def get_quiz(quiz_id):
    return QUIZ_CACHE.get(quiz_id)