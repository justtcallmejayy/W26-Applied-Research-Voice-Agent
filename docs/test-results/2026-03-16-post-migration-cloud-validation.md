
# Test Results: Cloud Pipeline Validation — Post Plug-and-Play Migration

**Date**: March 16, 2026
**Tester**: Brendan Dileo
**Branch**: `test/post-abstraction-pipeline-validation`
**Operating System**: macOS Sonoma 14.1
**Hardware**: MacBook Air M2, 8GB RAM
**Models Tested**: VoiceAgent (GPT-4 + Whisper-1 API + OpenAI TTS-1) via OnboardingPipeline

---

## 1. Background

The voice agent prototype was refactored in Week 11 to introduce a plug-and-play abstraction layer. The `VoiceAgent` and `LocalVoiceAgent` classes were replaced with a provider agnostic `OnboardingPipeline` that accepts injected STT, LLM, and TTS engine instances.

This test validates that the new pipeline architecture produces equivalent or better results compared to the March 11 cloud agent baseline, and that no setbacks were introduced in the new integration. Testing was conducted via the CLI using the cloud engine set (WhisperAPIEngine + OpenAILLMEngine + OpenAITTSEngine).

Two additional sessions were run to validate edge case handling: one with microphone disabled to test silent audio detection, and one with intentionally off topic and confusing responses to evaluate how resilient the agent is.

---

## 2. Changes

- CLI entry point remains in `main.py`, but relies on `OnboardingPipeline.run()`.
- STT, LLM, and TTS are now injected engine instances rather than methods on a single agent class.
- All constants and engine selection moved from hardcoded constructors to `config.py`.
- Logging routes to `logs/pipeline/` instead of `logs/cloud-agent/`.
- Provider switching done via `ENGINES` dict in `config.py` instead of `USE_LOCAL` flag.

---

## 3. Baseline Metrics (March 11, 2026 - original VoiceAgent, GPT-4)
 
| Metric | Baseline |
|--------|----------|
| Completion Rate | 100% (12/12) |
| Emoji Violations | 0% (0/12) |
| Proper Confirmation | 100% (12/12) |
| Question Order Errors | 0% (0/12) |

---

## 4. Test Execution

| Session | Name Used | Completed | Emoji Violations | Proper Confirmation | Question Order Errors |
|---------|-----------|-----------|-----------------|--------------------|-----------------------|
| 1 | Brendan | PASS | PASS | PASS | PASS |
| 2 | Brendan | PASS | PASS | PASS | PASS |
| 3 | Dhairya | PASS | PASS | PASS | PASS |
| 4 | Boolean | PASS | PASS | PASS | PASS |
| 5 | Billy | PASS | PASS | PASS | PASS |
| 6 | Jay | PASS | PASS | PASS | PASS |
| 7 | Brendan | PASS | PASS | PASS | PASS |
| 8 | Brendan | PASS | PASS | PASS | PASS |
| 9 | Brendan | PASS | PASS | PASS | PASS |
| 10 | Brendan | PASS | PASS | PASS | PASS |
| 11 | — | N/A (no audio) | N/A | N/A | N/A |
| 12 | Jeremy | PARTIAL | PASS | FAIL | FAIL |

---

## 5. Pipeline Timing

Timing based on 10 normal sessions.


| Stage | Min | Max | Avg | March 11 Avg | Change |
|-------|-----|-----|-----|--------------|--------|
| Recording | 5.21s | 5.25s | ~5.22s | 5.24s | ~0.02s |
| Transcription | 0.61s | 2.43s | ~1.3s | 1.36s | ~0.06s |
| LLM Generation | 0.95s | 5.43s | ~2.0s | 1.40s | ~+0.6s |
| TTS | 0.90s | 8.16s | ~2.6s | 2.48s | ~+0.12s |
| Playback | 1.43s | 27.13s | ~7.8s | 8.11s | ~-0.31s |
| **Total/Turn** | — | — | **~14–19s** | **~18.6s** | Consistent |

**Key Findings:**
- Recording is very consistent at roughly ~5.22s across all sessions.
- Transcription average is consistent with the March 11 baseline.
- LLM generation shows higher variance due to response length differences but remains within acceptable range.
- Confirmation turn playback is the most variable stage — reached 27.13s in session 2 due to reading back all 6 fields. This is expected behaviour consistent with previous findings.
- Overall per-turn timing is consistent with the March 11 baseline.

---

## 6. Edge Case Validation

### 6.1 No Audio: Mic Disabled (Session 11)
 
All 6 turns were correctly skipped with energy values well below the 0.01 threshold. No API calls were made and no errors were produced. Pipeline completed cleanly.
 
| Turn | Energy | Result |
|------|--------|--------|
| 1 | 0.0006 | Skipped |
| 2 | 0.0006 | Skipped |
| 3 | 0.0006 | Skipped |
| 4 | 0.0005 | Skipped |
| 5 | 0.0005 | Skipped |
| 6 | 0.0005 | Skipped |

### 6.2 Off-Topic / Confusing Responses (Session 12)
 
The tester intentionally gave confusing or off-topic responses to evaluate agent resilience.
 
| Turn | User Input | Agent Behaviour | Result |
|------|-----------|-----------------|--------|
| 1 | Echoed the agent's question back | Correctly clarified it was asking for the user's name | PASS |
| 2 | Provided valid name (Jeremy) | Session continued normally | PASS |
| 3 | "What exactly do you mean?" | Attempted to clarify the employment status question | PARTIAL |
| 4 | "Ah, I don't know." | Moved on and asked about skills | PARTIAL |
| 5 | "Skills? What's a skill?" | Explained what a skill is — went off script | FAIL |
| 6 | "Haha, project management, that's a funny word." | Asked about education instead of job preferences — field tracking drift | FAIL |
 
The agent handled isolated off-topic responses reasonably well but lost field position tracking after multiple consecutive ambiguous turns. This is a known pipeline-level limitation — the model infers its position from conversation history alone, which breaks down when the conversation goes significantly off-script.

---

## 7. Summary Metrics

| Metric | Baseline (Mar 11) | New Pipeline (Mar 16) | Change |
|--------|------------------|----------------------|--------|
| Completion Rate | 100% (12/12) | 100% (10/10) | NO CHANGE |
| Emoji Violations | 0% (0/12) | 0% (0/10) | NO CHANGE |
| Proper Confirmation | 100% (12/12) | 100% (10/10) | NO CHANGE |
| Question Order Errors | 0% (0/12) | 0% (0/10) | NO CHANGE |

---

## 8. Findings (if any)

### 8.1 No Regressions Detected
All four instruction-following metrics held at 100%/0% under the new pipeline architecture. The plug-and-play migration did not introduce any regressions in cloud agent behaviour.

### 8.2 Pipeline Timing Consistent
Per-turn timing is consistent with the March 11 baseline. Recording is highly stable at ~5.22s. LLM generation shows slightly higher variance due to response length but remains within acceptable range.

### 8.3 Agent Handles Edge Cases Well
Silent audio detection correctly skipped all 6 turns with no API calls made. The agent handled isolated off-topic responses gracefully but lost field position tracking after multiple consecutive ambiguous turns, consistent with the known no-per-turn-field-enforcement limitation.

---

## 9. Issues

**Issue 1 — No per-turn field enforcement**
The pipeline does not pass the current field to the LLM on each turn. Works reliably for normal sessions but breaks down under sustained off-topic input as observed in session 12.

**Issue 2 — Confirmation turn playback duration**
Confirmation turn playback reached 27.13s in session 2 due to reading back all 6 fields. Expected behaviour but a UX consideration for the final implementation.

---

### Findings

#### Cloud Agent

- Handles no audio well
- Handles off topic comments well

#### Local Agent
- Local Agent context quality drops off around the experience field, seems likely due to cutting context short...

- Tends to go off topic at the end of the conversation, the first half of the convo is good (around turn 3-4)

- Specifically goes off topic around experience and job prefereces - typically goes to job preferences first and then experience, sometimes goes back to name turn.

- Encountered an error where I said 'And', at the end of the recording, and the TTS failed: 

    You said: 'And...' [2.60s]
    [INFO] ollama_llm.py:78 - generate() - Generating response with local gemma3:1b...
    [INFO] ollama_llm.py:88 - generate() - Assistant: '' [0.58s]
    [INFO] pipeline.py:187 - _generate() - Trimmed conversation history to last 8 messages
    [INFO] gtts_tts.py:44 - synthesize() - Converting response to speech with gTTS...
    [ERROR] gtts_tts.py:55 - synthesize() - gTTS failed: No text to speak
    [INFO] pipeline.py:166 - cleanup_file() - Removed temporary file
    [ERROR] main.py:42 - main() - Unexpected error during onboarding: gTTS error (check internet connection): No text to speak

