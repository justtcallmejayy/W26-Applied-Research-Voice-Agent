# System Architecture

This document describes the current architecture of the voice agent onboarding prototype built for Enabled Talent as part of COMP-10199 Applied Research 1, Winter 2026. It reflects the actual state of the codebase as of March 2026.

---

## Overview

The system is a voice-based conversational onboarding agent that collects six candidate profile fields through spoken interaction. A single provider-agnostic `OnboardingPipeline` handles the full conversation loop. STT, LLM, and TTS are injected as engine instances at startup — the pipeline does not know or care which provider is active. Provider selection is controlled entirely by the `ENGINES` dict in `config.py`. A Streamlit dashboard provides an alternative browser-based interface to the same pipeline. A FastAPI REST API (`src/api/main.py`) exposes the pipeline over HTTP, enabling frontend integration and remote deployment.

---

## Plug-and-Play Engine Layer

`core/engines/base.py` defines three abstract base classes:

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

Seven concrete engine implementations exist:

| Engine class | Module | Provider |
|---|---|---|
| `WhisperAPIEngine` | `core/engines/stt/whisper_api.py` | OpenAI Whisper-1 API |
| `WhisperLocalEngine` | `core/engines/stt/whisper_local.py` | `openai-whisper` on-device |
| `OpenAILLMEngine` | `core/engines/llm/openai_llm.py` | OpenAI GPT-4 |
| `OllamaLLMEngine` | `core/engines/llm/ollama_llm.py` | Ollama (`gemma3:1b` default) |
| `OpenRouterLLMEngine` | `core/engines/llm/openrouter_llm.py` | OpenRouter (free model set) |
| `OpenAITTSEngine` | `core/engines/tts/openai_tts.py` | OpenAI TTS-1 |
| `GTTSEngine` | `core/engines/tts/gtts_tts.py` | gTTS |

All seven inherit from their respective base class. The pipeline only calls the interface methods (`transcribe`, `generate`, `synthesize`) and never imports engine classes directly.

---

## Provider Selection

Provider selection is controlled by the `ENGINES` dict in `config.py`:

```python
# Cloud (OpenAI)
ENGINES = {
    "stt": "core.engines.stt.whisper_api.WhisperAPIEngine",
    "llm": "core.engines.llm.openai_llm.OpenAILLMEngine",
    "tts": "core.engines.tts.openai_tts.OpenAITTSEngine",
}

# Local
# ENGINES = {
#     "stt": "core.engines.stt.whisper_local.WhisperLocalEngine",
#     "llm": "core.engines.llm.ollama_llm.OllamaLLMEngine",
#     "tts": "core.engines.tts.gtts_tts.GTTSEngine",
# }

# OpenRouter
# ENGINES = {
#     "stt": "core.engines.stt.whisper_local.WhisperLocalEngine",
#     "llm": "core.engines.llm.openrouter_llm.OpenRouterLLMEngine",
#     "tts": "core.engines.tts.gtts_tts.GTTSEngine",
# }
```

`load_engine(dotted_path)` in `core/pipeline.py` resolves these strings at runtime using `importlib.import_module`. No code changes are needed outside `config.py` to swap providers.

---

## End-to-End Pipeline (per turn)

`OnboardingPipeline` in `core/pipeline.py` drives the full conversation loop. Audio I/O lives here; STT, LLM, and TTS are delegated to the injected engines.

```
1. record_audio()
      sounddevice captures fixed-duration mono audio (default 5s, 16 kHz)
      returns numpy float32 array

2. save_audio()
      soundfile writes array to a temporary .wav file
      returns file path

3. Energy detection
      soundfile reads the .wav back
      np.abs(audio_data).mean() computes RMS amplitude
      if energy < ENERGY_THRESHOLD (0.01): skip turn, log warning, continue

4. stt.transcribe(audio_path)
      WhisperAPIEngine: POST audio to OpenAI Whisper-1 → returns text string
      WhisperLocalEngine: whisper.transcribe() on local model → result["text"].strip()
      if result is empty string: skip turn, log warning, continue

5. _generate(user_text, current_field)
      current field injected as context prefix: "[Collecting: <field>]\n<user_text>"
      user_text appended to conversation_history as {"role": "user", "content": ...}
      messages = [{"role": "system", "content": system_prompt}] + conversation_history
      llm.generate(messages) called
      OpenAILLMEngine: chat.completions.create(model="gpt-4", max_tokens=150,
                       temperature=0.7, presence_penalty=0.5, frequency_penalty=0.2)
      OllamaLLMEngine: HTTP POST to localhost:11434/api/chat (stream=False, timeout=30s)
      OpenRouterLLMEngine: OpenAI-compatible POST to openrouter.ai/api/v1
      if response is empty or None: remove user message from history, skip turn
      response appended to history as {"role": "assistant", "content": ...}
      history trimmed to last MAX_HISTORY_LENGTH (12) messages if exceeded

6. tts.synthesize(text)
      OpenAITTSEngine: audio.speech.create(model=TTS_MODEL, voice=TTS_VOICE) → .mp3
      GTTSEngine: gTTS(text, lang="en", slow=False) → .mp3
      returns path to temporary audio file

7. play_audio(filepath)
      pygame.mixer loads and plays the audio file
      blocks until playback is complete

8. cleanup_file(filepath)
      os.remove() deletes the temporary audio files

9. Logging
      every stage is timed and written to logs/pipeline/<timestamp>.log
      and to stdout via the configured logger
```

The current field name is passed into `_generate()` on every turn as a context prefix, providing explicit per-turn field enforcement rather than relying on the model to infer position from history alone.

---

## Onboarding Fields and System Prompt

Fields and the system prompt are defined in `config.py`:

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

`OnboardingPipeline.run()` loops `len(ONBOARDING_FIELDS)` turns (6), passing the current field to `_generate()` on each turn. `SYSTEM_PROMPT` instructs the model to collect one field per turn in the specified order, acknowledge each answer briefly, and after all six fields are collected, read back each field and answer and end with "Does everything look correct?".

The confirmation workflow is prompt-driven. There is no pipeline-level confirmation turn — the turn loop ends after 6 turns regardless of whether the model triggered a confirmation.

---

## Conversation History

`OnboardingPipeline` maintains `self.conversation_history`, a list of OpenAI-style message dicts (`role`/`content`). The system prompt is prepended fresh on every `_generate()` call and is not stored in history. Only user and assistant messages accumulate. History is trimmed to the last `MAX_HISTORY_LENGTH` (12) messages when exceeded.

The increase from 8 to 12 gives the local model more context before trimming occurs, reducing the frequency of field order errors caused by early turns being dropped.

---

## REST API

`src/api/main.py` is a FastAPI application that exposes `OnboardingPipeline` over HTTP. It uses the same `load_engine()` and `ENGINES` dict as the CLI and dashboard — provider switching requires no API code changes.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/session/start` | Create session, return opening audio + session ID |
| `POST` | `/session/{id}/turn` | Submit audio, run STT → LLM → TTS, return response audio |
| `POST` | `/session/{id}/confirm` | Submit confirmation audio, close session |
| `DELETE` | `/session/{id}` | End and clean up session |
| `GET` | `/health` | Engine config, field list, active session count |

**Session flow:**
1. `POST /session/start` → pipeline instantiated, opening message generated and synthesized, session ID returned in `X-Session-ID` header
2. `POST /session/{id}/turn` (×6) → uploaded WAV transcribed → LLM generates response with current field injected → TTS synthesized → audio returned
3. `POST /session/{id}/confirm` → confirmation transcribed, closing message returned, session deleted from store

**Response headers** carry metadata alongside the audio file: `X-Transcript`, `X-Response-Text`, `X-Turn`, `X-Field`, `X-Next-Field`, `X-Session-Complete`.

**Session store:** In-memory dict (`sessions: dict[str, dict]`). Sessions are lost on server restart. Production deployment would use Redis or a database.

**Header encoding:** LLM and STT output passed into response headers is sanitised through `safe_header()`, which strips newlines and encodes to latin-1, preventing `UnicodeEncodeError` and `LocalProtocolError` from typographic characters in model output.

**Running the API:**
```bash
cd src
python3 api/main.py
```

Interactive docs available at `http://localhost:8000/docs`.

---

## Configuration

All tuneable constants are defined in `config.py`:

| Constant | Value | Used by |
|---|---|---|
| `RECORDING_DURATION` | `5` (seconds) | `OnboardingPipeline` |
| `AUDIO_SAMPLE_RATE` | `16000` (Hz) | `OnboardingPipeline` |
| `ENERGY_THRESHOLD` | `0.01` | `OnboardingPipeline` |
| `MAX_HISTORY_LENGTH` | `12` | `OnboardingPipeline` |
| `TTS_VOICE` | `"alloy"` | `OpenAITTSEngine` |
| `TTS_MODEL` | `"tts-1"` | `OpenAITTSEngine` |
| `ONBOARDING_FIELDS` | 6-field list | `OnboardingPipeline`, `dashboard.py`, `api/main.py` |
| `SYSTEM_PROMPT` | full prompt string | `OnboardingPipeline` |
| `ENGINES` | dotted path dict | `main.py`, `dashboard.py`, `api/main.py` via `load_engine()` |

---

## Dashboard

`dashboard.py` is a Streamlit application providing a browser-based interface to the same `OnboardingPipeline`. It imports from `config.py` and uses `load_engine()` to instantiate engines.

**Layout:**

- **Sidebar** — audio settings (recording duration slider 3–15s, sample rate selectbox), active engine display (read from `ENGINES`), onboarding field list, session start/stop buttons
- **Main panel** — progress bar, conversation history rendered as chat messages, Record button, status label, Retry button on error
- **Debug panel** — session parameters expander, turn tracker per field (DONE/ACTIVE/PENDING), system prompt viewer, raw conversation history (JSON), runtime log

**Session flow:**
1. "Start session" pressed → engines loaded, pipeline instantiated, opening message generated and played, `session_active = True`
2. "Record" pressed → full pipeline runs synchronously (record → energy check → transcribe → generate → tts → play)
3. `st.session_state.turn` increments, `st.rerun()` called
4. After 6 turns, completion message shown

---

## Logging

`utils/logger.py` exports `setup_logger(name, log_type, level)`:

- Creates `src/app/logs/<log_type>/<timestamp>.log` on first call, making parent directories as needed
- Attaches a `FileHandler` and a `StreamHandler` (stdout) with the format `[LEVEL] filename:lineno - funcName() - message`
- Guard against duplicate handlers: returns the existing logger if handlers are already attached
- `_session_log_file` is a module-level global — `log_type` is only respected on the first call; subsequent calls with a different `log_type` reuse the same file
- All pipeline and engine modules use `log_type="pipeline"` — logs write to `logs/pipeline/<timestamp>.log`
- API uses `log_type="api"` — logs write to `logs/api/<timestamp>.log`
- `logs/` is gitignored — logs are local only and never committed

`dashboard.py` additionally attaches a `DashboardLogHandler` to the root logger that captures log lines into `st.session_state.log_lines` (buffered to 100 lines) for display in the Runtime log panel.

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
    ├── api/
    │   ├── __init__.py
    │   └── main.py                    # FastAPI REST API wrapper
    └── app/
        ├── main.py
        ├── config.py
        ├── core/
        │   ├── pipeline.py
        │   └── engines/
        │       ├── base.py
        │       ├── llm/
        │       │   ├── openai_llm.py
        │       │   ├── ollama_llm.py
        │       │   └── openrouter_llm.py
        │       ├── stt/
        │       │   ├── whisper_api.py
        │       │   └── whisper_local.py
        │       └── tts/
        │           ├── openai_tts.py
        │           └── gtts_tts.py
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
| No confirmation turn in loop | Readback and confirmation are prompt-only; turn loop ends after 6 turns regardless |
| gTTS requires internet | `GTTSEngine` TTS is not fully offline despite being part of the local engine set |
| Loud non-speech above threshold | RMS fix works for silence; loud ambient noise above 0.01 still triggers Whisper hallucinations |
| Single-threaded audio | `sd.wait()` and pygame playback block the entire process; dashboard freezes during recording/playback |
| gemma3 instruction-following | Unreliable at 1B scale — field enforcement and history increase help but do not fully resolve order errors |
| Name transcription errors | Whisper struggles with proper nouns (~20% local, ~10% cloud) |
| In-memory session store | API sessions are lost on server restart; production deployment requires Redis or a database |
| OpenRouter free tier cap | 50 requests/day across all free models — limits integration testing; mock LLM for automated tests |
| Status labels not updating mid-turn | Dashboard status labels write to `st.session_state.status` but Streamlit only rerenders on user action |