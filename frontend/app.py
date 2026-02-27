import streamlit as st
import requests

# ==================================
# CONFIG
# ==================================
API_PARSE = "http://127.0.0.1:8000/parse-document"
API_GENERATE = "http://127.0.0.1:8000/generate-quiz"
API_SUBMIT = "http://127.0.0.1:8000/submit-quiz"

st.set_page_config(
    page_title="Quizify · AI Quiz Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================
# CUSTOM CSS — Dark Academic Theme
# ==================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&family=DM+Mono&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0e0d0b !important;
    color: #e8e0d0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 60% at 20% 0%, rgba(139,104,60,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(90,60,30,0.10) 0%, transparent 60%),
        #0e0d0b !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }

/* ── TYPOGRAPHY ── */
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #f2e8d0 !important;
    letter-spacing: -0.01em;
}

/* ── HERO HEADER ── */
.quizify-hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
}
.quizify-hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 1px;
    height: 40px;
    background: linear-gradient(to bottom, transparent, #c9a96e);
}
.quizify-logo {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f2e8d0 0%, #c9a96e 50%, #f2e8d0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1;
}
.quizify-tagline {
    font-family: 'DM Sans', sans-serif;
    font-weight: 300;
    font-size: 0.95rem;
    color: #8a7a68;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}
.quizify-divider {
    width: 60px;
    height: 1px;
    background: linear-gradient(to right, transparent, #c9a96e, transparent);
    margin: 1.5rem auto 0;
}

/* ── CARDS ── */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(201,169,110,0.15);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(201,169,110,0.4), transparent);
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: #c9a96e;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── UPLOAD ZONE ── */
[data-testid="stFileUploader"] {
    background: rgba(201,169,110,0.04) !important;
    border: 1.5px dashed rgba(201,169,110,0.25) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    transition: all 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(201,169,110,0.5) !important;
    background: rgba(201,169,110,0.07) !important;
}
[data-testid="stFileUploaderDropzone"] label {
    color: #8a7a68 !important;
    font-size: 0.9rem !important;
}

/* ── BUTTONS ── */
[data-testid="stButton"] > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.06em !important;
    border-radius: 8px !important;
    border: 1px solid rgba(201,169,110,0.4) !important;
    background: rgba(201,169,110,0.10) !important;
    color: #c9a96e !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.25s ease !important;
    text-transform: uppercase !important;
}
[data-testid="stButton"] > button:hover {
    background: rgba(201,169,110,0.20) !important;
    border-color: #c9a96e !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(201,169,110,0.15) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* Primary button variant */
.primary-btn [data-testid="stButton"] > button {
    background: linear-gradient(135deg, rgba(201,169,110,0.25), rgba(201,169,110,0.12)) !important;
    border-color: rgba(201,169,110,0.6) !important;
    box-shadow: 0 2px 12px rgba(201,169,110,0.12) !important;
}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(201,169,110,0.2) !important;
    border-radius: 8px !important;
    color: #e8e0d0 !important;
}
[data-testid="stSelectbox"] label {
    color: #8a7a68 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ── NUMBER INPUT ── */
[data-testid="stNumberInput"] > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(201,169,110,0.2) !important;
    border-radius: 8px !important;
    color: #e8e0d0 !important;
}
[data-testid="stNumberInput"] label {
    color: #8a7a68 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ── TEXT INPUT ── */
[data-testid="stTextInput"] > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(201,169,110,0.2) !important;
    border-radius: 8px !important;
    color: #e8e0d0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] > div > div > input:focus {
    border-color: rgba(201,169,110,0.5) !important;
    box-shadow: 0 0 0 2px rgba(201,169,110,0.08) !important;
}
[data-testid="stTextInput"] label {
    color: #8a7a68 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ── RADIO ── */
[data-testid="stRadio"] label {
    color: #e8e0d0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stRadio"] > div > div {
    gap: 0.5rem !important;
}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    color: #8a7a68 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border-left: 3px solid !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] { color: #c9a96e !important; }

/* ── DIVIDER ── */
hr { border-color: rgba(201,169,110,0.1) !important; }

/* ── QUESTION CARD ── */
.q-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(201,169,110,0.12);
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
    position: relative;
}
.q-number {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #c9a96e;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.q-text {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    color: #f2e8d0;
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* ── RESULT CARDS ── */
.result-card {
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid;
    position: relative;
}
.result-correct {
    background: rgba(74,167,111,0.07);
    border-color: rgba(74,167,111,0.25);
}
.result-incorrect {
    background: rgba(220,80,80,0.07);
    border-color: rgba(220,80,80,0.25);
}
.result-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    margin-bottom: 0.75rem;
}
.badge-correct {
    background: rgba(74,167,111,0.15);
    color: #6dd89a;
    border: 1px solid rgba(74,167,111,0.3);
}
.badge-incorrect {
    background: rgba(220,80,80,0.15);
    color: #f08080;
    border: 1px solid rgba(220,80,80,0.3);
}
.result-question {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    color: #f2e8d0;
    margin-bottom: 0.75rem;
    line-height: 1.5;
}
.answer-row {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
    margin-bottom: 0.75rem;
}
.answer-label {
    font-size: 0.72rem;
    color: #6a5a48;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.2rem;
}
.answer-value {
    font-family: 'DM Mono', monospace;
    font-size: 0.88rem;
    color: #c9a96e;
}
.explanation-box {
    background: rgba(201,169,110,0.06);
    border-left: 2px solid rgba(201,169,110,0.35);
    border-radius: 0 8px 8px 0;
    padding: 0.875rem 1rem;
    margin-top: 0.75rem;
}
.explanation-label {
    font-size: 0.7rem;
    color: #8a7a68;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 0.35rem;
}
.explanation-text {
    font-size: 0.88rem;
    color: #c9b898;
    line-height: 1.7;
    font-style: italic;
}
.concept-tag {
    display: inline-block;
    font-size: 0.7rem;
    color: #8a7a68;
    border: 1px solid rgba(138,122,104,0.25);
    border-radius: 4px;
    padding: 0.15rem 0.5rem;
    margin-top: 0.5rem;
    letter-spacing: 0.06em;
}

/* ── SCORE DISPLAY ── */
.score-hero {
    text-align: center;
    padding: 3rem 1rem;
}
.score-number {
    font-family: 'Playfair Display', serif;
    font-size: 5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f2e8d0, #c9a96e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.score-label {
    font-size: 0.85rem;
    color: #6a5a48;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-top: 0.5rem;
}
.score-bar-bg {
    background: rgba(255,255,255,0.06);
    border-radius: 100px;
    height: 6px;
    margin: 1.5rem auto;
    max-width: 300px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(to right, #8a6a30, #c9a96e, #f2e8d0);
    transition: width 1s ease;
}
.score-message {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.1rem;
    color: #8a7a68;
    margin-top: 1rem;
}

/* ── STATUS BADGE ── */
.status-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.06em;
}
.status-ready {
    background: rgba(74,167,111,0.12);
    border: 1px solid rgba(74,167,111,0.3);
    color: #6dd89a;
}

/* ── PROGRESS BAR OVERRIDE ── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(to right, #8a6a30, #c9a96e) !important;
}
[data-testid="stProgress"] > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 100px !important;
}

/* ── COLUMN GAPS ── */
[data-testid="column"] { padding: 0 0.5rem !important; }

/* ── HIDE STREAMLIT BRANDING ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── STEP LABEL ── */
.step-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
.step-num {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 1px solid rgba(201,169,110,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #c9a96e;
    flex-shrink: 0;
}
.step-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    color: #f2e8d0;
}
</style>
""", unsafe_allow_html=True)

# ==================================
# SESSION STATE
# ==================================
defaults = {
    "document_ready": False,
    "quiz": None,
    "quiz_id": None,
    "quiz_generated": False,
    "submitted_result": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==================================
# HERO HEADER
# ==================================
st.markdown("""
<div class="quizify-hero">
    <p class="quizify-logo">Quizify</p>
    <p class="quizify-tagline">AI-Powered Knowledge Assessment</p>
    <div class="quizify-divider"></div>
</div>
""", unsafe_allow_html=True)

# ==================================
# LAYOUT — two column on wide screens
# ==================================
left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    # ── STEP 1: UPLOAD ──
    st.markdown("""
    <div class="step-label">
        <div class="step-num">01</div>
        <div class="step-title">Upload Document</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your PDF here",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if st.session_state.document_ready:
        st.markdown("""
        <div class="status-chip status-ready" style="margin: 0.75rem 0;">
            ✦ Document Ready
        </div>
        """, unsafe_allow_html=True)

    if uploaded_file:
        if st.button("Parse Document →", use_container_width=True):
            with st.spinner("Parsing your document..."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    )
                }
                response = requests.post(API_PARSE, files=files)
                if response.status_code == 200:
                    st.session_state.document_ready = True
                    st.rerun()
                else:
                    st.error("Backend connection failed.")

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    # ── STEP 2: SETTINGS ──
    if st.session_state.document_ready:
        st.markdown("""
        <div class="step-label">
            <div class="step-num">02</div>
            <div class="step-title">Configure Quiz</div>
        </div>
        """, unsafe_allow_html=True)

        num_questions = st.number_input(
            "Number of Questions",
            min_value=1, max_value=20, value=5
        )

        difficulty = st.selectbox(
            "Difficulty Level",
            ["Easy", "Medium", "Hard"]
        )

        question_type = st.selectbox(
            "Question Type",
            ["MCQ", "True/False", "Short Answer"]
        )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        if st.button("Generate Quiz ✦", use_container_width=True):
            with st.spinner("Crafting your quiz..."):
                payload = {
                    "topic": "full document",
                    "num_questions": num_questions,
                    "difficulty": difficulty,
                    "question_type": question_type,
                }
                res = requests.post(API_GENERATE, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.quiz = data["questions"]
                    st.session_state.quiz_id = data["quiz_id"]
                    st.session_state.quiz_generated = True
                    st.session_state.submitted_result = None
                    # clear old answers
                    for k in list(st.session_state.keys()):
                        if k.startswith("q_"):
                            del st.session_state[k]
                    st.rerun()
                else:
                    st.error("Quiz generation failed.")

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        if st.session_state.quiz_generated:
            if st.button("↺  Reset Quiz", use_container_width=True):
                st.session_state.quiz = None
                st.session_state.quiz_id = None
                st.session_state.quiz_generated = False
                st.session_state.submitted_result = None
                for k in list(st.session_state.keys()):
                    if k.startswith("q_"):
                        del st.session_state[k]
                st.rerun()

# ==================================
# MAIN CONTENT — RIGHT COLUMN
# ==================================
with right_col:

    # ── QUIZ QUESTIONS ──
    if (
        st.session_state.quiz_generated
        and st.session_state.quiz
        and not st.session_state.submitted_result
    ):
        st.markdown("""
        <div class="step-label">
            <div class="step-num">03</div>
            <div class="step-title">Answer the Questions</div>
        </div>
        """, unsafe_allow_html=True)

        answers_payload = []

        for i, q in enumerate(st.session_state.quiz):
            with st.container():
                st.markdown(
                    f"<p style='font-family:DM Mono,monospace;font-size:0.7rem;"
                    f"color:#c9a96e;letter-spacing:0.15em;text-transform:uppercase;"
                    f"margin-bottom:0.25rem'>Question {i+1} of {len(st.session_state.quiz)}</p>",
                    unsafe_allow_html=True
                )
                st.markdown(f"**{q['question']}**")

                key = f"q_{i}"

                if "options" in q:
                    user_answer = st.radio(
                        "Select your answer:",
                        q["options"],
                        key=key,
                        label_visibility="collapsed"
                    )
                else:
                    user_answer = st.text_input(
                        "Your answer:",
                        key=key,
                        placeholder="Type your answer here...",
                        label_visibility="collapsed"
                    )

                answers_payload.append({
                    "question_index": i,
                    "user_answer": user_answer or "",
                })

                st.divider()

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        if st.button("Submit Quiz →", use_container_width=True):
            unanswered = [
                a for a in answers_payload
                if not a["user_answer"].strip()
            ]
            if unanswered:
                st.warning(
                    f"⚠️ Please answer all questions before submitting. "
                    f"({len(unanswered)} remaining)"
                )
            else:
                with st.spinner("Evaluating your answers..."):
                    response = requests.post(
                        API_SUBMIT,
                        json={
                            "quiz_id": st.session_state.quiz_id,
                            "answers": answers_payload,
                        },
                    )
                    if response.status_code == 200:
                        st.session_state.submitted_result = response.json()
                        st.rerun()
                    elif response.status_code == 404:
                        st.error(
                            "Quiz session expired. Please generate a new quiz."
                        )
                    else:
                        st.error("Submission failed. Please try again.")

    # ── RESULTS ──
    elif st.session_state.submitted_result:
        result = st.session_state.submitted_result
        score = result["score"]
        total = result["total"]
        pct = (score / total * 100) if total else 0

        # Score message
        if pct == 100:
            msg = "Perfect score — Outstanding!"
        elif pct >= 80:
            msg = "Excellent command of the material."
        elif pct >= 60:
            msg = "Good effort — room to grow."
        elif pct >= 40:
            msg = "Keep studying — you'll get there."
        else:
            msg = "Review the material and try again."

        if pct == 100:
            st.balloons()

        # ── Score Hero (static HTML only, no user data) ──
        st.markdown(f"""
        <div class="score-hero">
            <div class="score-number">{score}<span style="font-size:2rem;color:#6a5a48">/{total}</span></div>
            <div class="score-label">Final Score</div>
            <div class="score-bar-bg">
                <div class="score-bar-fill" style="width:{pct:.1f}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Score message via native widget (safe for any text)
        st.markdown(
            f"<p style='text-align:center;font-family:Playfair Display,serif;"
            f"font-style:italic;font-size:1.1rem;color:#8a7a68;margin-bottom:2rem'>"
            f"{msg}</p>",
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="step-label" style="margin-top:1rem">
            <div class="step-num">✦</div>
            <div class="step-title">Detailed Review</div>
        </div>
        """, unsafe_allow_html=True)

        for i, r in enumerate(result["results"]):
            correct = r["correct"]

            # Native container with border styling
            with st.container():
                if correct:
                    # Green success styling
                    st.markdown("""
                    <div style="
                        background:rgba(74,167,111,0.07);
                        border:1px solid rgba(74,167,111,0.3);
                        border-radius:12px;
                        padding:1.25rem 1.5rem 0.5rem;
                        margin-bottom:0.25rem;
                    ">
                        <span style="
                            display:inline-block;
                            background:rgba(74,167,111,0.15);
                            color:#6dd89a;
                            border:1px solid rgba(74,167,111,0.3);
                            border-radius:20px;
                            padding:0.2rem 0.75rem;
                            font-size:0.75rem;
                            font-weight:500;
                            letter-spacing:0.1em;
                            text-transform:uppercase;
                            margin-bottom:0.6rem;
                        ">✓ Correct</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="
                        background:rgba(220,80,80,0.07);
                        border:1px solid rgba(220,80,80,0.3);
                        border-radius:12px;
                        padding:1.25rem 1.5rem 0.5rem;
                        margin-bottom:0.25rem;
                    ">
                        <span style="
                            display:inline-block;
                            background:rgba(220,80,80,0.15);
                            color:#f08080;
                            border:1px solid rgba(220,80,80,0.3);
                            border-radius:20px;
                            padding:0.2rem 0.75rem;
                            font-size:0.75rem;
                            font-weight:500;
                            letter-spacing:0.1em;
                            text-transform:uppercase;
                            margin-bottom:0.6rem;
                        ">✗ Incorrect</span>
                    </div>
                    """, unsafe_allow_html=True)

                # Question text — native markdown (safe)
                st.markdown(f"**Q{i+1}.** {r['question']}")

                # Answers — native widgets only
                if not correct:
                    a_col, b_col = st.columns(2)
                    with a_col:
                        st.caption("YOUR ANSWER")
                        st.markdown(
                            f"<span style='font-family:DM Mono,monospace;"
                            f"color:#f08080;font-size:0.9rem'>"
                            f"{r['user_answer'] or '—'}</span>",
                            unsafe_allow_html=True
                        )
                    with b_col:
                        st.caption("CORRECT ANSWER")
                        st.markdown(
                            f"<span style='font-family:DM Mono,monospace;"
                            f"color:#c9a96e;font-size:0.9rem'>"
                            f"{r['correct_answer']}</span>",
                            unsafe_allow_html=True
                        )

                # Concept tag
                if r.get("concept"):
                    st.caption(f"✦ Concept: {r['concept']}")

                # Explanation box — native st.info (fully safe, no HTML injection)
                if not correct and r.get("explanation"):
                    st.info(f"**Explanation:** {r['explanation']}")

                st.divider()

    # ── EMPTY STATE ──
    elif not st.session_state.document_ready:
        st.markdown("""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 400px;
            text-align: center;
            color: #3a3028;
        ">
            <div style="font-size:4rem;margin-bottom:1rem;opacity:0.3">📜</div>
            <p style="font-family:'Playfair Display',serif;font-size:1.2rem;color:#4a3f35;font-style:italic">
                Upload a document to begin your study session
            </p>
            <p style="font-size:0.82rem;color:#3a3028;margin-top:0.5rem;letter-spacing:0.08em;text-transform:uppercase">
                Supports PDF
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.document_ready and not st.session_state.quiz_generated:
        st.markdown("""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 400px;
            text-align: center;
        ">
            <div style="font-size:4rem;margin-bottom:1rem;opacity:0.25">✦</div>
            <p style="font-family:'Playfair Display',serif;font-size:1.2rem;color:#5a4a38;font-style:italic">
                Configure your quiz settings and generate
            </p>
        </div>
        """, unsafe_allow_html=True)