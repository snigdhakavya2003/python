import streamlit as st
import requests
import os

# ── Config ────────────────────────────────────────────────────────────────────
API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="🐍 Python Practice Hub",
    page_icon="🐍",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

.main { background-color: #0d1117; }

h1 { 
    font-family: 'JetBrains Mono', monospace !important;
    color: #58a6ff !important;
    font-size: 2rem !important;
}

.stButton > button {
    background: linear-gradient(135deg, #238636, #2ea043);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    padding: 0.6rem 2rem;
    font-size: 1rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2ea043, #3fb950);
    transform: translateY(-1px);
}

.question-box {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 4px solid #58a6ff;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    font-family: 'Space Grotesk', sans-serif;
    color: #e6edf3;
}

.hint-box {
    background: #1c2128;
    border: 1px solid #30363d;
    border-left: 4px solid #d29922;
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    margin: 0.5rem 0;
    color: #e3b341;
    font-size: 0.9rem;
}

.feedback-correct {
    background: #0d2818;
    border: 1px solid #238636;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    color: #3fb950;
}
.feedback-partial {
    background: #1f1d0e;
    border: 1px solid #d29922;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    color: #e3b341;
}
.feedback-wrong {
    background: #2d0f0f;
    border: 1px solid #da3633;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    color: #ff7b72;
}

.score-badge {
    display: inline-block;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 20px;
    padding: 0.2rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #58a6ff;
}

.ideal-box {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-top: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #c9d1d9;
    white-space: pre-wrap;
}

.level-beginner { color: #3fb950; font-weight: 700; }
.level-intermediate { color: #e3b341; font-weight: 700; }
.level-advanced { color: #ff7b72; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ── State Init ────────────────────────────────────────────────────────────────
if "question_data" not in st.session_state:
    st.session_state.question_data = None
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "show_hint" not in st.session_state:
    st.session_state.show_hint = False


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🐍 Python Practice Hub")
st.markdown("**Select a topic, pick your level, and get an AI-generated question to solve.**")
st.divider()


# ── Load Topics ───────────────────────────────────────────────────────────────
@st.cache_data
def load_topics():
    try:
        res = requests.get(f"{API_URL}/topics", timeout=5)
        return res.json()["topics"]
    except Exception:
        return {}

topics_data = load_topics()

if not topics_data:
    st.error("⚠️ Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
    st.code("cd backend && uvicorn main:app --reload", language="bash")
    st.stop()


# ── Sidebar — Topic Selector ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configure")
    st.markdown("---")

    difficulty = st.radio(
        "🎯 Difficulty Level",
        ["Beginner", "Intermediate", "Advanced"],
        index=0,
    )

    topic_list = topics_data.get(difficulty, [])
    topic = st.selectbox("📚 Select Topic", topic_list)

    st.markdown("---")
    st.markdown("### 📊 Your Session")
    if "attempts" not in st.session_state:
        st.session_state.attempts = 0
    if "correct" not in st.session_state:
        st.session_state.correct = 0

    col1, col2 = st.columns(2)
    col1.metric("Attempted", st.session_state.attempts)
    col2.metric("Correct", st.session_state.correct)

    if st.session_state.attempts > 0:
        pct = int((st.session_state.correct / st.session_state.attempts) * 100)
        st.progress(pct / 100, text=f"Accuracy: {pct}%")

    st.markdown("---")
    st.markdown("**🔑 Setup**")
    st.markdown("Set `GROQ_API_KEY` in your `.env` file")
    st.markdown("[Get free key →](https://console.groq.com)")


# ── Main Area ─────────────────────────────────────────────────────────────────
col_diff = {"Beginner": "level-beginner", "Intermediate": "level-intermediate", "Advanced": "level-advanced"}
st.markdown(f"**Topic:** {topic} &nbsp;|&nbsp; **Level:** <span class='{col_diff[difficulty]}'>{difficulty}</span>", unsafe_allow_html=True)

if st.button("⚡ Generate New Question", use_container_width=True):
    with st.spinner("Generating question..."):
        try:
            res = requests.post(f"{API_URL}/get-question", json={
                "topic": topic,
                "difficulty": difficulty,
            }, timeout=20)
            st.session_state.question_data = res.json()
            st.session_state.feedback = None
            st.session_state.show_hint = False
        except Exception as e:
            st.error(f"Error: {e}")

# ── Question Display ──────────────────────────────────────────────────────────
if st.session_state.question_data:
    q = st.session_state.question_data

    st.markdown(f"""
    <div class="question-box">
        <strong>📌 Question:</strong><br><br>
        {q.get('question', '')}
        {"<br><br><strong>Example Input:</strong> <code>" + q['example_input'] + "</code>" if q.get('example_input') else ""}
        {"<br><strong>Expected Output:</strong> <code>" + q['expected_output'] + "</code>" if q.get('expected_output') else ""}
    </div>
    """, unsafe_allow_html=True)

    # Hint toggle
    if q.get("hint"):
        if st.button("💡 Show Hint"):
            st.session_state.show_hint = not st.session_state.show_hint
        if st.session_state.show_hint:
            st.markdown(f'<div class="hint-box">💡 <strong>Hint:</strong> {q["hint"]}</div>', unsafe_allow_html=True)

    st.markdown("#### ✍️ Your Answer")
    user_answer = st.text_area(
        "Write your code or explanation below:",
        height=180,
        placeholder="# Write your Python code here...\ndef solution():\n    pass",
        label_visibility="collapsed",
    )

    if st.button("🚀 Submit Answer", use_container_width=True):
        if not user_answer.strip():
            st.warning("Please write an answer before submitting.")
        else:
            with st.spinner("Evaluating your answer..."):
                try:
                    res = requests.post(f"{API_URL}/evaluate", json={
                        "topic": topic,
                        "difficulty": difficulty,
                        "question": q.get("question", ""),
                        "user_answer": user_answer,
                    }, timeout=30)
                    st.session_state.feedback = res.json()
                    st.session_state.attempts += 1
                    verdict = st.session_state.feedback.get("verdict", "")
                    if verdict == "Correct":
                        st.session_state.correct += 1
                except Exception as e:
                    st.error(f"Error: {e}")

# ── Feedback Display ──────────────────────────────────────────────────────────
if st.session_state.feedback:
    fb = st.session_state.feedback
    verdict = fb.get("verdict", "")
    score = fb.get("score", 0)

    css_class = {
        "Correct": "feedback-correct",
        "Partially Correct": "feedback-partial",
        "Incorrect": "feedback-wrong",
    }.get(verdict, "feedback-partial")

    emoji = {"Correct": "✅", "Partially Correct": "⚠️", "Incorrect": "❌"}.get(verdict, "📝")

    st.markdown(f"""
    <div class="{css_class}">
        <strong>{emoji} {verdict}</strong> &nbsp; <span class="score-badge">Score: {score}/10</span>
        <br><br>
        <strong>👍 What was good:</strong><br>{fb.get('what_was_good', '-')}
        <br><br>
        <strong>📌 What was missing:</strong><br>{fb.get('what_was_missing', '-')}
        <br><br>
        <strong>💬 Tip:</strong> {fb.get('tip', '-')}
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📖 View Ideal Answer / Solution"):
        st.markdown(f'<div class="ideal-box">{fb.get("ideal_answer", "")}</div>', unsafe_allow_html=True)
