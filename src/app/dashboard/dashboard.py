
"""
src.app.dashboard.dashboard

Interactive Streamlit dashboard for the voice agent onboarding prototype.
"""

import sys
import logging
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Ensure the app directory is in the path for internal imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from utils.logger import setup_logger
    from agent.onboarding_config import ONBOARDING_FIELDS, SYSTEM_PROMPT
except ImportError:
    # Fallback placeholders for localized testing
    setup_logger = None
    ONBOARDING_FIELDS = ["name", "employment_status", "skills", "experience", "education", "job_preferences"]
    SYSTEM_PROMPT = "You are a voice assistant..."


st.set_page_config(page_title="Voice Agent Dashboard", layout="wide")


def init_state():
    """Initialize Streamlit session state with default values."""
    defaults = {
        "agent": None,
        "agent_type": None,
        "session_active": False,
        "turn": 0,
        "status": "idle",
        "error": None,
        "last_transcript": "",
        "last_response": "",
        "agent_params": {},
        "log_lines": [],
        "log_handler_attached": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

class DashboardLogHandler(logging.Handler):
    """Custom logging handler that captures log messages from the entire app into session state."""
    def emit(self, record):
        try:
            line = self.format(record)
            # We use a list in session state to store log lines
            if "log_lines" in st.session_state:
                st.session_state["log_lines"].append(line)
                # Keep buffer manageable (last 100 lines)
                if len(st.session_state["log_lines"]) > 100:
                    st.session_state["log_lines"] = st.session_state["log_lines"][-100:]
        except Exception:
            self.handleError(record)

if not st.session_state.log_handler_attached:
    root_logger = logging.getLogger()
    dash_handler = DashboardLogHandler()
    dash_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"))
    root_logger.addHandler(dash_handler)
    # Ensure the level is set to capture info
    root_logger.setLevel(logging.INFO)
    st.session_state.log_handler_attached = True
    logging.info("Dashboard Log Handler successfully attached to Root Logger.")


def build_local_agent(whisper_model, ollama_model, recording_duration, sample_rate):
    """Create a LocalVoiceAgent with specified models and audio settings."""
    from agent.local_voice_agent import LocalVoiceAgent
    return LocalVoiceAgent(
        recording_duration=recording_duration,
        sample_rate=sample_rate,
        whisper_model=whisper_model,
        ollama_model=ollama_model,
    )

def build_cloud_agent(recording_duration, sample_rate):
    """Create a VoiceAgent using OpenAI services"""
    from openai import OpenAI
    load_dotenv()
    from agent.voice_agent import VoiceAgent
    return VoiceAgent(
        client=OpenAI(),
        recording_duration=recording_duration,
        sample_rate=sample_rate,
    )

st.title("Voice Agent Onboarding Dashboard")
st.caption("Onboarding prototype - browser interface")
main_col, debug_col = st.columns([3, 2])

# ==========================================
# SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.header("Configuration")
    agent_choice = st.radio(
        "Agent",
        ["Local (Ollama + Whisper)", "Cloud (OpenAI)"],
        disabled=st.session_state.session_active,
    )
    use_local = agent_choice.startswith("Local")

    st.divider()
    st.subheader("Audio")
    
    recording_duration = st.slider(
        "Recording duration (s)", 3, 15, 5, 1,
        disabled=st.session_state.session_active,
        help="How long to record each time you press Record.",
    )
    sample_rate = st.selectbox(
        "Sample rate (Hz)", [16000, 22050, 44100],
        disabled=st.session_state.session_active,
    )

    if use_local:
        st.divider()
        st.subheader("Local Models")
        whisper_model = st.selectbox(
            "Whisper model", ["base", "small", "medium", "large"],
            disabled=st.session_state.session_active,
        )
        ollama_model = st.text_input(
            "Ollama model", value="gemma3:4b",
            disabled=st.session_state.session_active,
        )
    else:
        whisper_model = "base"
        ollama_model = "—"
        st.divider()
        st.info("OpenAI key is read from `.env` → `OPENAI_API_KEY`.")

    st.divider()
    st.subheader("Onboarding fields")
    for f in ONBOARDING_FIELDS:
        st.markdown(f"- `{f}`")

    st.divider()

    # Session Lifecycle Toggle
    if not st.session_state.session_active:
        if st.button("▶ Start session", type="primary", use_container_width=True):
            st.session_state.log_lines = []
            try:
                with st.spinner("Loading models..."):
                    agent = (
                        build_local_agent(whisper_model, ollama_model, recording_duration, sample_rate)
                        if use_local
                        else build_cloud_agent(recording_duration, sample_rate)
                    )

                st.session_state.agent = agent
                st.session_state.agent_type = "local" if use_local else "cloud"
                st.session_state.session_active = True
                st.session_state.turn = 0
                st.session_state.status = "ready"
                st.session_state.error = None
                
                st.session_state.agent_params = {
                    "agent_class": "LocalVoiceAgent" if use_local else "VoiceAgent",
                    "whisper": whisper_model if use_local else "whisper-1",
                    "llm": ollama_model if use_local else "gpt-4",
                }

                opening = agent.generate_response("Begin the onboarding conversation.")
                speech_path = agent.text_to_speech(opening)
                agent.play_audio(speech_path)
                agent.cleanup_file(speech_path)
                st.session_state.last_response = opening

            except Exception as e:
                st.session_state.error = str(e)
                st.session_state.status = "error"
                st.session_state.session_active = False
            st.rerun()
    else:
        if st.button("⏹ End session", use_container_width=True):
            st.session_state.session_active = False
            st.session_state.agent = None
            st.session_state.status = "idle"
            st.rerun()

# ==========================================
# MAIN CONVERSATION PANEL
# ==========================================
with main_col:
    if st.session_state.error and not st.session_state.session_active:
        st.error(f"**Failed to start session:** {st.session_state.error}")

    if not st.session_state.session_active:
        st.info("Configure agent in the sidebar and press **▶ Start session** to begin.")
        st.stop()

    agent = st.session_state.agent
    total_turns = len(ONBOARDING_FIELDS)
    current_turn = st.session_state.turn

    display_turn = min(current_turn + 1, total_turns)
    progress_val = min(current_turn / total_turns, 1.0)
    
    st.progress(
        progress_val,
        text=(
            f"Turn {display_turn} of {total_turns} — "
            f"collecting: `{ONBOARDING_FIELDS[min(current_turn, total_turns - 1)]}`"
            if current_turn < total_turns else "Onboarding Complete"
        ),
    )

    st.subheader("Conversation")
    history = agent.conversation_history
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    st.divider()

    if current_turn >= total_turns:
        st.success("Onboarding complete — all fields collected.")
        st.stop()
    
    # Status & Recording Logic
    status = st.session_state.status
    status_display = {
        "ready":        ("READY", "Press **Record** to answer."),
        "recording":    ("RECORDING", f"Speak now ({recording_duration}s)..."),
        "transcribing": ("PROCESSING", "Transcribing..."),
        "generating":   ("PROCESSING", "Agent is thinking..."),
        "speaking":     ("PLAYING", "Agent is speaking..."),
        "error":        ("ERROR", f"{st.session_state.error}"),
    }
    icon, label = status_display.get(status, ("IDLE", status))
    st.markdown(f"**{icon}**: {label}")

    btn_col, retry_col = st.columns([1, 2])
    with btn_col:
        if st.button("Record", disabled=(status != "ready"), type="primary", use_container_width=True):
            try:
                st.session_state.status = "recording"
                audio_data = agent.record_audio()
                recorded_path = agent.save_audio(audio_data)

                st.session_state.status = "transcribing"
                user_text = agent.transcribe_audio(recorded_path)
                st.session_state.last_transcript = user_text

                if not user_text.strip():
                    raise ValueError("Nothing was transcribed. Please try again.")

                st.session_state.status = "generating"
                response = agent.generate_response(user_text)
                st.session_state.last_response = response

                st.session_state.status = "speaking"
                speech_path = agent.text_to_speech(response)
                agent.play_audio(speech_path)

                st.session_state.turn += 1
                st.session_state.status = "ready"
                st.session_state.error = None
            except Exception as e:
                st.session_state.error = str(e)
                st.session_state.status = "error"
            st.rerun()

    with retry_col:
        if status == "error" and st.button("↩ Retry turn", use_container_width=True):
            st.session_state.status = "ready"
            st.session_state.error = None
            st.rerun()

# ==========================================
# DEBUG PANEL (OBSERVABILITY)
# ==========================================
with debug_col:
    st.header("Debug")
    
    with st.expander("Session parameters", expanded=True):
        params = st.session_state.get("agent_params", {})
        for k, v in params.items():
            st.markdown(f"**{k}:** `{v}`")
    
    with st.expander("Turn tracker", expanded=True):
        if st.session_state.session_active:
            for i, field in enumerate(ONBOARDING_FIELDS):
                # Using text labels instead of emojis
                if i < st.session_state.turn:
                    st.markdown(f"[DONE] Turn {i + 1} — `{field}`")
                elif i == st.session_state.turn:
                    st.markdown(f"[ACTIVE] **Turn {i + 1} — `{field}`**")
                else:
                    st.markdown(f"[PENDING] Turn {i + 1} — `{field}`")
        else:
            st.caption("No active session.")
    
    with st.expander("System prompt", expanded=False):
        st.code(SYSTEM_PROMPT, language=None)
    
    with st.expander("Raw conversation history (JSON)", expanded=False):
        if st.session_state.agent:
            st.json(st.session_state.agent.conversation_history)
    
    with st.expander("Runtime log", expanded=True):
        log_lines = st.session_state.get("log_lines", [])
        if log_lines:
            st.code("\n".join(log_lines), language=None)
        else:
            st.caption("Waiting for logs... (Interaction required)")