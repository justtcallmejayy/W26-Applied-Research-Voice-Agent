# W26-Applied-Research-Voice-Agent
Voice Agent for Candidate Onboarding &amp; Career Guidance (Applied Research 1, Winter 2026)

---

## Commands

- Run the VoiceAgent: python3 src/app/main.py
- Run the dashboard: streamlit run dashboard/dashboard.py

- Create Virtual Environment: python3 -m venv venv
- Activate Virtual Environment: source venv/bin/activate
- Install Dependencies: pip install -r requirements.txt
- Deactivate Virtual Environment: deactivate
- Remove venv: rm -rf venv

---

## Tech & API Usage
- Audio Recording: `sounddevice`
- Audio I/O: `soundfile`
- Audio Playback: `pygame.mixer`
- API Client: `openai`
    - OpenAI Whisper API (Audio transcription, speech-to-text) [whisper-1]
    - OpenAI Chat Completions API (Text generation) [gpt-4]
    - OpenAI Text-to-Speech API (Speech synthesis)
- Dashboard: `streamlit`

---

## Project Structure
```bash
W26-Applied-Research-Voice-Agent/

```

---