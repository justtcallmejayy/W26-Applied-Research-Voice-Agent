# Decisions

This document records the key technical decisions made throughout the project and the reasoning behind them.

---

## pyproject.toml over requirements.txt
**Decision:** Use pyproject.toml to manage dependencies instead of requirements.txt alone.
**Reason:** requirements.txt does not enforce Python version constraints. Dependency conflicts across macOS, Linux, and Windows team machines caused environment inconsistencies early in the project. pyproject.toml pins Python 3.10-3.13 and exact dependency versions resolving this.

---

## Dashboard as Debug Tool
**Decision:** Repurpose the dashboard from a candidate-facing form to a developer debug and audit tool.
**Reason:** Agreed with the client on January 30 that the dashboard would serve as a debug tool showing real-time logs, conversation history, turn tracking, and session parameters rather than a production UI for candidates.

---

## Dual Agent Architecture (Weeks 1–10)
**Decision:** Implement two separate agent implementations, a cloud agent (`VoiceAgent`) and a local agent (`LocalVoiceAgent`), sharing a common interface.
**Reason:** OpenAI account sharing across the team was impractical due to privacy and cost concerns. A service outage mid-Week 4 also blocked cloud development entirely. The local agent gave all team members a working implementation without API credentials and satisfied the client's plug-and-play requirement.
**Status:** Superseded in Week 11 by the plug-and-play pipeline migration (see below). Both agent classes and `onboarding_config.py` have been removed.

---

## Plug-and-Play Pipeline Migration (Week 11)
**Decision:** Replace `VoiceAgent` and `LocalVoiceAgent` with a single provider-agnostic `OnboardingPipeline` that accepts injected STT, LLM, and TTS engine instances.
**Reason:** The dual agent design required duplicating the full pipeline (record → energy check → transcribe → generate → tts → play → cleanup) in two separate classes. Any change to pipeline logic had to be applied twice. The plug-and-play layer eliminates duplication, makes provider switching a config-only change, and satisfies the client's requirement more directly than the dual class approach.
**Implementation:** `core/pipeline.py` contains `OnboardingPipeline`. `core/engines/base.py` defines abstract `STTEngine`, `LLMEngine`, `TTSEngine` interfaces. Seven concrete engine classes implement these interfaces across `core/engines/stt/`, `core/engines/llm/`, and `core/engines/tts/`.

---

## ENGINES Dict over USE_LOCAL Flag
**Decision:** Control provider selection via an `ENGINES` dict of dotted import paths in `config.py` rather than a boolean `USE_LOCAL` flag in `main.py`.
**Reason:** A boolean flag can only select between two hardcoded sets of providers. The dotted path dict allows any combination of engines to be activated without modifying pipeline or entry point code, and makes the swap a single-file config change rather than a code change. `load_engine()` resolves dotted paths at runtime using `importlib.import_module`.

---

## RMS Energy Detection for Silent Audio
**Decision:** Use soundfile to calculate RMS energy and skip turns below a 0.01 threshold before sending audio to Whisper.
**Reason:** Whisper-1 API hallucinates on silent audio instead of returning an empty string. This caused garbage transcriptions to enter the conversation history. The energy check skips silent turns entirely avoiding unnecessary API calls and preventing hallucinations from affecting the conversation flow.

---

## Positive Constraints in System Prompt
**Decision:** Rewrite the system prompt using positive constraints instead of negative ones.
**Reason:** Testing on March 10 revealed that negative constraints such as "do not use emojis" were ignored by gemma3:1b in 71% of sessions. Rewriting as positive constraints such as "use plain letters, numbers, and punctuation only" eliminated violations entirely. Positive constraints are significantly more effective at the 1B parameter scale.

---

## Central config.py
**Decision:** Consolidate all tuneable constants, model settings, onboarding fields, and system prompt into a single `config.py` file. Provider switching is done by editing the `ENGINES` dict — no changes needed elsewhere.
**Reason:** Constants were previously spread across `main.py`, `voice_agent.py`, `local_voice_agent.py`, and `onboarding_config.py`. A single configuration file supports the client's plug-and-play requirement and makes the system easier to maintain and hand off.
**Status:** Fully integrated. `main.py`, `dashboard.py`, and `api/main.py` all import from `config.py`. `onboarding_config.py` has been removed. `TTS_VOICE` and `TTS_MODEL` added so OpenAI TTS voice and model are configurable without touching engine code.

---

## Per-Turn Field Enforcement
**Decision:** Pass the current field name into `_generate()` as a context prefix on every turn rather than relying on the model to infer its position from conversation history alone.
**Reason:** Testing showed that `gemma3:1b` loses track of its position in the field sequence when conversation history is trimmed at turn 4–5, causing question order errors in every local session. Injecting `[Collecting: <field>]` as a prefix on each turn gives the model an explicit anchor regardless of history length, reducing order errors without requiring a larger model or longer context.
**Implementation:** `run()` in `pipeline.py` passes `current_field` to `_generate()` on each turn. The API (`api/main.py`) does the same in `process_turn()`.

---

## MAX_HISTORY_LENGTH Increased from 8 to 12
**Decision:** Increase conversation history cap from 8 to 12 messages.
**Reason:** The 8-message cap was reached at turn 4–5 of a 6-turn session, causing the local model to lose earlier field context before the session was complete. Increasing to 12 ensures the full session history is retained without trimming in the normal case.

---

## Empty LLM Response Guard
**Decision:** Add a guard in `_generate()` that checks for empty or None LLM responses before passing text to TTS.
**Reason:** gTTS raises "No text to speak" on an empty string, crashing the pipeline. The guard removes the user message from history and skips the turn cleanly rather than crashing.

---

## OpenRouter Integration
**Decision:** Add `OpenRouterLLMEngine` as a seventh concrete engine using OpenRouter's OpenAI-compatible API endpoint.
**Reason:** The client requested flexible model testing without being locked to a single provider. OpenRouter provides a single endpoint giving access to many free and paid models. Implemented as a drop-in `LLMEngine` — validated with 6 confirmed free models as of March 25, 2026. Provider switching requires only a config change.

---

## FastAPI REST API Wrapper
**Decision:** Expose `OnboardingPipeline` via a FastAPI REST API (`src/api/main.py`) rather than only through the CLI and Streamlit dashboard.
**Reason:** The client requested a hosted version accessible from a frontend without requiring the full Python environment. A REST API decouples the pipeline from any specific UI, allows the frontend to record audio in the browser and send it as a WAV upload, and makes the system deployable as a standalone service. The API reuses the same `load_engine()` and `ENGINES` config as the CLI — no pipeline code changes were needed.
**Implementation:** Five endpoints — `/session/start`, `/session/{id}/turn`, `/session/{id}/confirm`, `DELETE /session/{id}`, `/health`. Sessions are keyed by UUID in an in-memory dict. Audio is returned as `FileResponse` with metadata in response headers.

---

## safe_header() for HTTP Response Headers
**Decision:** Sanitise all LLM and STT output before placing it in HTTP response headers using a `safe_header()` helper.
**Reason:** HTTP headers are latin-1 encoded and cannot contain newlines. LLM responses frequently contain typographic apostrophes (`\u2019`), curly quotes, and `\n` line breaks, all of which cause `UnicodeEncodeError` or `h11.LocalProtocolError` at the ASGI layer. `safe_header()` strips newlines and encodes to latin-1 with `errors="ignore"` before any text is placed in a header.

---

## Restructured Test Suite
**Decision:** Reorganise tests into `unit/`, `integration/`, and `old/` subdirectories with a shared `conftest.py` for `sys.path` setup.
**Reason:** All tests previously lived in a flat `tests/` directory with no separation between unit tests (no API calls, fast) and integration tests (require API keys and audio fixtures, slow). Separating them allows unit tests to run in CI without credentials and integration tests to be run explicitly. `old/` retains legacy tests for reference without polluting the active test suite.
