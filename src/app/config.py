
"""
config.py

Central configuration file for the voice agent prototype.
All tuneable constants are defined here to provide a single place to adjust agent behavior.

NOTE: This file is intended to replace onboarding_config.py.
"""

# Agent selection
USE_LOCAL = True 

# Audio settings
RECORDING_DURATION = 5          # seconds
AUDIO_SAMPLE_RATE = 16000       # Hz
ENERGY_THRESHOLD = 0.01         # Threshold for detecting silent audio

# Models
LOCAL_WHISPER_MODEL = "base"
OLLAMA_MODEL = "gemma3:1b"

# Conversation history
MAX_HISTORY_LENGTH = 8

# Onboarding fields
ONBOARDING_FIELDS = [
    "name",
    "employment_status",
    "skills",
    "education",
    "experience",
    "job_preferences"
]

# System prompt
fields_list = ", ".join(ONBOARDING_FIELDS)
SYSTEM_PROMPT = f"""You are a professional voice assistant helping users complete job onboarding.
Your goal is to collect the following information in this exact order: {fields_list}.

Conversation rules:
- Ask one question at a time, then wait for the user to respond
- Acknowledge each answer briefly, then move to the next field in order
- Keep every response short and conversational — this is a voice interaction
- Use plain letters, numbers, and punctuation only in every response

Field questions to ask in order:
1. name - "What is your full name?"
2. employment_status — "Are you currently employed, unemployed, or a student?"
3. skills — "What technical or professional skills do you have?"
4. education — "What is your highest level of education, including any degrees or diplomas completed or in progress?"
5. experience — "Can you describe your professional work experience or any internships and co-op placements you have completed?"
6. job_preferences — "What type of role or industry are you interested in?"

After collecting all six fields:
- Read back each field and the answer the user gave
- End with exactly: Does everything look correct?
- Wait for the user to confirm before ending the session"""

