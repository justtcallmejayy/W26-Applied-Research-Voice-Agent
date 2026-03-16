
# Test Results: Local Pipeline Validation — Post Plug-and-Play Migration

**Date**: March 16, 2026
**Tester**: Brendan Dileo
**Branch**: `test/post-abstraction-pipeline-validation`
**Operating System**: macOS Sonoma 14.1
**Hardware**: MacBook Air M2, 8GB RAM
**Models Tested**: gemma3:1b + Whisper base + gTTS via OnboardingPipeline

---

## 1. Background

The following test report validates the local engine set (WhisperLocalEngine + OllamaLLMEngine + GTTSEngine) with the new OnboardingPipeline architecture. The March 10 local agent baseline established that emoji violations were resolved via prompt engineering but question order errors (55%) and confirmation workflow failures (0% compliance) persisted as pipeline-level issues.

This test confirms whether those known limitations carry forward into the new pipeline, and whether the migration introduced any new issues specific to the local engine set.

Two additional sessions were run: one with microphone disabled to validate silent audio detection, and one with intentionally bad user input to evaluate pipeline resilience under the local model.

---

## 2. Changes
- CLI entry point remains in `main.py`, but relies on `OnboardingPipeline.run()`.
- STT, LLM, and TTS are now injected engine instances rather than methods on a single agent class.
- All constants and engine selection moved from hardcoded constructors to `config.py`.
- Logging routes to `logs/pipeline/` instead of `logs/local-agent/`.
- Provider switching done via `ENGINES` dict in `config.py` instead of `USE_LOCAL` flag.

---

## 3. Baseline Metrics (March 10, 2026 — LocalVoiceAgent, gemma3:1b)

| Metric | Baseline |
|--------|----------|
| Completion Rate | 27% (3/11) |
| Emoji Violations | 0% (0/11) |
| Proper Confirmation | 0% (0/11) |
| Question Order Errors | 55% (6/11) |

---

## 4. Test Execution

A total of 12 sessions were executed. Sessions 1–10 are normal onboarding runs with valid speech input. Session 11 is a no-audio test. Session 12 is an intentional bad user input test. Sessions 11 and 12 are excluded from instruction-following metric calculations. Session 7 crashed mid session due to an empty LLM response and is counted as a crash rather than a completion failure.

| Session | Completed | Emoji Violations | Proper Confirmation | Question Order Errors | Notes |
|---------|-----------|-----------------|--------------------|-----------------------|-------|
| 1 | FAIL | PASS | FAIL | FAIL | Skipped experience; asked job_preferences on turn 4; restarted from name on turn 6 |
| 2 | FAIL | PASS | FAIL | FAIL | Skipped skills on turn 2; multiple field confusions throughout |
| 3 | FAIL | PASS | FAIL | FAIL | Skipped experience; asked job_preferences on turn 4; restarted from name on turn 6 |
| 4 | FAIL | PASS | FAIL | FAIL | Skipped experience on turn 4; mixed job_preferences and experience; asked skills again on turn 6 |
| 5 | FAIL | PASS | FAIL | FAIL | Skipped experience; asked follow-up on experience instead of job_preferences on turn 5; asked skills again on turn 6 |
| 6 | FAIL | PASS | FAIL | FAIL | Skipped experience; asked job_preferences on turn 4; vague response caused follow-up; restarted from name on turn 6 |
| 7 | CRASH | PASS | FAIL | FAIL | Transcribed "And..." --> LLM returned empty string --> gTTS crash with "No text to speak" |
| 8 | FAIL | PASS | FAIL | FAIL | Skipped skills on turn 2; asked job_preferences early; multiple field confusions |
| 9 | FAIL | PASS | FAIL | FAIL | Skipped experience; asked job_preferences on turn 4; asked experience again on turn 6 |
| 10 | FAIL | PASS | FAIL | FAIL | Reached experience correctly but asked follow-up instead of advancing; restarted from name on turn 6 |
| 11 | N/A (no audio) | N/A | N/A | N/A | All 6 turns skipped correctly |
| 12 | CRASH | PASS | FAIL | FAIL | Bad user input caused LLM empty response on turn 6; gTTS crash |

---

## 5. Pipeline Timing

Timing extracted from log files across 9 valid sessions (excluding session 7 crash).

| Stage | Min | Max | Avg | March 10 Avg | Change |
|-------|-----|-----|-----|--------------|--------|
| Recording | 5.20s | 5.30s | ~5.23s | 5.23s | ~0.00s |
| Transcription | 0.68s | 2.60s | ~0.87s | 0.94s | ~-0.07s |
| LLM Generation | 0.56s | 2.35s | ~0.87s | 1.22s | ~-0.35s |
| TTS (gTTS) | 0.21s | 1.25s | ~0.57s | 1.36s | ~-0.79s |
| Playback | 0.73s | 11.33s | ~6.1s | 10.01s | ~-3.91s |
| **Total/Turn** | — | — | **~12–16s** | **~18.8s** | Faster |
 
**Key Findings:**
- Recording is highly consistent at ~5.23s.
- LLM generation is faster on average (~0.87s vs 1.22s), but this is likely due to the model losing context and producing worst ouputs.
- gTTS is significantly faster (~0.57s vs 1.36s) likely for the same reason.
- Playback is faster on average (~6.1s vs 10.01s), again, likely due to the shorter responses or context loss.
- The **faster timing** is **not** an improvement and reflects degraded response quality rather than performance gains.

---

## 6. Question Order Analysis

Question order errors occurred in all 9 valid sessions (100%). The pattern is highly consistent across sessions:


| Turn | Field | Collected Correctly | Notes |
|------|-------|---------------------|-------|
| 1 | name | 9/9 | Consistently correct |
| 2 | employment_status | 8/9 | Session 2 skipped to education |
| 3 | skills | 8/9 | Session 8 skipped skills early |
| 4 | education | 7/9 | History trim triggers here |
| 5 | experience | 2/9 | Most common failure — model jumps to job_preferences |
| 6 | job_preferences | 0/9 | Model restarted or asked wrong field in every session |

This pattern seems to confirm that the history trim is causing the local agent to provide bad output. The trim at turn 4 causes the model to lose the early conversation context, causing it to lose track of its position in the field sequence for the remaining turns.

---

## 7. Edge Case Validation
 
### 7.1 No Audio - Mic Disabled (Session 11)
 
All 6 turns were correctly skipped with energy values well below the 0.01 threshold. No API calls were made and no errors were produced.
 
| Turn | Energy | Result |
|------|--------|--------|
| 1 | 0.0002 | Skipped |
| 2 | 0.0002 | Skipped |
| 3 | 0.0002 | Skipped |
| 4 | 0.0002 | Skipped |
| 5 | 0.0002 | Skipped |
| 6 | 0.0002 | Skipped |

### 7.2 Empty LLM Response - gTTS Crash (Session 7)
 
On turn 5 of session 7, the tester said "And..." at the end of the recording window. Whisper transcribed this as a valid input, which was passed to the LLM. The LLM returned an empty string response. gTTS then failed with "No text to speak", crashing the session.
 
```
You said: 'And...' [2.60s]
Assistant: '' [0.58s]
gTTS failed: No text to speak
Unexpected error during onboarding: gTTS error (check internet connection): No text to speak
```
 
This is a new issue not observed in previous testing. The pipeline does not guard against empty LLM responses before passing them to TTS.


### 7.3 Bad User Input (Session 12)
 
The tester gave intentionally confusing and off topic responses throughout the session. The local model (gemma3:1b) handled this significantly worse than the cloud agent in the equivalent session 12 test:
 
| Turn | User Input | Agent Behaviour | Result |
|------|-----------|-----------------|--------|
| 1 | "My name is Brendan, thank you." | Correctly collected name | PASS |
| 2 | "What is a student?" | Assumed user is a student without clarifying | FAIL |
| 3 | "No, what is a student?" | Responded "Right." - lost context entirely | FAIL |
| 4 | "What do you mean because I'm asking what a student is?" | Responded "You're asking for a definition." | FAIL |
| 5 | "Yes, I'm asking for a definition." | Responded "Okay, let's start with a simple definition." | FAIL |
| 6 | "Okay, I'm waiting." | LLM returned empty string --> gTTS crash | CRASH |
 
The local model lost conversational context entirely by turn 3 and produced increasingly brief and unhelpful responses before crashing on turn 6.

---
 
## 8. Summary Metrics (9 valid sessions, excluding session 7 crash)
 
| Metric | Baseline (Mar 10) | New Pipeline (Mar 16) | Change |
|--------|------------------|----------------------|--------|
| Completion Rate | 27% (3/11) | 0% (0/9) | WORSE |
| Emoji Violations | 0% (0/11) | 0% (0/9) | NO CHANGE |
| Proper Confirmation | 0% (0/11) | 0% (0/9) | NO CHANGE |
| Question Order Errors | 55% (6/11) | 100% (9/9) | WORSE |

---

## 9. Findings

### 9.1 Completion Rate and Order Errors Worsened
Completion rate dropped from 27% to 0% and order errors increased from 55% to 100%. The 8-message history trim at turn 4 removes the context the model needs to track field position, causing failures in every session from turn 5 onward.

### 9.2 Emoji Violations — Still Resolved
Zero violations across all 10 sessions. The positive constraint prompt holds under the new pipeline with no regression.

### 9.3 Confirmation Workflow — Still Not Working
Zero sessions produced a proper confirmation, consistent with the March 10 finding. This is a pipeline-level problem — the model cannot self-trigger confirmation reliably at 1B scale.

### 9.4 Context Degradation Pattern
Turns 1–3 were consistently correct. History trim triggered at turn 4. Turns 5–6 showed field position loss in every session — experience skipped, job_preferences asked early, or session restarted from name.

### 9.5 Empty LLM Response Crashes Pipeline
Session 7 exposed a new unhandled failure — the LLM returned an empty string which was passed directly to gTTS, crashing the session with "No text to speak". The pipeline has no guard against empty responses before the TTS call.

### 9.6 Local Model More Fragile Under Bad Input
The local model collapsed after turn 2 under confusing input, producing one-word responses and eventually an empty string. The cloud agent handled equivalent input far more gracefully, confirming this is a model scale limitation.

### 9.7 Faster Timing Reflects Degraded Output
Per-turn timing is faster than the March 10 baseline but this is not an improvement. Shorter and sometimes single-word LLM responses generate faster TTS and shorter playback. The faster timing is a symptom of context loss, not a performance gain.

---

## 10. Issues Identified

**Issue 1 — Empty LLM response crashes pipeline**
When the LLM returns an empty string the pipeline passes it directly to gTTS which throws "No text to speak" and crashes the session. The pipeline needs an empty response guard before the TTS call.

**Issue 2 — Question order errors in all sessions**
The 8-message history trim at turn 4 removes the context the model needs to track field position. Requires pipeline-level field enforcement, the current field should be passed to the LLM on each turn.

**Issue 3 — No confirmation workflow**
The pipeline ends after turn 6 with no dedicated confirmation step. The model never self triggers confirmation at 1B scale. Requires a pipeline level confirmation turn.

**Issue 4 — Local model collapses under ambiguous input**
gemma3:1b loses context entirely under repeated off-topic input, producing one word responses and eventually empty strings. A model scale limitation, cannot be resolved through prompt engineering alone.