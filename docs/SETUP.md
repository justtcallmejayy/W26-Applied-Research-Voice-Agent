
# Setup

This guide covers how to set up and run the voice agent prototype locally. Both the cloud agent and local agent are supported. Follow the steps below based on your preferred configuration.

> This document is a work in progress and will be updated as the project evolves.

---

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.10–3.13
- FFmpeg
- Ollama (required for local agent only)

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

### Installing Ollama (Local Agent Only)
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

### OpenAI API Key (Cloud Agent Only)
Create a `.env` file in `src/app/`:
```
OPENAI_API_KEY=your_key_here
```

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
Make sure Ollama is running before starting the local agent:
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