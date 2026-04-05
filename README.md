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

# 3. Run the voice agent (CLI)
python3 src/app/main.py

# 4. Run the dashboard (optional)
streamlit run src/app/dashboard/dashboard.py

# 5. Run the REST API (optional)
cd src && python3 api/main.py
```

> To switch providers, edit the `ENGINES` dict in `src/app/config.py`. Supports OpenAI, OpenRouter, local Ollama, and on-device Whisper — no code changes required to swap.

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
└── src/
    ├── api/
    │   ├── __init__.py
    │   └── main.py                    # FastAPI REST API wrapper
    └── app/
        ├── main.py                    # CLI entry point
        ├── config.py                  # central configuration — engines, fields, prompt, audio
        ├── core/
        │   ├── pipeline.py            # OnboardingPipeline — provider-agnostic conversation loop
        │   └── engines/
        │       ├── base.py            # abstract STTEngine, LLMEngine, TTSEngine interfaces
        │       ├── llm/
        │       │   ├── openai_llm.py      # OpenAILLMEngine (GPT-4)
        │       │   ├── ollama_llm.py      # OllamaLLMEngine (gemma3:1b)
        │       │   ├── groq_llm.py        # GroqLLMEngine (Groq API)
        │       │   └── openrouter_llm.py  # OpenRouterLLMEngine (free model set)
        │       ├── stt/
        │       │   ├── whisper_api.py     # WhisperAPIEngine (OpenAI Whisper-1)
        │       │   └── whisper_local.py   # WhisperLocalEngine (on-device)
        │       └── tts/
        │           ├── openai_tts.py      # OpenAITTSEngine (TTS-1)
        │           └── gtts_tts.py        # GTTSEngine (gTTS)
        ├── dashboard/
        │   └── dashboard.py           # Streamlit dashboard
        └── utils/
            └── logger.py
tests/
    ├── conftest.py                    # sys.path setup for all tests
    ├── audio/                         # gitignored audio fixtures for integration tests
    │   └── test_audio.py              # helper script to record test audio
    ├── unit/
    │   ├── test_pipeline.py           # unit tests for OnboardingPipeline (no API calls)
    │   ├── test_api.py                # unit tests for the REST API wrapper
    │   └── test_openrouter.py         # unit tests for OpenRouterLLMEngine
    ├── integration/
    │   ├── test_pipelines_sess.py     # integration tests with pre-recorded audio (pipeline)
    │   └── test_api_sess.py           # integration tests with pre-recorded audio (API)
    └── old/                           # legacy tests kept for reference
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
| 5. Generate | Send transcription + current field + history to the configured LLM engine |
| 6. Synthesise | Convert response text to audio via the configured TTS engine |
| 7. Play | Play audio through the user's speakers via pygame |
| 8. Cleanup | Delete both temporary audio files |

The current field is injected as a context prefix on each turn for explicit field enforcement. The turn count is driven by `ONBOARDING_FIELDS` in `config.py`. Provider selection is controlled entirely by the `ENGINES` dict in `config.py` — no code changes required to swap STT, LLM, or TTS.

---

## REST API

The FastAPI wrapper exposes the pipeline over HTTP for frontend integration.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/session/start` | Start session, receive opening audio |
| `POST` | `/session/{id}/turn` | Upload audio, receive response audio |
| `POST` | `/session/{id}/confirm` | Submit confirmation, close session |
| `DELETE` | `/session/{id}` | End session |
| `GET` | `/health` | Engine config and session status |

Interactive API docs: `http://localhost:8000/docs`

---

## Tech Stack

| Concern | Cloud engines | Local engines |
|---------|--------------|---------------|
| LLM | OpenAI (`gpt-4`), OpenRouter (free model set) | Ollama (`gemma3:1b`) |
| Speech-to-text | OpenAI Whisper-1 API | `openai-whisper` (on-device) |
| Text-to-speech | OpenAI TTS-1 API | gTTS (requires internet) |
| Audio recording | `sounddevice` + `soundfile` | same |
| Audio playback | `pygame.mixer` | same |
| REST API | `fastapi` + `uvicorn` | same |
| Dashboard | `streamlit` | same |
| Python | 3.10–3.13 | same |

FFmpeg is required for local Whisper transcription.

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `python3 src/app/main.py` | Run the voice agent (CLI) |
| `streamlit run src/app/dashboard/dashboard.py` | Run the dashboard |
| `cd src && python3 api/main.py` | Run the REST API |
| `python3 -m venv venv` | Create virtual environment |
| `source venv/bin/activate` | Activate virtual environment |
| `pip install -r requirements.txt` | Install dependencies |
| `deactivate` | Deactivate virtual environment |
| `pytest tests/unit/ -v` | Run unit tests (no API keys needed) |
| `pytest tests/integration/ -v -s` | Run integration tests (requires keys + audio fixtures) |
| `pytest tests/ -v` | Run all tests |
| `python tests/audio/record_fixtures.py` | Record audio fixtures for integration tests |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design, pipeline, API, and component overview |
| [Decisions](docs/DECISIONS.md) | Key technical decisions and reasoning |
| [Setup](docs/SETUP.md) | Detailed setup, configuration, and troubleshooting |
| [Test Results](docs/test-results/README.md) | All test reports and current performance metrics |
