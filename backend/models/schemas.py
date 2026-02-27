from pydantic import BaseModel
from typing import List


class QuizRequest(BaseModel):
    topic: str
    num_questions: int
    difficulty: str
    question_type: str


class AnswerItem(BaseModel):
    question_index: int
    user_answer: str


class SubmitRequest(BaseModel):
    quiz_id: str
    answers: List[AnswerItem]