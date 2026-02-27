# 📚 AI Quiz Generator

A **Retrieval-Augmented Generation (RAG)** powered quiz application that automatically generates quizzes from your PDF documents using Google's Gemini AI. Upload any study material, and the app will produce contextually relevant questions, validate answers with semantic similarity, and provide AI-generated explanations.

---

## ✨ Features

- **PDF Ingestion** — Upload any PDF; it's parsed, chunked, and stored in a FAISS vector index
- **Dynamic Quiz Generation** — Generates MCQ, True/False, or Short Answer questions directly from document content
- **Anti-Repetition** — Tracks previously asked questions to avoid duplicates within a session
- **Smart Answer Validation** — Exact match for MCQ/True-False; semantic cosine similarity for short answers
- **AI Explanations** — Wrong answers trigger a contextual explanation pulled from the document
- **REST API** — Clean FastAPI endpoints, ready to connect to any frontend

---

## 🗂️ Project Structure

```
AI Quiz Generator/
│
├── backend/
│   ├── core/
│   │   ├── .env                   # Your secret API key (never committed)
│   │   ├── cache.py               # In-memory quiz session cache
│   │   ├── config.py              # Vector DB path + chunking config (no secrets)
│   │   └── llm.py                 # Gemini LLM + embeddings (loads API key from .env)
│   │
│   ├── faiss_index/               # Persisted FAISS vector store (auto-generated)
│   │
│   ├── feedback/
│   │   └── explainer.py           # LLM-based explanation generation
│   │
│   ├── models/
│   │   └── schemas.py             # Pydantic request/response schemas
│   │
│   ├── quiz/
│   │   ├── generator.py           # LLM-based quiz question generation
│   │   ├── semantic.py            # Sentence-transformer cosine similarity
│   │   └── validator.py           # Answer validation (exact + semantic)
│   │
│   ├── rag/
│   │   ├── parser.py              # PDF → markdown → FAISS chunks
│   │   ├── retriever.py           # Random diverse context retrieval
│   │   └── vector_store.py        # FAISS load/save/get/set helpers
│   │
│   ├── utils/
│   │   └── text_utils.py          # Text normalization utilities
│   │
│   └── main.py                    # FastAPI app + route handlers
│
├── frontend/
│   └── app.py                     # Streamlit frontend app
│
├── .gitignore
└── requirements.txt               # Backend dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10.7
- A Google AI API key from [https://aistudio.google.com](https://aistudio.google.com)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-quiz-generator.git
cd ai-quiz-generator
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Copy the example env file into `backend/core/` and add your Google AI API key:

```bash
cp .env.example backend/core/.env
```

Then open `backend/core/.env` and fill in your key:

```
GOOGLE_API_KEY=your-google-api-key-here
```

The key is loaded automatically by `core/llm.py` via `python-dotenv`. Never commit `.env` — it's already covered by `.gitignore`.

### 5. Run the backend server

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 6. Run the frontend

Open a new terminal:

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔌 API Endpoints

### `POST /parse-document`
Upload a PDF to build the vector index.

```
Content-Type: multipart/form-data
Body: file=<your_pdf>
```

**Response:**
```json
{ "status": "success" }
```

---

### `POST /generate-quiz`
Generate a quiz from the uploaded document.

**Request body:**
```json
{
  "topic": "Machine Learning",
  "num_questions": 5,
  "difficulty": "Medium",
  "question_type": "MCQ"
}
```

- `question_type`: `"MCQ"` | `"True/False"` | `"Short Answer"`
- `difficulty`: `"Easy"` | `"Medium"` | `"Hard"`

**Response:**
```json
{
  "quiz_id": "uuid-string",
  "questions": [
    {
      "question": "What is supervised learning?",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."]
    }
  ]
}
```

---

### `POST /submit-quiz`
Submit answers and receive scored results with explanations.

**Request body:**
```json
{
  "quiz_id": "uuid-string",
  "answers": [
    { "question_index": 0, "user_answer": "A) ..." },
    { "question_index": 1, "user_answer": "True" }
  ]
}
```

**Response:**
```json
{
  "score": 3,
  "total": 5,
  "results": [
    {
      "question": "...",
      "user_answer": "...",
      "correct_answer": "...",
      "correct": false,
      "similarity_score": 0.42,
      "explanation": "The correct answer is ... because ...",
      "concept": "..."
    }
  ]
}
```

---

## ⚙️ Configuration

### Environment Variables (`backend/core/.env`)

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Your Gemini API key — loaded by `core/llm.py` via `python-dotenv` |

### App Settings (`backend/core/config.py`)

| Variable | Default | Description |
|---|---|---|
| `VECTOR_DB_PATH` | `faiss_index` | Local path for FAISS persistence |
| `CHUNK_SIZE` | `900` | Characters per document chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between adjacent chunks |

---

## 🧠 How It Works

1. **Parse** — PDF is converted to markdown via `docling`, then split into overlapping chunks and embedded using `gemini-embedding-001`, stored in a FAISS index.
2. **Generate** — On quiz request, diverse chunks are retrieved using randomised query sampling. Gemini generates questions strictly from that content.
3. **Validate** — MCQ/True-False answers use normalised letter matching. Short answers use `all-MiniLM-L6-v2` cosine similarity with a 0.50 threshold.
4. **Explain** — Incorrect answers trigger an LLM explanation grounded in the document context (max 120 words, difficulty-appropriate).

---

## 📦 Key Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | REST API framework |
| `langchain` + `langchain-google-genai` | LLM orchestration |
| `google-genai` | Gemini LLM & embeddings (unified SDK) |
| `faiss-cpu` | Vector similarity search |
| `docling` | PDF → structured markdown parsing |
| `sentence-transformers` | Short-answer semantic validation |
| `scikit-learn` | Cosine similarity computation |
| `python-dotenv` | Loads API key from `.env` at runtime |

---

## 📝 License

MIT License. See `LICENSE` for details.