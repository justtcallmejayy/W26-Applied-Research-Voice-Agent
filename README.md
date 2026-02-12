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
streamlit run dashboard/dashboard.py
```

> Set `USE_LOCAL = True` in `main.py` to use local models, or `False` for the OpenAI cloud-based agent.

---

## Project Structure

```bash
W26-Applied-Research-Voice-Agent/
├── README.md
├── requirements.txt        # pip dependencies
├── pyproject.toml          # project config and Python version
├── docs/                   # documentation files
├── src/
│   └── app/
│       ├── main.py         # entry point
│       ├── agent/          # cloud and local agent logic
│       │   ├── voice_agent.py
│       │   ├── local_voice_agent.py
│       │   └── onboarding_config.py
│       ├── dashboard/      # Streamlit dashboard
│       └── logs/           # runtime logs
└── tests/
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
| Python | 3.8+ |

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

## Configuration

Onboarding behaviour is controlled entirely in `src/app/agent/onboarding_config.py`:

```python
# Fields the LLM will collect in order
ONBOARDING_FIELDS = [
    "name",
    "employment_status",
    "desired_job_title",
]

# Controls LLM behaviour during the session
SYSTEM_PROMPT = """..."""
```

To add a new onboarding field, add a string to `ONBOARDING_FIELDS`. No other changes are needed.

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `python3 src/app/main.py` | Run the voice agent |
| `streamlit run dashboard/dashboard.py` | Run the dashboard |
| `python3 -m venv venv` | Create virtual environment |
| `source venv/bin/activate` | Activate virtual environment |
| `pip install -r requirements.txt` | Install dependencies |
| `deactivate` | Deactivate virtual environment |
| `rm -rf venv` | Remove virtual environment |

---