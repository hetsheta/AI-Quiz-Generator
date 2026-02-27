import os
from langchain_community.vectorstores import FAISS
from core.config import VECTOR_DB_PATH
from core.llm import embeddings

vector_db = None


def save_db(db):
    db.save_local(VECTOR_DB_PATH)


def load_db():
    global vector_db

    if os.path.exists(VECTOR_DB_PATH):
        vector_db = FAISS.load_local(
            VECTOR_DB_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    return vector_db


def set_db(db):
    global vector_db
    vector_db = db


def get_db():
    return vector_db