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

.header h3 {{
    margin: 0;
    font-weight: 600;
}}

.stats {{
    display: flex;
    gap: 12px;
}}

.stats span {{
    background: white;
    color: #333;
    padding: 6px 16px;
    border-radius: 22px;
    font-size: 14px;
    font-weight: 500;
}}

.tabs {{
    display: flex;
    justify-content: center;
    margin-top: 24px;
    margin-bottom: 10px;
    gap: 80px;
    font-weight: 500;
    color: #555;
}}

.tabs div {{
    cursor: pointer;
}}

textarea {{
    width: 100%;
    height: 220px;
    border-radius: 10px;
    border: 2px solid #3f51b5;
    padding: 14px;
    font-size: 15px;
    resize: none;
}}

textarea:focus {{
    outline: none;
    border: 2px solid #1e88e5;
}}

.buttons {{
    display: flex;
    align-items: center;
    margin-top: 22px;
}}

.left-buttons {{
    display: flex;
    gap: 12px;
}}

.right-buttons {{
    margin-left: auto;
    display: flex;
    gap: 12px;
}}

button {{
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 14px;
    cursor: pointer;
    border: none;
}}

.save {{
    background: #1e88e5;
    color: white;
}}

.regen {{
    background: #5e35b1;
    color: white;
}}

.clear {{
    background: white;
    border: 1px solid #e53935;
    color: #e53935;
}}

.back {{
    background: transparent;
    color: #333;
}}

.generate {{
    background: #3949ab;
    color: white;
}}

.output {{
    white-space: pre-wrap;
    background: #f4f6fa;
    padding: 22px;
    border-radius: 14px;
    margin-top: 30px;
    border: 1px solid #e0e0e0;
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

  <div class="tabs">
    <div style="color:#3f51b5; border-bottom:2px solid #3f51b5;">Text</div>
    <div>File</div>
  </div>

  <textarea id="req" oninput="updateCount()"
  placeholder="System must support biometric login for mobile app..."></textarea>

  <div class="buttons">
    <div class="left-buttons">
      <button class="save">💾 Save Draft</button>
      <button class="regen">🔄 Regenerate</button>
      <button class="clear"
        onclick="document.getElementById('req').value=''; updateCount();">
        ✖ Clear
      </button>
    </div>

    <div class="right-buttons">
      <button class="back">← Back</button>

      <form method="post">
        <input type="hidden" name="reqText"
        value="" id="hiddenText">
        <button class="generate"
          onclick="document.getElementById('hiddenText').value =
          document.getElementById('req').value;">
          ✨ Generate
        </button>
      </form>
    </div>
  </div>

  {"<div class='output'>" + st.session_state.result + "</div>" if st.session_state.result else ""}
</div>

</body>
</html>
""",
height=950,
scrolling=True,
)
height=900,
scrolling=True,
)

