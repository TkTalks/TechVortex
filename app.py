import streamlit as st
from groq import Groq
from docx import Document
from PyPDF2 import PdfReader
from datetime import datetime
from io import BytesIO
import base64

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="TechVortex | Requirements",
    page_icon="✨",
    layout="wide"
)

# ----------------------------------
# CUSTOM CSS (Card-style UI)
# ----------------------------------
st.markdown("""
<style>
.card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.counter {
    display: flex;
    gap: 16px;
}
.badge {
    background: #e6f4ea;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 14px;
}
.actions {
    display: flex;
    gap: 12px;
    margin-top: 20px;
}
.output {
    background: #f7f9fc;
    padding: 16px;
    border-radius: 12px;
    white-space: pre-wrap;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# GROQ CLIENT
# ----------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ----------------------------------
# SESSION STATE
# ----------------------------------
for key in ["input_text", "generated"]:
    st.session_state.setdefault(key, "")

# ----------------------------------
# CARD START
# ----------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

# Header
word_count = len(st.session_state.input_text.split())
char_count = len(st.session_state.input_text)

st.markdown(f"""
<div class="header">
  <h2>Provide Requirements</h2>
  <div class="counter">
    <div class="badge">📝 Words: {word_count}</div>
    <div class="badge">🔤 Characters: {char_count}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# TABS
# ----------------------------------
tab_text, tab_file = st.tabs(["Text", "File"])

with tab_text:
    st.session_state.input_text = st.text_area(
        "Requirement Text",
        value=st.session_state.input_text,
        height=200,
        placeholder="Paste or type your requirements..."
    )

with tab_file:
    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf", "docx"]
    )

    if uploaded_file:
        extracted = ""
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                extracted += page.extract_text() or ""
        else:
            doc = Document(uploaded_file)
            for p in doc.paragraphs:
                extracted += p.text + "\n"

        st.session_state.input_text = extracted
        st.success("File content loaded into Text tab")

# ----------------------------------
# BUTTON ACTIONS
# ----------------------------------
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,2])

with col1:
    if st.button("💾 Save Draft"):
        st.success("Draft saved locally")

with col2:
    if st.button("🔄 Regenerate") and st.session_state.input_text:
        st.session_state.generated = ""

with col3:
    if st.button("❌ Clear"):
        st.session_state.input_text = ""
        st.session_state.generated = ""

with col4:
    st.button("⬅ Back")

with col5:
    generate = st.button("✨ Generate")

# ----------------------------------
# AI GENERATION
# ----------------------------------
def generate_story(requirement):
    prompt = f"""
You are a Senior Agile Business Analyst.

Convert the requirement into well-structured user stories with:
- As a / I want / So that
- Acceptance criteria
- Edge cases
- Assumptions

Requirement:
{requirement}
"""
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return res.choices[0].message.content

if generate and st.session_state.input_text.strip():
    with st.spinner("Generating structured user stories..."):
        st.session_state.generated = generate_story(st.session_state.input_text)

# ----------------------------------
# OUTPUT
# ----------------------------------
if st.session_state.generated:
    st.markdown("### Output")
    st.markdown(f'<div class="output">{st.session_state.generated}</div>', unsafe_allow_html=True)

    # Download Word
    doc = Document()
    doc.add_heading("Generated User Stories", level=1)
    doc.add_paragraph(st.session_state.generated)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "⬇ Download Word",
        buffer,
        file_name=f"user_stories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

st.markdown('</div>', unsafe_allow_html=True)
