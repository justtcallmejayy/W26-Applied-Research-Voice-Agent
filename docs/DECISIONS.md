
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

## Dual Agent Architecture
**Decision:** Implement two separate agent implementations, a cloud agent using OpenAI services and a local agent running entirely on-device.
**Reason:** OpenAI account sharing across the team was impractical due to privacy and cost concerns. A service outage mid-Week 4 also blocked cloud development entirely. The local agent gives all team members a working implementation without API credentials and satisfies the client's plug-and-play requirement.

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
**Decision:** Consolidate all tuneable constants, model settings, onboarding fields, and system prompt into a single config.py file.
**Reason:** Constants were previously spread across main.py, voice_agent.py, local_voice_agent.py, and onboarding_config.py. A single configuration file supports the client's plug-and-play requirement and makes the system easier to maintain and hand off.

---

## Abstract Engine Interfaces
**Decision:** Define abstract STTEngine, LLMEngine, and TTSEngine base classes in core/engines/base.py.
**Reason:** The client's plug-and-play requirement means STT, LLM, and TTS providers must be swappable without modifying pipeline code. Abstract interfaces define the contract any provider must implement, allowing concrete implementations to be swapped freely once integration is complete.

---
