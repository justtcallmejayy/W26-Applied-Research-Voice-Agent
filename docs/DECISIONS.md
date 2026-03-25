
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
**Implementation:** `core/pipeline.py` contains `OnboardingPipeline`. `core/engines/base.py` defines abstract `STTEngine`, `LLMEngine`, `TTSEngine` interfaces. Six concrete engine classes implement these interfaces across `core/engines/stt/`, `core/engines/llm/`, and `core/engines/tts/`.

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
**Status:** Fully integrated. `main.py` and `dashboard.py` both import from `config.py`. `onboarding_config.py` has been removed. Note: `pipeline.py` still hardcodes `8` for history trim length instead of importing `MAX_HISTORY_LENGTH`, and `dashboard.py` hardcodes `0.01` for the energy threshold instead of using `ENERGY_THRESHOLD`.
