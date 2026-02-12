

"""
src.app.dashboard.dashboard

The core dashboard module for the 
"""


import re
import streamlit as st
import logging

# Initialize logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
    handlers=[
        logging.FileHandler('src/app/logs/dashboard.log'),  # to file
        logging.StreamHandler()                     # to console
    ]
)


# ---------------- Page config ----------------
st.set_page_config(
    page_title="AI Voice Assistant Dashboard",
    page_icon="🎙️",
    layout="wide",
)

# ---------------- Dark Dashboard Style ----------------
st.markdown(
    """
    <style>
      .stApp {
        background: radial-gradient(circle at 20% 10%, #1c2430 0%, #0b0f14 45%, #070a0e 100%);
        color: #e8eef7;
      }

      header {visibility: hidden;}
      footer {visibility: hidden;}

      section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(24,30,40,0.95) 0%, rgba(13,16,22,0.95) 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
      }

      .dash-title {
        font-size: 44px;
        font-weight: 800;
        margin: 6px 0 10px 0;
      }

      .muted {
        color: rgba(232,238,247,0.65);
      }

      .panel {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
      }

      textarea, input {
        background: rgba(255,255,255,0.03) !important;
        color: #e8eef7 !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
      }

      .record-btn > button {
        background: linear-gradient(90deg, #ff4b4b 0%, #ff3d63 100%) !important;
        border: none !important;
        color: #0b0f14 !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
      }

      .response-paragraph {
        color: rgba(64,167,255,0.95);
        font-weight: 600;
        line-height: 1.6;
        white-space: pre-wrap;
      }

      .thin-divider {
        height: 1px;
        background: rgba(255,255,255,0.10);
        margin: 14px 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Session State ----------------
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

if "response" not in st.session_state:
    st.session_state.response = "Response will appear here after voice input."

if "name" not in st.session_state:
    st.session_state.name = ""


# ---------------- Extract Name ----------------
def extract_name(text: str) -> str:
    """
    Extract name if user says:
    name: John Doe
    """
    match = re.search(r"name\s*:\s*(.*)", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


# ---------------- Main UI ----------------
st.markdown('<div class="dash-title">AI Voice Assistant Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="muted">Voice input → response → name field → submit</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

# ---------------- Voice + Response Layout ----------------
left, right = st.columns(2, gap="large")

with left:
    st.markdown('<div class="panel"><h3>Voice Input</h3>', unsafe_allow_html=True)

    st.markdown('<div class="record-btn">', unsafe_allow_html=True)
    record = st.button("Record & Ask", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if record:
        st.session_state.response = "🎙️ Recording started (demo). Paste transcript below."

    st.caption("Paste transcript here (simulates voice-to-text):")

    st.session_state.voice_text = st.text_area(
        "",
        value=st.session_state.voice_text,
        height=140,
        placeholder="Example: name: Rishyu Babariya",
    )

    if st.button("Process Voice Input", use_container_width=True):
        st.session_state.response = (
            "Thanks! I captured your voice input and extracted your name below."
        )

        extracted = extract_name(st.session_state.voice_text)
        if extracted:
            st.session_state.name = extracted

    st.markdown("</div>", unsafe_allow_html=True)


with right:
    st.markdown('<div class="panel"><h3>Response</h3>', unsafe_allow_html=True)

    st.markdown(
        f"<div class='response-paragraph'>{st.session_state.response}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------- Name Field + Submit ----------------
st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

st.markdown('<div class="panel"><h3>Extracted Information</h3>', unsafe_allow_html=True)

st.markdown("**Name**")
st.session_state.name = st.text_input("", value=st.session_state.name)

submit = st.button("Submit")

if submit:
    st.success("Submitted successfully!")
    st.json({"name": st.session_state.name})

st.markdown("</div>", unsafe_allow_html=True)
