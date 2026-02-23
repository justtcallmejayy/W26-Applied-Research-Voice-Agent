

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

with st.sidebar:
    st.header("Configuration")