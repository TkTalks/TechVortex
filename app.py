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
if "draft" not in st.session_state:
    st.session_state.draft = ""

if "initial_story" not in st.session_state:
    st.session_state.initial_story = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "followup_input" not in st.session_state:
    st.session_state.followup_input = ""

# ------------------------------------------------
# CSS (Your original improved slightly)
# ------------------------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #eef2f3, #e9e4f0);
}
header {visibility:hidden;}

.topbar {
    background: #3f51b5;
    color: white;
    padding: 14px 30px;
    font-size: 20px;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
}

.card {
    background: white;
    border-radius: 16px;
    padding: 25px;
    max-width: 900px;
    margin: 40px auto;
    box-shadow: 0 15px 40px rgba(0,0,0,0.1);
}

.card-header {
    background: linear-gradient(90deg, #1e88e5, #43a047);
    color: white;
    padding: 16px 20px;
    border-radius: 12px;
    font-size: 20px;
    font-weight: 600;
    display:flex;
    justify-content:space-between;
}

.counter {
    background: rgba(255,255,255,0.9);
    color: #333;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 13px;
    margin-left: 8px;
}

div.stButton > button {
    background-color: #3f51b5 !important;
    color: white !important;
    border-radius: 6px !important;
    height: 42px !important;
    font-weight: 600 !important;
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

st.markdown('<div class="card">', unsafe_allow_html=True)

# ------------------------------------------------
# GROQ CLIENT
# ------------------------------------------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("GROQ_API_KEY not configured.")
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

Convert into:
- Atomic User Stories
- Acceptance Criteria (Given-When-Then)
- Edge Cases
- Assumptions

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
        {"role": "assistant", "content": st.session_state.initial_story},
        {"role": "user", "content": question}
    ]

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


# ------------------------------------------------
# REQUIREMENT INPUT
# ------------------------------------------------
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
        key="requirement_input"
    )
    st.session_state.draft = requirement

with tab_file:
    uploaded_file = st.file_uploader("Upload .docx or .pdf", type=["docx", "pdf"])
    if uploaded_file:
        st.session_state.draft = extract_text(uploaded_file)
        st.success("File loaded into editor")

# ------------------------------------------------
# BUTTONS
# ------------------------------------------------
col1, col2, col3, col4 = st.columns([1,1,1,1])

with col1:
    st.button("💾 Save Draft")

with col2:
    if st.button("🔄 Regenerate"):
        if st.session_state.draft.strip():
            st.session_state.initial_story = generate_initial_story(
                st.session_state.draft
            )
            st.session_state.chat_history = []

with col3:
    st.button("❌ Clear", on_click=clear_all)

with col4:
    if st.button("✨ Generate"):
        if st.session_state.draft.strip():
            with st.spinner("Generating..."):
                st.session_state.initial_story = generate_initial_story(
                    st.session_state.draft
                )
        else:
            st.warning("Please enter requirement text")

st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------
# OUTPUT
# ------------------------------------------------
if st.session_state.initial_story:
    st.markdown("## 📝 Generated User Stories")
    st.markdown(st.session_state.initial_story)

    st.markdown("## 💬 Follow-up Question")
    st.session_state.followup_input = st.text_area(
        "Ask question",
        value=st.session_state.followup_input,
        height=100
    )

    if st.button("Ask AI"):
        if st.session_state.followup_input.strip():
            with st.spinner("AI responding..."):
                answer = generate_followup(st.session_state.followup_input)
            st.session_state.followup_input = ""
            st.markdown(answer)

if st.session_state.chat_history:
    st.markdown("## 🗂 Follow-up History")
    for i, h in enumerate(st.session_state.chat_history, 1):
        st.markdown(f"**Follow-up {i}:**")
        st.markdown(h)
