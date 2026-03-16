
"""
src.app.dashboard.dashboard

Interactive Streamlit dashboard for the voice agent onboarding prototype.
Uses the OnboardingPipeline and engine layer, provider is controlled via config.py.
"""

import sys
import logging
import streamlit as st
from pathlib import Path

# Ensure the app directory is in the path for internal imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    ONBOARDING_FIELDS,
    SYSTEM_PROMPT,
    RECORDING_DURATION,
    AUDIO_SAMPLE_RATE,
    ENERGY_THRESHOLD,
    ENGINES
)
from core.pipeline import load_engine, OnboardingPipeline

st.set_page_config(page_title="Voice Agent Dashboard", layout="wide")

def init_state():
    """Initialize Streamlit session state with default values."""
    defaults = {
        "pipeline": None,
        "session_active": False,
        "turn": 0,
        "status": "idle",
        "error": None,
        "last_transcript": "",
        "last_response": "",
        "pipeline_params": {},
        "log_lines": [],
        "log_handler_attached": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


class DashboardLogHandler(logging.Handler):
    """Captures log messages from the entire app into session state for display."""
    def emit(self, record):
        try:
            line = self.format(record)
            if "log_lines" in st.session_state:
                st.session_state["log_lines"].append(line)
                if len(st.session_state["log_lines"]) > 100:
                    st.session_state["log_lines"] = st.session_state["log_lines"][-100:]
        except Exception:
            self.handleError(record)


if not st.session_state.log_handler_attached:
    root_logger = logging.getLogger()
    dash_handler = DashboardLogHandler()
    dash_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"))
    root_logger.addHandler(dash_handler)
    root_logger.setLevel(logging.INFO)
    st.session_state.log_handler_attached = True
    logging.info("Dashboard log handler attached.")


def build_pipeline(recording_duration: int, sample_rate: int) -> OnboardingPipeline:
    """Instantiate the OnboardingPipeline using engines defined in config.py."""
    stt = load_engine(ENGINES["stt"])
    llm = load_engine(ENGINES["llm"])
    tts = load_engine(ENGINES["tts"])
    return OnboardingPipeline(
        stt=stt,
        llm=llm,
        tts=tts,
        system_prompt=SYSTEM_PROMPT,
        onboarding_fields=ONBOARDING_FIELDS,
        recording_duration=recording_duration,
        sample_rate=sample_rate,
        energy_threshold=ENERGY_THRESHOLD,
    )


st.title("Voice Agent Onboarding Dashboard")
main_col, debug_col = st.columns([3, 2])

# ==========================================
# SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.header("Configuration")

    st.divider()
    st.subheader("Audio")
    recording_duration = st.slider(
        "Recording duration (s)", 3, 15, RECORDING_DURATION, 1,
        disabled=st.session_state.session_active,
        help="How long to record each time you press Record.",
    )
    sample_rate = st.selectbox(
        "Sample rate (Hz)", [16000, 22050, 44100],
        index=[16000, 22050, 44100].index(AUDIO_SAMPLE_RATE),
        disabled=st.session_state.session_active,
    )

    st.divider()
    st.subheader("Active engines")
    st.markdown(f"- **STT:** `{ENGINES['stt'].split('.')[-1]}`")
    st.markdown(f"- **LLM:** `{ENGINES['llm'].split('.')[-1]}`")
    st.markdown(f"- **TTS:** `{ENGINES['tts'].split('.')[-1]}`")
    st.caption("To switch providers, update ENGINES in config.py")

    st.divider()
    st.subheader("Onboarding fields")
    for f in ONBOARDING_FIELDS:
        st.markdown(f"- `{f}`")

    st.divider()

    if not st.session_state.session_active:
        if st.button("▶ Start session", type="primary", use_container_width=True):
            st.session_state.log_lines = []
            try:
                with st.spinner("Loading models..."):
                    pipeline = build_pipeline(recording_duration, sample_rate)

                st.session_state.pipeline = pipeline
                st.session_state.session_active = True
                st.session_state.turn = 0
                st.session_state.status = "ready"
                st.session_state.error = None

                st.session_state.pipeline_params = {
                    "stt": ENGINES["stt"].split(".")[-1],
                    "llm": ENGINES["llm"].split(".")[-1],
                    "tts": ENGINES["tts"].split(".")[-1],
                    "recording_duration": recording_duration,
                    "sample_rate": sample_rate,
                    "energy_threshold": ENERGY_THRESHOLD,
                }

                opening = pipeline._generate("Begin the onboarding conversation.")
                pipeline._speak(opening)
                st.session_state.last_response = opening

            except Exception as e:
                st.session_state.error = str(e)
                st.session_state.status = "error"
                st.session_state.session_active = False
            st.rerun()
    else:
        if st.button("⏹ End session", use_container_width=True):
            st.session_state.session_active = False
            st.session_state.pipeline = None
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

    pipeline = st.session_state.pipeline
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
    for msg in pipeline.conversation_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.divider()

    if current_turn >= total_turns:
        st.success("Onboarding complete — all fields collected.")
        st.stop()

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
                audio_data = pipeline.record_audio()
                recorded_path = pipeline.save_audio(audio_data)

                st.session_state.status = "transcribing"
                user_text = pipeline.stt.transcribe(recorded_path)
                pipeline.cleanup_file(recorded_path)
                st.session_state.last_transcript = user_text

                if not user_text.strip():
                    raise ValueError("Nothing was transcribed. Please try again.")

                st.session_state.status = "generating"
                response = pipeline._generate(user_text)
                st.session_state.last_response = response

                st.session_state.status = "speaking"
                pipeline._speak(response)

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
# DEBUG PANEL
# ==========================================
with debug_col:
    st.header("Debug")

    with st.expander("Session parameters", expanded=True):
        params = st.session_state.get("pipeline_params", {})
        for k, v in params.items():
            st.markdown(f"**{k}:** `{v}`")

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
        if st.session_state.pipeline:
            st.json(st.session_state.pipeline.conversation_history)

    with st.expander("Runtime log", expanded=True):
        log_lines = st.session_state.get("log_lines", [])
        if log_lines:
            st.code("\n".join(log_lines), language=None)
        else:
            st.caption("Waiting for logs... (Interaction required)")

