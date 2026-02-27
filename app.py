import streamlit as st
from groq import Groq
from docx import Document
from PyPDF2 import PdfReader

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(
    page_title="TechVortex",
    page_icon="💡",
    layout="wide"
)

# ------------------------------------------------
# GLOBAL CSS
# ------------------------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #eef2f3, #e9e4f0);
}
[data-testid="stAppViewContainer"] {
    background: transparent;
}
header { visibility: hidden; }

/* Top Navbar */
.topbar {
    background: #3f51b5;
    color: white;
    padding: 14px 30px;
    font-size: 20px;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Main Card */
.card {
    background: white;
    border-radius: 16px;
    padding: 25px;
    max-width: 900px;
    margin: 40px auto;
    box-shadow: 0 15px 40px rgba(0,0,0,0.1);
}

/* Header */
.card-header {
    background: linear-gradient(90deg, #1e88e5, #43a047);
    color: white;
    padding: 16px 20px;
    border-radius: 12px;
    font-size: 20px;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

/* Counter */
.counter {
    background: rgba(255,255,255,0.9);
    color: #333;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 13px;
    margin-left: 8px;
}

/* Buttons */
.stButton > button {
    border-radius: 25px !important;
    height: 44px !important;
    font-weight: 600 !important;
    padding: 0 22px !important;
    border: none !important;
    transition: 0.2s ease;
}

/* Hover */
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}

/* Helper text */
.helper {
    font-size: 13px;
    color: #666;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# TOP BAR
# ------------------------------------------------
st.markdown("""
<div class="topbar">
    <div>TechVortex</div>
    <div>Logout</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# GROQ SETUP
# ------------------------------------------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠ GROQ_API_KEY not configured.")
    st.stop()

# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------
st.session_state.setdefault("initial_story", None)
st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("followup_input", "")
st.session_state.setdefault("draft", "")
st.session_state.setdefault("last_uploaded", None)

# ------------------------------------------------
# HELPERS
# ------------------------------------------------
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        reader = PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file.type == "text/plain":
        text = file.read().decode("utf-8")
    return text


def generate_initial_story(requirement):
    prompt = f"""
You are a Senior Agile Business Analyst.

Convert this requirement into:
- Atomic user stories
- Acceptance Criteria
- Edge Cases
- Assumptions

STRICT FORMAT.

Requirement:
{requirement}
"""
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return resp.choices[0].message.content


def generate_followup(question):
    messages = [
        {"role": "system", "content": "You are a helpful AI Business Analyst."},
        {"role": "assistant", "content": st.session_state.initial_story},
        {"role": "user", "content": question}
    ]

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.5
    )
    return resp.choices[0].message.content


def clear_all():
    st.session_state["draft"] = ""
    st.session_state["initial_story"] = None
    st.session_state["chat_history"] = []
    st.session_state["followup_input"] = ""


# ------------------------------------------------
# MAIN CARD
# ------------------------------------------------
requirement = st.session_state.draft
words = len(requirement.split())
chars = len(requirement)

st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown(f"""
<div class="card-header">
    <span>Provide Requirements</span>
    <div>
        <span class="counter">Words: {words}</span>
        <span class="counter">Characters: {chars}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_text, tab_file = st.tabs(["Text", "File"])

with tab_text:
    st.text_area(
        "Requirement Text",
        key="draft",
        height=220,
        label_visibility="collapsed"
    )

with tab_file:
    uploaded_file = st.file_uploader(
        "Upload .docx or .pdf or .txt",
        type=["docx", "pdf", "txt"]
    )
    if uploaded_file:
        st.session_state["draft"] = extract_text(uploaded_file)

# ------------------------------------------------
# BUTTONS
# ------------------------------------------------
left, mid1, mid2, right = st.columns([1.2, 1.2, 1.2, 4])

with left:
    if st.button("💾 Save Draft", use_container_width=True):
        st.success("Draft saved")

with mid1:
    if st.button("🔄 Regenerate", use_container_width=True):
        if st.session_state.draft.strip():
            with st.spinner("Regenerating..."):
                st.session_state.initial_story = generate_initial_story(
                    st.session_state.draft
                )
        else:
            st.warning("Please enter requirement text")

with mid2:
    st.button("❌ Clear", on_click=clear_all, use_container_width=True)

with right:
    if st.button("✨ Generate"):
        if st.session_state.draft.strip():
            with st.spinner("Generating user stories..."):
                st.session_state.initial_story = generate_initial_story(
                    st.session_state.draft
                )
        else:
            st.warning("Please enter requirement text")

st.markdown('<div class="helper">Tips for better results · Optional guidance</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------
# OUTPUT
# ------------------------------------------------
if st.session_state.initial_story:
    st.markdown("## 📝 Generated User Stories")
    st.markdown(st.session_state.initial_story)

    st.markdown("## 💬 Follow-up Question")
    st.session_state.followup_input = st.text_area(
        "Ask refinement question",
        value=st.session_state.followup_input,
        height=100
    )

    if st.button("Ask AI"):
        if st.session_state.followup_input.strip():
            with st.spinner("AI responding..."):
                answer = generate_followup(
                    st.session_state.followup_input
                )
            st.markdown(answer)
