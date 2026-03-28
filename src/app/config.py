
"""
config.py

Central configuration file for the voice agent prototype.
All tuneable constants are defined here to provide a single place to adjust agent behavior.

NOTE: To switch providers, update the ENGINES dict below, no changes needed anywhere else.
"""


# ===================================================================================
# AUDIO SETTINGS
# ===================================================================================
RECORDING_DURATION = 5
AUDIO_SAMPLE_RATE = 16000
ENERGY_THRESHOLD = 0.01


# ===================================================================================
# CONVERSATION HISTORY
# ===================================================================================
MAX_HISTORY_LENGTH = 12


# ===================================================================================
# OPENAI LLM PARAMETERS
# ===================================================================================
LLM_MAX_TOKENS = 150
LLM_TEMPERATURE = 0.7
LLM_PRESENCE_PENALTY = 0.5
LLM_FREQUENCY_PENALTY = 0.2


# ===================================================================================
# OPENAI TTS PARAMETERS
# ===================================================================================
# Available voices: alloy, echo, fable, onyx, nova, shimmer
TTS_VOICE = "alloy"
TTS_MODEL = "tts-1"


# ===================================================================================
# GROQ MODEL CONSTANTS
# ===================================================================================
GROQ_MODEL = "llama-3.1-8b-instant"


# ===================================================================================
# OPENROUTER MODEL AND PARAMETER CONSTANTS
# ===================================================================================
OPENROUTER_FREE_MODELS = {
    "stepfun-flash":      "stepfun/step-3.5-flash:free",
    "nemotron-9b":        "nvidia/nemotron-nano-9b-v2:free",        # May return None
    "nemotron-30b":       "nvidia/nemotron-3-nano-30b-a3b:free",
    "nemotron-120b":      "nvidia/nemotron-3-super-120b-a12b:free",
    "glm-4.5-air":        "z-ai/glm-4.5-air:free",
    "lfm-instruct":    "liquid/lfm-2.5-1.2b-instruct:free",
    "trinity-large":   "arcee-ai/trinity-large-preview:free",
}
OPENROUTER_MODEL = OPENROUTER_FREE_MODELS["stepfun-flash"]


# ===================================================================================
# ONBOARDING FIELDS
# ===================================================================================
ONBOARDING_FIELDS = [
    "name",
    "employment_status",
    "skills",
    "education",
    "experience",
    "job_preferences"
]


# ===================================================================================
# SYSTEM PROMPT
# ===================================================================================
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


# ===================================================================================
# ENGINE CONFIGURATION - Swap providers by changing dotted paths below
# ===================================================================================

# Cloud
ENGINES = {
    "stt": "core.engines.stt.whisper_api.WhisperAPIEngine",
    "llm": "core.engines.llm.openai_llm.OpenAILLMEngine",
    "tts": "core.engines.tts.openai_tts.OpenAITTSEngine",
}

# Local
# ENGINES = {
#     "stt": "core.engines.stt.whisper_local.WhisperLocalEngine",
#     "llm": "core.engines.llm.ollama_llm.OllamaLLMEngine",
#     "tts": "core.engines.tts.gtts_tts.GTTSEngine",
# }

# Hybrid (Groq LLM + local STT/TTS)
# ENGINES = {
#     "stt": "core.engines.stt.whisper_local.WhisperLocalEngine",
#     "llm": "core.engines.llm.groq_llm.GroqLLMEngine",
#     "tts": "core.engines.tts.gtts_tts.GTTSEngine",
# }

# ENGINES = {
#     "stt": "core.engines.stt.whisper_api.WhisperAPIEngine",
#     "llm": "core.engines.llm.openrouter_llm.OpenRouterLLMEngine",
#     "tts": "core.engines.tts.openai_tts.OpenAITTSEngine",
# }

