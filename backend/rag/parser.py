import tempfile
import os

from docling.document_converter import DocumentConverter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from core.config import CHUNK_SIZE, CHUNK_OVERLAP
from core.llm import embeddings
from rag.vector_store import save_db, set_db

from langchain_community.vectorstores import FAISS

converter = DocumentConverter()


async def parse_pdf(file):

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".pdf"
    ) as tmp:

        tmp.write(await file.read())
        path = tmp.name

    result = converter.convert(path)
    markdown = result.document.export_to_markdown()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    docs = []

    for chunk in splitter.split_text(markdown):
        docs.append(
            Document(
                page_content=chunk,
                metadata={"source": "document"}
            )
        )

    db = FAISS.from_documents(docs, embeddings)

    set_db(db)
    save_db(db)

    os.remove(path)

    return True