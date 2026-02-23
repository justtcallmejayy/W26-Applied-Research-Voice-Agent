

"""
src.app.dashboard.dashboard

Interactive Streamlit dashboard for the voice agent onboarding prototype.
"""

import sys
import os
import logging

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

