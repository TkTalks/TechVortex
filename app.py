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
# SESSION STATE INIT
# ------------------------------------------------
defaults = {
    "draft": "",
    "initial_story": None,
    "chat_history": [],
    "followup_input": "",
    "editor_key": 0
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------------------------------------
# GLOBAL CSS (Modern UI - Like Screenshot 2)
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
    padding: 16px 30px;
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
    padding: 30px;
    max-width: 950px;
    margin: 50px auto;
    box-shadow: 0 20px 45px rgba(0,0,0,0.12);
}

/* Header gradient */
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
}

/* Counters */
.counter {
    background: rgba(255,255,255,0.9);
    color: #333;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 13px;
    margin-left: 8px;
}

/* Buttons */
div.stButton > button {
    border-radius: 20px !important;
    height: 42px !important;
    font-weight: 600 !important;
}

.primary-btn button {
    background-color: #3f51b5 !important;
    color: white !important;
}

.secondary-btn button {
    background-color: #ede7f6 !important;
    color: #5e35b1 !important;
}

/* Helper */
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
# GROQ CLIENT
# ------------------------------------------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠ GROQ_API_KEY not configured.")
    st.stop()

# ------------------------------------------------
# HELPERS
# ------------------------------------------------
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        reader = PdfReader(file)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text


def generate_initial_story(requirement):
    prompt = f"""
You are a Senior Agile Business Analyst.

Convert the following requirement into:
1. Atomic User Stories
2. Acceptance Criteria (Given-When-Then)
3. Edge Cases
4. Assumptions

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
        {"role": "system", "content": "You are a Senior Agile Business Analyst."},
        {"role": "assistant", "content": st.session_state.initial_story}
    ]

    for h in st.session_state.chat_history:
        messages.append({"role": "assistant", "content": h})

    messages.append({"role": "user", "content": question})

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.5
    )

    answer = resp.choices[0].message.content
    st.session_state.chat_history.append(answer)
    return answer


def clear_all():
    st.session_state.draft = ""
    st.session_state.initial_story = None
    st.session_state.chat_history = []
    st.session_state.followup_input = ""
    st.session_state.editor_key += 1
    st.rerun()


def regenerate_story():
    if st.session_state.draft.strip():
        st.session_state.initial_story = generate_initial_story(
            st.session_state.draft
        )
        st.session_state.chat_history = []
        st.session_state.followup_input = ""
        st.rerun()

# ------------------------------------------------
# MAIN CARD
# ------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

requirement = st.session_state.draft
words = len(requirement.split())
chars = len(requirement)

st.markdown(f"""
<div class="card-header">
    <span>Provide Requirements</span>
    <div>
        <span class="counter">Words: {words}</span>
        <span class="counter">Characters: {chars}</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab_text, tab_file = st.tabs(["Text", "File"])

with tab_text:
    requirement = st.text_area(
        "Requirement Text",
        value=st.session_state.draft,
        height=220,
        key=f"editor_{st.session_state.editor_key}"
    )
    st.session_state.draft = requirement

with tab_file:
    uploaded_file = st.file_uploader("Upload .docx or .pdf", type=["docx", "pdf"])
    if uploaded_file:
        st.session_state.draft = extract_text(uploaded_file)
        st.session_state.editor_key += 1
        st.success("File content loaded into editor")
        st.rerun()

# ------------------------------------------------
# BUTTON ROW
# ------------------------------------------------
col1, col2, col3, col4, col5 = st.columns([1,1,1,2,1])

with col1:
    st.button("💾 Save Draft")

with col2:
    st.button("🔄 Regenerate", on_click=regenerate_story)

with col3:
    st.button("❌ Clear", on_click=clear_all)

with col5:
    generate_disabled = not st.session_state.draft.strip()
    if st.button("✨ Generate", disabled=generate_disabled):
        with st.spinner("Generating user stories..."):
            st.session_state.initial_story = generate_initial_story(
                st.session_state.draft
            )
        st.rerun()

st.markdown('<div class="helper">Tips for better results · Optional guidance</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------
# OUTPUT SECTION
# ------------------------------------------------
if st.session_state.initial_story:

    st.markdown("## 📝 Generated User Stories")
    st.markdown(st.session_state.initial_story)

    st.markdown("## 💬 Follow-up Questions")

    st.session_state.followup_input = st.text_area(
        "Ask refinement questions",
        value=st.session_state.followup_input,
        height=100
    )

    if st.button("Ask AI"):
        if st.session_state.followup_input.strip():
            with st.spinner("AI responding..."):
                generate_followup(st.session_state.followup_input)
            st.session_state.followup_input = ""
            st.rerun()

if st.session_state.chat_history:
    st.markdown("## 🗂 Follow-up History")
    for i, h in enumerate(st.session_state.chat_history, 1):
        st.markdown(f"**Follow-up {i}:**")
        st.markdown(h)
