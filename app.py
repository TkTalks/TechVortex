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
# GLOBAL CSS (FIXED BUTTON COLORS ONLY)
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
.logout {
    font-size: 14px;
    cursor: pointer;
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
    margin-top: 10px;
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

/* ✅ BUTTON COLOR FIX (THIS WAS MISSING) */
div.stButton > button {
    border-radius: 20px;
    font-weight: 600;
    height: 42px;
    background: #ede7f6;
    color: #5e35b1;
    border: none;
}
div.stButton > button:hover {
    background: #d1c4e9;
}

/* Highlight Generate button */
.generate-btn div.stButton > button {
    background: #3f51b5 !important;
    color: white !important;
}

/* Footer helper text */
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
    <div class="logout">Logout</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# GROQ SETUP
# ------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ------------------------------------------------
# SESSION STATE (MINIMAL FIX)
# ------------------------------------------------
st.session_state.setdefault("initial_story", None)
st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("followup_input", "")
st.session_state.setdefault("draft", "")
st.session_state.setdefault("text_key", 0)  # ✅ required for Clear

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
    else:
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

def generate_initial_story(requirement, context):
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

# ------------------------------------------------
# MAIN HEADER
# ------------------------------------------------
req = st.session_state.draft

st.markdown(f"""
<div class="card-header">
    <span>Provide Requirements</span>
    <div>
        <span class="counter">Words: {len(req.split())}</span>
        <span class="counter">Characters: {len(req)}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# INPUT TABS
# ------------------------------------------------
tab_text, tab_file = st.tabs(["Text", "File"])

with tab_text:
    st.session_state.draft = st.text_area(
        "Requirement Text",
        value=st.session_state.draft,
        height=220,
        label_visibility="collapsed",
        key=f"text_{st.session_state.text_key}"
    )

with tab_file:
    uploaded_file = st.file_uploader("Upload .docx or .pdf", type=["docx", "pdf"])
    if uploaded_file:
        st.session_state.draft = extract_text(uploaded_file)
        st.success("File content loaded into editor")

# ------------------------------------------------
# ACTION BUTTONS
# ------------------------------------------------
col1, col2, col3, col4, col5 = st.columns([1,1,1,3,1])

with col1:
    if st.button("💾 Save Draft"):
        st.success("Draft saved")

with col2:
    if st.button("🔄 Regenerate"):
        if st.session_state.draft.strip():
            st.session_state.initial_story = generate_initial_story(
                st.session_state.draft, ""
            )
            st.session_state.chat_history = []

with col3:
    if st.button("❌ Clear"):
        st.session_state.draft = ""
        st.session_state.initial_story = None
        st.session_state.chat_history = []
        st.session_state.text_key += 1  # ✅ forces textarea reset

with col5:
    st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
    if st.button("✨ Generate"):
        if st.session_state.draft.strip():
            with st.spinner("Generating user stories..."):
                st.session_state.initial_story = generate_initial_story(
                    st.session_state.draft, ""
                )
        else:
            st.warning("Please enter requirement text")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="helper">Tips for better results · Optional guidance</div>', unsafe_allow_html=True)

# ------------------------------------------------
# OUTPUT
# ------------------------------------------------
if st.session_state.initial_story:
    st.markdown("## 📝 Generated User Stories")
    st.markdown(st.session_state.initial_story)
