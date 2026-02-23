

"""
src.app.dashboard.dashboard

Interactive Streamlit dashboard for the voice agent onboarding prototype.
"""

import sys
import os
import logging
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from dotenv import load_dotenv
from agent.onboarding_config import ONBOARDING_FIELDS, SYSTEM_PROMPT

st.set_page_config(
    page_title="Voice Agent Dashboard",
    layout="wide"
)


def init_state():
    """Initialize Streamlit session state with default values for agent control and tracking."""
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

# Logging to file and console
log_file = Path(__file__).parent.parent / "logs" / "dashboard.log"
log_file.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

class DashboardLogHandler(logging.Handler):
    """Custom logging handler that captures log messages in session state for UI display."""
    def emit(self, record):
        line = self.format(record)
        st.session_state["log_lines"].append(line)

        if len(st.session_state["log_lines"]) > 200:    # Keep only last 200 log lines
            st.session_state["log_lines"] = st.session_state["log_lines"][-200:]

# Attach the custom log handler if not already attached
if not st.session_state.log_handler_attached:
    handler = DashboardLogHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(filename)s - %(funcName)s()"))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
    st.session_state.log_handler_attached = True


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
    """Create a VoiceAgent using OpenAI services (API key from .env)."""
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



# Configuration Sidebar
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
            "Ollama model", value="gemma3:1b",
            disabled=st.session_state.session_active,
        )
    else:
        whisper_model = "base"
        ollama_model = "—"
        st.divider()
        st.info("OpenAI key is read from `.env` → `OPENAI_API_KEY`.")

    st.divider()
    st.subheader("Onboarding fields")
    st.caption("Edit in `onboarding_config.py`")
    for f in ONBOARDING_FIELDS:
        st.markdown(f"- `{f}`")

    st.divider()

    # Start or end the session based on current state
    if not st.session_state.session_active:
        if st.button("▶ Start session", type="primary", use_container_width=True):
            st.session_state.log_lines = []
            try:
                with st.spinner("Loading models…"):
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
                st.session_state.last_transcript = ""
                st.session_state.last_response = ""
                st.session_state.agent_params = {
                    "agent_class": "LocalVoiceAgent" if use_local else "VoiceAgent",
                    "recording_duration": f"{recording_duration}s",
                    "sample_rate": f"{sample_rate} Hz",
                    "whisper_model": whisper_model if use_local else "whisper-1 (API)",
                    "llm": ollama_model if use_local else "gpt-4",
                    "tts": "gTTS" if use_local else "OpenAI TTS (alloy)",
                    "total_turns": len(ONBOARDING_FIELDS),
                }

                # Opening message (same behaviour as in main.py)
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
            st.session_state.turn = 0
            st.session_state.last_transcript = ""
            st.session_state.last_response = ""
            st.rerun()


# Main Section
with main_col:

    if st.session_state.error and not st.session_state.session_active:
        st.error(f"**Failed to start session:** {st.session_state.error}")

    if not st.session_state.session_active:
        st.info("Configure agent in the sidebar and press **▶ Start session** to begin.")
        st.stop()

    agent = st.session_state.agent
    total_turns = len(ONBOARDING_FIELDS)
    current_turn = st.session_state.turn

    # Progress bar
    st.progress(
        min(current_turn / total_turns, 1.0),
        text=(
            f"Turn {current_turn} of {total_turns} — "
            f"collecting: `{ONBOARDING_FIELDS[min(current_turn, total_turns - 1)]}`"
            if current_turn < total_turns
            else "All fields collected"
        ),
    )

    # Conversation history
    st.subheader("Conversation")
    history = agent.conversation_history
    if not history:
        st.caption("Waiting for session to start...")
    else:
        for msg in history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    st.divider()

    # Session complete
    if current_turn >= total_turns:
        st.success("Onboarding complete — all fields collected.")
        st.stop()
    
    # Status indicator
    status = st.session_state.status
    status_display = {
        "ready":        ("READY", "Press **Record** when you're ready to speak."),
        "recording":    ("RECORDING", f"Recording for {recording_duration}s… speak now!"),
        "transcribing": ("PROCESSING", "Transcribing audio…"),
        "generating":   ("PROCESSING", "Generating response…"),
        "speaking":     ("PLAYING", "Playing response…"),
        "error":        ("ERROR", f"{st.session_state.error}"),
    }
    icon, label = status_display.get(status, ("IDLE", status))
    st.markdown(f"**{icon}**: {label}")

    # Record button and retry button
    btn_col, retry_col = st.columns([1, 2])
    
    with btn_col:
        if st.button(
            "Record",
            disabled=(status != "ready"),
            type="primary",
            use_container_width=True,
        ):
            recorded_path = None 
            speech_path = None 

            try:
                st.session_state.status = "recording"
                audio_data = agent.record_audio()
                recorded_path = agent.save_audio(audio_data)

                st.session_state.status = "transcribing"
                user_text = agent.transcribe_audio(recorded_path)
                st.session_state.last_transcript = user_text

                # Check if transcription is empty or just whitespace
                if not user_text.strip():
                    raise ValueError("Nothing was transcribed, please speak clearly and try again.")

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
            finally:
                if recorded_path:
                    agent.cleanup_file(recorded_path)
                if speech_path:
                    agent.cleanup_file(speech_path)

            st.rerun()

    with retry_col:
        # Show retry button if error occurred
        if status == "error":
            if st.button("↩ Retry turn", use_container_width=True):
                st.session_state.status = "ready"
                st.session_state.error = None
                st.rerun()
    
    # Last turn info
    if st.session_state.last_transcript or st.session_state.last_response:
        with st.expander("Last turn detail"):
            if st.session_state.last_transcript:
                st.markdown("**Transcript (what you said)**")
                st.code(st.session_state.last_transcript, language=None)
            if st.session_state.last_response:
                st.markdown("**Agent response**")
                st.code(st.session_state.last_response, language=None)

# Debugging Section
with debug_col:
    st.header("Debug")
    
    with st.expander("Session parameters", expanded=True):
        params = st.session_state.get("agent_params", {})
        if params:
            for k, v in params.items():
                st.markdown(f"**{k}:** `{v}`")
        else:
            st.caption("No active session.")
    
    with st.expander("Turn tracker", expanded=True):
        if st.session_state.session_active:
            for i, field in enumerate(ONBOARDING_FIELDS):
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
        if st.session_state.session_active and st.session_state.agent:
            history = st.session_state.agent.conversation_history
            st.caption(f"{len(history)} messages in history")
            st.json(history)
        else:
            st.caption("No active session.")
    
    with st.expander("Runtime log", expanded=False):
        log_lines = st.session_state.get("log_lines", [])
        if log_lines:
            st.code("\n".join(log_lines[-50:]), language=None)
        else:
            st.caption("No log output yet.")