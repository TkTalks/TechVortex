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


# ---------- READ FORM POST ----------
query_params = st.query_params
if "reqText" in query_params:
    st.session_state.submitted_text = query_params["reqText"]

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
    font-family: Roboto, sans-serif;
    background: linear-gradient(to right, #eef2ff, #f8fafc);
}}

.card {{
    width: 65%;
    margin: 60px auto;
    background: #ffffff;
    border-radius: 18px;
    padding: 28px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
}}

.header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(90deg, #1e88e5, #43a047);
    padding: 18px 22px;
    border-radius: 14px;
    color: white;
}}

.stats span {{
    background: white;
    color: #333;
    padding: 6px 16px;
    border-radius: 22px;
    font-size: 14px;
}}

textarea {{
    width: 100%;
    height: 220px;
    border-radius: 10px;
    border: 2px solid #3f51b5;
    padding: 14px;
    font-size: 15px;
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
    <div>
      <span>Words: <b id="words">0</b></span>
      <span>Characters: <b id="chars">0</b></span>
    </div>
  </div>

  <textarea id="req" oninput="updateCount()"
  placeholder="System must support biometric login for mobile app..."></textarea>

  <form method="get">
    <input type="hidden" name="reqText" id="hiddenText">
    <button onclick="
      document.getElementById('hiddenText').value =
      document.getElementById('req').value;">
      ✨ Generate
    </button>
  </form>

  {"<div class='output'>" + st.session_state.result + "</div>" if st.session_state.result else ""}
</div>

</body>
</html>
""",
height=950,
scrolling=True,
)
