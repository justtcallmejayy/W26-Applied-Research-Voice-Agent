# W26-Applied-Research-Voice-Agent
Voice Agent for Candidate Onboarding & Career Guidance
> Applied Research 1, Winter 2026

---

## Quick Start

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the voice agent
python3 src/app/main.py

# 4. Run the dashboard (optional)
streamlit run src/app/dashboard/dashboard.py
```

> To switch providers, edit the `ENGINES` dict in `src/app/config.py`. Current default uses OpenRouter for LLM. You can also switch to OpenAI, Groq, or local Ollama.

---

## Project Structure

```
W26-Applied-Research-Voice-Agent/
├── README.md
├── requirements.txt                   # pip dependencies
├── pyproject.toml                     # project config and Python version
├── docs/
│   ├── ARCHITECTURE.md                # system design and pipeline overview
│   ├── DECISIONS.md                   # key technical decisions and reasoning
│   ├── SETUP.md                       # detailed setup and troubleshooting
│   └── test-results/                  # structured test reports
├── src/
│   └── app/
│       ├── main.py                    # CLI entry point
│       ├── config.py                  # central configuration — engines, fields, prompt, audio
│       ├── core/
│       │   ├── pipeline.py            # OnboardingPipeline — provider-agnostic conversation loop
│       │   └── engines/
│       │       ├── base.py            # abstract STTEngine, LLMEngine, TTSEngine interfaces
│       │       ├── llm/
│       │       │   ├── openai_llm.py  # OpenAILLMEngine (GPT-4)
│       │       │   └── ollama_llm.py  # OllamaLLMEngine (gemma3:1b)
│       │       ├── stt/
│       │       │   ├── whisper_api.py # WhisperAPIEngine (OpenAI Whisper-1)
│       │       │   └── whisper_local.py # WhisperLocalEngine (on-device)
│       │       └── tts/
│       │           ├── openai_tts.py  # OpenAITTSEngine (TTS-1)
│       │           └── gtts_tts.py    # GTTSEngine (gTTS)
│       ├── dashboard/
│       │   └── dashboard.py           # Streamlit dashboard
│       └── utils/
│           └── logger.py
└── tests/
    ├── conftest.py
    ├── test_voice_agent.py            # legacy tests (broken — imports removed agent/)
    ├── stress_test.py
    └── openrouter_test.py             # OpenRouter API key validation script
```

---

## Onboarding Pipeline

Each conversational turn follows this pipeline:

| Step | Description |
|------|-------------|
| 1. Record | Capture audio from the user's microphone (5s default) |
| 2. Save | Write audio to a temporary `.wav` file on disk |
| 3. Energy check | Compute RMS amplitude — skip turn if below threshold (0.01) |
| 4. Transcribe | Convert `.wav` to text via the configured STT engine |
| 5. Generate | Send transcription + history to the configured LLM engine |
| 6. Synthesise | Convert response text to audio via the configured TTS engine |
| 7. Play | Play audio through the user's speakers via pygame |
| 8. Cleanup | Delete both temporary audio files |

The turn count is driven by `ONBOARDING_FIELDS` in `config.py`. Provider selection is controlled entirely by the `ENGINES` dict in `config.py` — no code changes required to swap STT, LLM, or TTS.

---

## Tech Stack

| Concern | Cloud engines | Local engines |
|---------|--------------|---------------|
| LLM | OpenAI (`gpt-4`), OpenRouter (free model set), Groq (`llama-3.1-8b-instant`) | Ollama (`gemma3:1b`) |
| Speech-to-text | OpenAI Whisper-1 API | `openai-whisper` (on-device) |
| Text-to-speech | OpenAI TTS-1 API | gTTS (requires internet) |
| Audio recording | `sounddevice` + `soundfile` | same |
| Audio playback | `pygame.mixer` | same |
| Dashboard | `streamlit` | same |
| Python | 3.10–3.13 | same |

FFmpeg is required for local Whisper transcription.

For Groq LLM mode, set `GROQ_API_KEY` in `src/app/.env`.

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `python3 src/app/main.py` | Run the voice agent |
| `streamlit run src/app/dashboard/dashboard.py` | Run the dashboard |
| `python3 -m venv venv` | Create virtual environment |
| `source venv/bin/activate` | Activate virtual environment |
| `pip install -r requirements.txt` | Install dependencies |
| `deactivate` | Deactivate virtual environment |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design, pipeline, and component overview |
| [Decisions](docs/DECISIONS.md) | Key technical decisions and reasoning |
| [Setup](docs/SETUP.md) | Detailed setup, configuration, and troubleshooting |
| [Test Results](docs/test-results/README.md) | All test reports and current performance metrics |

