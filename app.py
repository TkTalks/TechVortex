import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

st.set_page_config(page_title="TechVortex", layout="wide")

# ---------- GROQ ----------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ---------- BACKEND FUNCTION ----------
def generate_user_story(req):
    prompt = f"""
Convert this raw requirement into structured Agile user stories
with acceptance criteria.

Requirement:
{req}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content


# ---------- HANDLE FORM SUBMIT ----------
if "result" not in st.session_state:
    st.session_state.result = ""

if st.session_state.get("submitted_text"):
    st.session_state.result = generate_user_story(
        st.session_state.submitted_text
    )

# ---------- FULL UI ----------
components.html(
f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    font-family: Inter, sans-serif;
    background: linear-gradient(to right, #eef2ff, #fdf2f8);
}}

.card {{
    width: 70%;
    margin: 40px auto;
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}}

.header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(to right, #1d4ed8, #22c55e);
    padding: 16px;
    color: white;
    border-radius: 12px;
}}

.stats span {{
    background: white;
    color: black;
    padding: 6px 14px;
    border-radius: 20px;
    margin-left: 8px;
    font-size: 14px;
}}

textarea {{
    width: 100%;
    height: 180px;
    border-radius: 10px;
    border: 2px solid #2563eb;
    padding: 12px;
    font-size: 15px;
}}

.buttons {{
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
}}

button {{
    border-radius: 10px;
    padding: 10px 18px;
    font-size: 14px;
    cursor: pointer;
}}

.primary {{
    background: #2563eb;
    color: white;
    border: none;
}}

.secondary {{
    background: #6366f1;
    color: white;
    border: none;
}}

.clear {{
    background: white;
    border: 1px solid red;
    color: red;
}}

.output {{
    white-space: pre-wrap;
    background: #f8fafc;
    padding: 20px;
    border-radius: 12px;
    margin-top: 30px;
}}
</style>

<script>
function updateCount() {{
    const text = document.getElementById("req").value;
    document.getElementById("words").innerText =
        text.trim() ? text.trim().split(/\\s+/).length : 0;
    document.getElementById("chars").innerText = text.length;
}}
</script>
</head>

<body>

<div class="card">
  <div class="header">
    <h3>Provide Requirements</h3>
    <div class="stats">
      <span>Words: <b id="words">0</b></span>
      <span>Characters: <b id="chars">0</b></span>
    </div>
  </div>

  <br>
  <textarea id="req" oninput="updateCount()"
  placeholder="System must support biometric login..."></textarea>

  <div class="buttons">
    <button class="secondary">Save Draft</button>
    <button class="clear" onclick="document.getElementById('req').value=''">
      Clear
    </button>
    <form method="post">
      <input type="hidden" name="reqText"
        value="" id="hiddenText">
      <button class="primary"
        onclick="document.getElementById('hiddenText').value =
        document.getElementById('req').value;">
        Generate
      </button>
    </form>
  </div>

  {"<div class='output'>" + st.session_state.result + "</div>" if st.session_state.result else ""}
</div>

</body>
</html>
""",
height=900,
scrolling=True,
)
