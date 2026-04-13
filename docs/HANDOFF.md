# Handoff Document

> Voice Onboarding Assistant Prototype

**Prepared for:** Sahil Gogna, Enabled Talent
**Prepared by:** Brendan Dileo, Dhairya Patel, Jay Choksi, Rishyu Babariya
**Date:** April 2026
**Course:** COMP-10199 Applied Research 1, Winter 2026

---

## Overview

This document summarizes everything delivered as part of the Voice Onboarding Assistant prototype, and provides the information needed to set up, run, and build on the system. The prototype demonstrates the viability of replacing Enabled Talent's traditional form-based candidate onboarding with a voice-based conversational agent that collects six candidate profile fields through natural conversation.

---

## What Was Delivered

| Deliverable | Description |
|-------------|-------------|
| Voice onboarding pipeline | Provider-agnostic OnboardingPipeline with 8 engine implementations across OpenAI, Ollama, Groq, and OpenRouter |
| CLI interface | Terminal-based voice agent for local development and testing |
| Streamlit dashboard | Browser-based debug and audit interface with turn tracker, live logs, and conversation history |
| FastAPI REST API | HTTP interface exposing the pipeline for frontend integration, 5 endpoints, session management, audio upload and response |
| Unit test suite | 21 automated unit tests requiring no API keys, passing in under 1 second |
| Integration test suite | Full 6-turn session tests using pre-recorded audio fixtures |
| 19 structured test reports | Covering all engine configurations from February to April 2026 |
| Documentation | ARCHITECTURE.md, DECISIONS.md, SETUP.md, API.md, and this handoff document |

---

## Repository Access

The repository is hosted at:
**https://github.com/justtcallmejayy/W26-Applied-Research-Voice-Agent**

You should already have access. If not, request access from the repository owner or fork the repository to your own GitHub account. All source code, documentation, and test reports are in the repository. Logs and audio fixtures are gitignored and remain local only, no candidate data is ever committed.

---

## Dependencies

### Runtime Dependencies (API deployment)

For running the REST API in a hosted or server environment, install from `requirements-api.txt`. This is a stripped dependency set that excludes local Whisper and other development-only packages:

```bash
pip install -r requirements-api.txt
```

Key runtime packages:
- `fastapi==0.115.0` — REST API framework
- `uvicorn==0.42.0` — ASGI server
- `openai==1.75.0` — OpenAI API client (Whisper STT + GPT-4 + TTS)
- `groq` — Groq API client (recommended LLM for deployment)
- `gtts==2.5.4` — Google Text-to-Speech
- `soundfile==0.13.1` — Audio energy detection
- `numpy` — Audio data processing
- `python-dotenv==1.1.0` — Environment variable management

### Full Development Dependencies

For running the full system locally including the CLI, dashboard, and local Whisper STT:

```bash
pip install -r requirements.txt
```

This includes everything in `requirements-api.txt` plus:
- `openai-whisper==20250625` — On-device speech transcription (requires FFmpeg)
- `streamlit==1.53.0` — Dashboard framework
- `sounddevice==0.5.1` — Microphone recording
- `pygame>=2.6.1` — Audio playback

### Testing Dependencies

Included in `requirements.txt`:
- `pytest==7.3.1` — Test framework
- `httpx` — HTTP client used by FastAPI TestClient

### System Prerequisites

| Prerequisite | Required for | Install |
|-------------|-------------|---------|
| Python 3.10–3.13 | Everything | https://python.org |
| FFmpeg | Local Whisper STT only | `brew install ffmpeg` (macOS), `sudo apt install ffmpeg` (Linux) |
| Ollama | Local LLM only | https://ollama.com |

---

## API Keys

API keys are required for cloud-based engine configurations. Create a `.env` file at `src/app/.env`:

```
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

| Key | Used by | Where to get it |
|-----|---------|----------------|
| `OPENAI_API_KEY` | WhisperAPIEngine, OpenAILLMEngine, OpenAITTSEngine | https://platform.openai.com |
| `GROQ_API_KEY` | GroqLLMEngine | https://console.groq.com — free tier available |
| `OPENROUTER_API_KEY` | OpenRouterLLMEngine | https://openrouter.ai — free tier, 50 req/day limit |

Only add the keys needed for the engine configuration you intend to use. The Groq hybrid configuration only requires `GROQ_API_KEY`.

---

## Setup

Full setup instructions are documented in `docs/SETUP.md` and the Installation Guide. The quick version:

```bash
# Clone the repository
git clone https://github.com/justtcallmejayy/W26-Applied-Research-Voice-Agent.git
cd W26-Applied-Research-Voice-Agent

# Create and activate virtual environment (use Python 3.10-3.13)
python3.11 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Add API keys
# Create src/app/.env and add your keys

# Verify installation
python -m pytest tests/unit/test_api.py -v
```

All 21 unit tests should pass in under 1 second with no API keys required.

---

## Engine Configuration

The system supports four engine configurations. Switching providers requires only editing the `ENGINES` dict in `src/app/config.py` — no pipeline code changes are needed.

| Configuration | STT | LLM | TTS | Recommended for |
|--------------|-----|-----|-----|----------------|
| Cloud (OpenAI) | WhisperAPIEngine | OpenAILLMEngine (GPT-4) | OpenAITTSEngine | Best instruction-following quality |
| Hybrid (Groq) | WhisperLocalEngine | GroqLLMEngine (llama-3.1-8b) | GTTSEngine | Deployment — free, fast, fully compliant |
| Local (Ollama) | WhisperLocalEngine | OllamaLLMEngine (gemma3:1b) | GTTSEngine | Offline testing, no API keys required |
| OpenRouter | WhisperLocalEngine | OpenRouterLLMEngine | GTTSEngine | Flexible model testing — 50 req/day free limit |

**Recommendation:** Use the Groq hybrid configuration for deployment. It was validated across 10 sessions through the REST API with 100% field order compliance, 100% confirmation summary production, and sub-second latency on early turns — at no cost.

To activate the Groq hybrid config in `src/app/config.py`:

```python
ENGINES = {
    "stt": "core.engines.stt.whisper_local.WhisperLocalEngine",
    "llm": "core.engines.llm.groq_llm.GroqLLMEngine",
    "tts": "core.engines.tts.gtts_tts.GTTSEngine",
}
```

---

## Running the System

### CLI Voice Agent
```bash
python3 src/app/main.py
```
Records from microphone, runs full onboarding session in terminal.

### Streamlit Dashboard
```bash
streamlit run src/app/dashboard/dashboard.py
```
Opens at http://localhost:8501 — browser-based interface with debug panel and live logs.

### REST API
```bash
cd src && python3 api/main.py
```
Starts at http://localhost:8000. Interactive API documentation available at http://localhost:8000/docs.

---

## REST API

The REST API exposes the onboarding pipeline over HTTP so any frontend can integrate without touching backend code. Full documentation is in `docs/API.md`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Engine config, field list, active session count |
| POST | `/session/start` | Start session, receive opening audio and session ID |
| POST | `/session/{id}/turn` | Upload audio WAV, receive response audio |
| POST | `/session/{id}/confirm` | Submit confirmation audio, close session |
| DELETE | `/session/{id}` | End session early |

**Typical session flow:**
1. `POST /session/start` — save the `X-Session-ID` from response headers
2. `POST /session/{id}/turn` × 6 — upload WAV audio for each field, receive agent response audio
3. `POST /session/{id}/confirm` — submit user's verbal confirmation, session closes

Response headers carry metadata alongside audio: `X-Transcript`, `X-Response-Text`, `X-Field`, `X-Next-Field`, `X-Session-Complete`.

**Note:** The session store is in-memory. Sessions are lost if the server restarts. A production deployment would replace this with Redis or a database.

---

## Running Tests

### Unit Tests (no API keys or audio fixtures required)

```bash
python -m pytest tests/unit/test_api.py -v
```

Expected result: 21/21 passing in under 1 second. These tests use mocked engines and synthetic audio — safe to run in any environment.

### Integration Tests (requires API keys and audio fixtures)

Integration tests run full 6-turn onboarding sessions using pre-recorded audio. You will need to provide your own WAV audio fixtures recorded at 16kHz mono and placed in `tests/audio/`:

| File | Question to answer |
|------|--------------------|
| `name.wav` | What is your full name? |
| `employment.wav` | Are you currently employed, unemployed, or a student? |
| `skills.wav` | What technical or professional skills do you have? |
| `education.wav` | What is your highest level of education? |
| `experience.wav` | Can you describe your work experience? |
| `job_prefs.wav` | What type of role or industry are you interested in? |

Once fixtures are in place:

```bash
python -m pytest tests/integration/ -v -s
```

Ensure your `.env` file contains valid API keys for the engine configuration set in `config.py`.

### All Tests

```bash
python -m pytest tests/unit/ -v
```

---

## Deployment

Deployment to Railway was initiated but could not be completed before submission due to the end of semester timeline. The intended deployment architecture is:

- **Platform:** Railway (https://railway.app)
- **Engine config:** Groq hybrid (WhisperAPIEngine + GroqLLMEngine + GTTSEngine)
- **Start command:** `cd src && uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Dependencies:** `requirements-api.txt` (excludes openai-whisper to stay under Railway's 4 GB image limit)
- **Environment variables:** `GROQ_API_KEY` set in Railway service variables

The `railway.json` and `nixpacks.toml` configuration files are already in the repository root. To complete deployment, install the Railway CLI and run `railway up` from the project root, or connect the repository directly through the Railway dashboard.

---

## Known Limitations

| Limitation | Detail |
|------------|--------|
| In-memory session store | Sessions lost on server restart — Redis or database needed for production |
| Local model (gemma3:1b) unreliable | 1B parameter scale insufficient for consistent instruction-following — Groq or OpenAI recommended |
| Loud non-speech hallucinations | RMS energy check handles silence but loud ambient audio above 0.01 threshold can still trigger Whisper |
| gTTS requires internet | Google TTS makes outbound requests even in the local engine set |
| Railway deployment in progress | Not completed before submission — configuration is in place, image size constraint needs resolution |
| Small tester pool | All testing conducted by team members — real-user testing recommended before production use |

---

## Recommended Next Steps

1. **Complete Railway deployment** — use the existing `railway.json` and `nixpacks.toml` with `requirements-api.txt` to resolve the image size issue and get a public API URL
2. **Build a frontend** — the REST API provides everything needed; record audio via the Web Audio API, POST to `/session/{id}/turn`, play back the returned MP3
3. **Replace in-memory session store** — integrate Redis or PostgreSQL for production session persistence
4. **Real-user testing** — run sessions with actual job seekers to surface transcription errors and field ambiguities not seen in internal testing
5. **Voice Activity Detection** — replace the RMS threshold with Silero VAD or WebRTC VAD to handle loud non-speech audio
6. **Upgrade local model** — gemma3:4b or gemma3:8b would significantly improve instruction-following without cloud API costs

---

## Contact

For questions about the codebase, architecture decisions, or setup issues, contact the development team through the GitHub repository or via the course.

| Team Member | Role |
|-------------|------|
| Brendan Dileo | Lead Developer |
| Dhairya Pareshbhai Patel | QA / Code Review |
| Jay Nitinkumar Choksi | QA / Code Review |
| Rishyu Babariya | Research and Maintenance |