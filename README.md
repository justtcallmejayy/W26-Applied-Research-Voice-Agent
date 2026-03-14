# W26-Applied-Research-Voice-Agent
Voice Agent for Candidate Onboarding &amp; Career Guidance 
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

> Set `USE_LOCAL = True` in `main.py` to use local models, or `False` for the OpenAI cloud-based agent.

---

## Project Structure

```bash
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
│       ├── config.py                  # central configuration (integration pending)
│       ├── agent/
│       │   ├── voice_agent.py         # cloud agent
│       │   ├── local_voice_agent.py   # local agent
│       │   └── onboarding_config.py   # fields and system prompt
│       ├── core/
│       │   └── engines/
│       │       └── base.py            # abstract engine interfaces
│       ├── dashboard/
│       │   └── dashboard.py           # Streamlit dashboard
│       └── utils/
│           └── logger.py
└── tests/
    ├── conftest.py
    └── test_voice_agent.py
```

---

## Onboarding Pipeline

Each conversational turn follows this pipeline:

| Step | Description |
|------|-------------|
| 1. Record | Capture 5 seconds of audio from the user's microphone |
| 2. Save | Write audio to a temporary `.wav` file on disk |
| 3. Transcribe | Convert `.wav` to text via Whisper |
| 4. Generate | Send transcription to LLM, receive conversational response |
| 5. Synthesise | Convert response text to a `.mp3` via TTS |
| 6. Play | Play `.mp3` through the user's speakers via pygame |
| 7. Cleanup | Delete both temporary audio files |

The number of turns is driven by `ONBOARDING_FIELDS` in `onboarding_config.py`. The LLM is guided by `SYSTEM_PROMPT` to collect fields in order through natural conversation.

---

## Tech Stack

### Local (USE_LOCAL = True)
| Concern | Tool |
|---------|------|
| LLM inference | Ollama (`gemma3:1b`) |
| Speech-to-text | `openai-whisper` (runs on-device) |
| Text-to-speech | `gTTS` |
| Audio recording | `sounddevice` + `soundfile` |
| Audio playback | `pygame.mixer` |
| Audio processing | `FFmpeg` (via Homebrew) |
| Python | 3.10+ |


### Cloud (USE_LOCAL = False)
| Concern | Tool |
|---------|------|
| LLM inference | OpenAI Chat Completions (`gpt-4`) |
| Speech-to-text | OpenAI Whisper API (`whisper-1`) |
| Text-to-speech | OpenAI TTS API |
| Audio recording | `sounddevice` + `soundfile` |
| Audio playback | `pygame.mixer` |
| Dashboard | `streamlit` |

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
| `rm -rf venv` | Remove virtual environment |
| `pytest tests/ -v` | Run the test suite |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design, pipeline, and component overview |
| [Decisions](docs/DECISIONS.md) | Key technical decisions and reasoning |
| [Setup](docs/SETUP.md) | Detailed setup, configuration, and troubleshooting |
| [Test Results](docs/test-results/README.md) | All test reports and current performance metrics |