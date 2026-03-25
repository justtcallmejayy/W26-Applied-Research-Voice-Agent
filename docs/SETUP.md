
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

**Cloud (OpenAI — default):**
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

### OpenAI API Key (Cloud Engines Only)
Create a `.env` file in `src/app/`:
```
OPENAI_API_KEY=your_key_here
```
This key is used by `WhisperAPIEngine`, `OpenAILLMEngine`, and `OpenAITTSEngine`.

---

## Running the Project

### CLI
```bash
python3 src/app/main.py
```

### Dashboard
```bash
streamlit run src/app/dashboard/dashboard.py
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

**gTTS errors**
gTTS requires an active internet connection even when running the local engine set.
