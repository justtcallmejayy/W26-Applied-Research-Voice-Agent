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

## Current Pipeline

1. Record Audio 
    - Capture users voice from microphone on their computer (5 seconds)
    - Store as a numpy array in memory
2. Save to a temporary file 
    - Convert audio data to a .WAV file 
    - Save to a temporary location local on disk
3. Transcribe the audio
    - Send the .WAV file to OpenAI Whisper API 
    - Receibe text transcription back from OpenAI
4. Generate Response 
    - Send transcribed text back to OpenAI GPT model 
    - AI processes and generates a reply 
5. Text to Speech 
    - Send model response to OpenAI TTS API 
    - Receive .MP3 audio file back as response 
    - Save to temporary location locally 
6. Play Audio
    - Load .MP3 audio file into pygame mixer 
    - Play audio through users computer speakers 
    - Wait until playback completes 
7. Cleanup 
    - Delete temporary .WAV file storing the recorded audio
    - Delete the temporary .MP3 audio file containing the TTS response

---

## Project Structure
```bash
W26-Applied-Research-Voice-Agent/

```

---