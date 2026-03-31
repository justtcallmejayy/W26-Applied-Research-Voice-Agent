# Setup

This guide covers how to set up and run the voice agent prototype locally. Both cloud and local engine sets are supported. Provider selection is controlled by editing the `ENGINES` dict in `src/app/config.py`.

---

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.10–3.13
- FFmpeg (required for local Whisper transcription)
- Ollama (required for local LLM only)

### Installing FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH.

**Linux:**
```bash
sudo apt install ffmpeg
```

### Installing Ollama (Local LLM Only)
Download and install from https://ollama.com, then pull the required model:
```bash
ollama pull gemma3:1b
ollama serve
```

---

## Installation
```bash
git clone https://github.com/justtcallmejayy/W26-Applied-Research-Voice-Agent/
cd W26-Applied-Research-Voice-Agent

python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

---

## Configuration

### Provider Selection
Open `src/app/config.py` and set the `ENGINES` dict to the desired provider set.

**Cloud (OpenAI):**
```python
ENGINES = {
    "stt": "core.engines.stt.whisper_api.WhisperAPIEngine",
    "llm": "core.engines.llm.openai_llm.OpenAILLMEngine",
    "tts": "core.engines.tts.openai_tts.OpenAITTSEngine",
}
```

**Local (Ollama + on-device Whisper + gTTS):**
```python
ENGINES = {
    "stt": "core.engines.stt.whisper_local.WhisperLocalEngine",
    "llm": "core.engines.llm.ollama_llm.OllamaLLMEngine",
    "tts": "core.engines.tts.gtts_tts.GTTSEngine",
}
```

**OpenRouter:**
```python
ENGINES = {
    "stt": "core.engines.stt.whisper_local.WhisperLocalEngine",
    "llm": "core.engines.llm.openrouter_llm.OpenRouterLLMEngine",
    "tts": "core.engines.tts.gtts_tts.GTTSEngine",
}
```

### API Keys
Create a `.env` file in `src/app/`:
```
OPENAI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

`OPENAI_API_KEY` is used by `WhisperAPIEngine`, `OpenAILLMEngine`, and `OpenAITTSEngine`.
`OPENROUTER_API_KEY` is used by `OpenRouterLLMEngine`.

---

## Running the Project

### CLI Voice Agent
```bash
python3 src/app/main.py
```

### Streamlit Dashboard
```bash
streamlit run src/app/dashboard/dashboard.py
```

### REST API
```bash
cd src
python3 api/main.py
```

The API runs on `http://localhost:8000` by default. Interactive docs are available at `http://localhost:8000/docs`.

---

## Running Tests

```bash
# Unit tests only — no API keys or audio fixtures required
pytest tests/unit/ -v

# Integration tests — requires API keys in src/app/.env and audio fixtures in tests/audio/
pytest tests/integration/ -v -s

# All tests
pytest tests/ -v
```

### Recording Audio Fixtures for Integration Tests
Integration tests require pre-recorded WAV files in `tests/audio/` (gitignored). Record them using the helper script:
```bash
python tests/audio/record_fixtures.py
```

---

## Common Issues

**Microphone not detected**
Ensure your system grants microphone permissions to the terminal or IDE you are running from.

**Ollama not responding**
Make sure Ollama is running before starting the local engine set:
```bash
ollama serve
```

**FFmpeg not found**
Ensure FFmpeg is installed and available on your PATH. Verify with:
```bash
ffmpeg -version
```

**OpenAI API errors**
Ensure your `.env` file exists at `src/app/.env` and contains a valid `OPENAI_API_KEY`.

**OpenRouter rate limit (429)**
The free tier allows 50 requests per day across all free models. If the limit is hit, the cap resets at midnight UTC. For automated testing, mock the LLM engine instead of making real API calls.

**API import errors on startup**
If running the API with `python3 api/main.py` from inside `src/`, the `sys.path` inserts at the top of `api/main.py` handle path resolution automatically. If running from the project root, use:
```bash
PYTHONPATH=src:src/app python -m uvicorn api.main:app --reload --port 8000
```

**gTTS errors**
gTTS requires an active internet connection even when running the local engine set.

**FP16 warning from Whisper**
`UserWarning: FP16 is not supported on CPU; using FP32 instead` is harmless — Whisper falls back to FP32 on CPU automatically.
