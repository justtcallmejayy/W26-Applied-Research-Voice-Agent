# System Architecture

This document describes the current architecture of the voice agent onboarding prototype built for Enabled Talent as part of COMP-10199 Applied Research 1, Winter 2026. It reflects the actual state of the codebase as of March 2026.

---

## Overview

The system is a voice-based conversational onboarding agent that collects six candidate profile fields through spoken interaction. It has two execution paths — a cloud agent backed by OpenAI APIs and a local agent that runs on-device — controlled by a single flag in the entry point. A Streamlit dashboard provides an alternative browser-based interface to the same agents.

---

## Dual Agent Design

| Property | Cloud Agent (`VoiceAgent`) | Local Agent (`LocalVoiceAgent`) |
|---|---|---|
| Module | `agent/voice_agent.py` | `agent/local_voice_agent.py` |
| STT | OpenAI Whisper-1 API | Whisper base (local, `openai-whisper` package) |
| LLM | GPT-4 via OpenAI API | Ollama (`gemma3:1b` default, configurable) |
| TTS | OpenAI TTS-1 (`voice="alloy"`) | gTTS (requires internet despite "local" label) |
| Playback | pygame | pygame |
| Credentials | `OPENAI_API_KEY` in `.env` | Ollama running at `http://localhost:11434` |
| Instruction-following | High (100% completion, 100% confirmation) | Low (27% completion, 0% confirmation) |

Both agents implement the same public interface (`record_audio`, `save_audio`, `transcribe_audio`, `generate_response`, `text_to_speech`, `play_audio`, `cleanup_file`), allowing `main.py` and `dashboard.py` to call either one without branching after initialization.

---

## Agent Selection

`main.py` contains a hardcoded `USE_LOCAL` flag (currently `True`). Setting it to `False` loads `VoiceAgent` with an OpenAI client instead. The dashboard exposes this as a radio button in the sidebar.

```python
# main.py
USE_LOCAL = True   # change to False for cloud agent
```

---

## End-to-End Pipeline (per turn)

The pipeline runs identically through both agents. Each turn maps to one onboarding field.

```
1. record_audio()
      sounddevice captures fixed-duration mono audio (5s default, 16 kHz)
      returns numpy float32 array

2. save_audio()
      soundfile writes array to a temporary .wav file
      returns file path

3. Energy detection  [main.py only — not present in dashboard.py]
      soundfile reads the .wav back
      np.abs(audio_data).mean() computes RMS amplitude
      if energy < 0.01: skip turn (no API call, no transcription)

4. transcribe_audio()
      Cloud: POST audio to OpenAI Whisper-1 API → returns text string
      Local: whisper.transcribe() on local model → returns result["text"].strip()
      if result is empty: skip turn

5. generate_response()
      user_input appended to conversation_history as {"role": "user", "content": ...}
      messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history
      Cloud: client.chat.completions.create(model="gpt-4", max_tokens=150,
             temperature=0.7, presence_penalty=0.5, frequency_penalty=0.2)
      Local: HTTP POST to http://localhost:11434/api/chat
             (stream=False, keep_alive="30m", one retry on timeout)
      response appended to conversation_history as {"role": "assistant", "content": ...}
      history trimmed to last 8 messages if exceeded

6. text_to_speech()
      Cloud: client.audio.speech.create(model="tts-1", voice="alloy") → .mp3
      Local: gTTS(text, lang="en", slow=False) → .mp3

7. play_audio()
      pygame.mixer loads and plays the .mp3
      blocks until playback is complete

8. cleanup_file()
      os.remove() deletes the temporary .wav and .mp3 files

9. Logging
      Every stage is timed (time.time()) and written to logs/<log_type>/<timestamp>.log
      and to stdout via the configured logger
```

The pipeline does **not** pass the current field name into `generate_response()`. The model is expected to infer its position in the conversation from history alone. This works reliably at GPT-4 scale and fails frequently at 1B parameter scale.

---

## Onboarding Fields and System Prompt

Both agents read their configuration from `agent/onboarding_config.py`:

```python
ONBOARDING_FIELDS = [
    "name",
    "employment_status",
    "skills",
    "education",
    "experience",
    "job_preferences"
]
```

`main.py` loops `len(ONBOARDING_FIELDS)` turns (6). `SYSTEM_PROMPT` in the same file instructs the model to ask one field per turn in the specified order, acknowledge each answer briefly, and after all six fields are collected, read back each field and answer and ask "Does everything look correct?".

The confirmation workflow is entirely prompt-driven. There is no pipeline-level enforcement — the turn loop ends after 6 turns regardless of whether the model triggered a confirmation.

---

## Conversation History

Both agents maintain `self.conversation_history`, a list of OpenAI-style message dicts (`role`/`content`). The system prompt is prepended fresh on every `generate_response()` call and is not stored in history. Only user and assistant messages accumulate. History is trimmed to the last 8 messages when exceeded.

For the local agent, this trim triggers at turn 4–5. The 1B model loses its position in the field sequence when early turns are dropped, causing question order errors.

---

## Config-Driven Architecture (in progress)

`config.py` was created to centralize all tuneable constants:

| Constant | Value |
|---|---|
| `USE_LOCAL` | `True` |
| `RECORDING_DURATION` | `5` (seconds) |
| `AUDIO_SAMPLE_RATE` | `16000` (Hz) |
| `ENERGY_THRESHOLD` | `0.01` |
| `LOCAL_WHISPER_MODEL` | `"base"` |
| `OLLAMA_MODEL` | `"gemma3:1b"` |
| `MAX_HISTORY_LENGTH` | `8` |
| `ONBOARDING_FIELDS` | 6-field list (identical to `onboarding_config.py`) |
| `SYSTEM_PROMPT` | full prompt string (identical to `onboarding_config.py`) |

**Current state:** `config.py` is not imported by any module. `main.py`, both agent files, and `dashboard.py` all still import from `agent/onboarding_config.py`. Audio and model constants are hardcoded in each class constructor. Integration of `config.py` is pending.

---

## Plug-and-Play Abstraction Layer (in progress)

`core/engines/base.py` defines three abstract base classes using Python's `abc` module:

```python
class STTEngine(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str: ...

class LLMEngine(ABC):
    @abstractmethod
    def generate(self, messages: list[dict]) -> str: ...

class TTSEngine(ABC):
    @abstractmethod
    def synthesize(self, text: str) -> str: ...
```

**Current state:** These are interface definitions only. No concrete implementations exist (no `WhisperEngine`, `OllamaEngine`, `OpenAISTTEngine`, etc.). Neither `VoiceAgent` nor `LocalVoiceAgent` inherits from or references these classes. The plug-and-play layer is structurally defined but not connected to anything.

---

## Dashboard

`dashboard.py` is a Streamlit application providing a browser-based interface to the same agents. It imports from `agent/onboarding_config.py`, not `config.py`.

**Layout:**

- **Sidebar** — agent selection radio (Local/Cloud), audio settings (duration slider 3–15s, sample rate selectbox), local model settings (Whisper model size, Ollama model tag), onboarding field list, session start/stop buttons
- **Main panel** — progress bar, conversation history rendered as chat messages, Record button, status label, Retry button on error
- **Debug panel** — session parameters expander, turn tracker per field (DONE/ACTIVE/PENDING), system prompt viewer, raw conversation history (JSON), runtime log

**Session flow:**
1. "Start session" pressed → agent instantiated, opening message generated and played, `session_active = True`
2. "Record" pressed → full pipeline runs synchronously (record → energy not checked → transcribe → generate → tts → play)
3. `st.session_state.turn` increments, `st.rerun()` called
4. After 6 turns, completion message shown

**Differences from `main.py`:**

- The dashboard does **not** perform RMS energy detection — it only raises an error if the transcription string is empty
- Status labels (`recording`, `transcribing`, `generating`, `speaking`) are written to `st.session_state.status` but Streamlit only rerenders on user action, so they do not update mid-turn
- `DashboardLogHandler` attaches to the root logger and appends formatted log lines to `st.session_state.log_lines`, buffered to 100 lines; the debug "Runtime log" panel displays this buffer

---

## Logging

`utils/logger.py` exports `setup_logger(name, log_type, level)`:

- Creates `src/app/logs/<log_type>/<timestamp>.log` on first call, making parent directories as needed
- Attaches a `FileHandler` and a `StreamHandler` (stdout) with the format `[LEVEL] filename:lineno - funcName() - message`
- Guard against duplicate handlers: returns the existing logger if handlers are already attached
- `VoiceAgent` uses `log_type="cloud-agent"`, `LocalVoiceAgent` uses `log_type="local-agent"`
- `logs/` is gitignored — logs are local only and never committed

---

## Repository Structure

```
W26-Applied-Research-Voice-Agent/
├── README.md
├── requirements.txt
├── pyproject.toml                       
├── docs/
│   ├── ARCHITECTURE.md                   
│   ├── DECISIONS.md    
│   ├── SETUP.md             
│   └── test-results/
└── src/
    └── app/
        ├── main.py                     
        ├── config.py                    
        ├── agent/
        │   ├── voice_agent.py            
        │   ├── local_voice_agent.py      
        │   └── onboarding_config.py     
        ├── core/
        │   └── engines/
        │       └── base.py              
        ├── dashboard/
        │   └── dashboard.py              
        ├── utils/
        │   └── logger.py                
        └── logs/                        
```

---

## Known Limitations

| Limitation | Detail |
|---|---|
| `config.py` not integrated | All modules import from `onboarding_config.py`; constants hardcoded in constructors |
| Plug-and-play not implemented | `core/engines/base.py` defines interfaces; no concrete implementations exist; agents do not extend them |
| No pipeline field enforcement | Current field not passed to `generate_response()`; model infers position from history alone |
| No confirmation turn in loop | Readback and confirmation are prompt-only; turn loop ends after 6 turns regardless |
| History trim causes local order errors | 8-message cap reached at turn 4–5; 1B model loses field position context |
| gTTS requires internet | `LocalVoiceAgent` TTS is not fully offline |
| Energy detection missing in dashboard | `dashboard.py` skips RMS check; only catches empty transcriptions |
| Loud non-speech above threshold | RMS fix works for silence; loud ambient noise above 0.01 still triggers Whisper hallucinations |
| Single-threaded audio | `sd.wait()` and pygame playback block the entire process; dashboard freezes during recording/playback |
| `VoiceAgent.start_onboarding()` unused | Method defined in `voice_agent.py` but `main.py` calls `generate_response()` directly |
| gemma3 instruction-following | 27% completion rate, 0% confirmation compliance, 55% question order errors |
| Name transcription errors | Whisper struggles with proper nouns (~20% local, ~10% cloud) |

