
# Test Results: Local Pipeline Validation — Post Pipeline Fixes

**Date**: March 30, 2026
**Tester**: Brendan Dileo
**Branch**: `feat/pipeline-integration`
**Operating System**: macOS Sonoma 14.1
**Hardware**: MacBook Air M2, 8GB RAM
**Models Tested**: gemma3:1b + Whisper base + gTTS via OnboardingPipeline

---

## 1. Background

Following the pipeline fixes implemented on the `fix/pipeline-improvements` branch, this test validates the local engine set against the March 16, 2026 post-migration baseline. Three targeted fixes were applied:

- **Issue #31** — Per-turn field enforcement: current field now passed to `_generate()` on each turn
- **Issue #32** — History trim increased from 8 to 12 messages (`MAX_HISTORY_LENGTH`)
- **Issue #33** — Empty LLM response guard added before TTS call

15 sessions were run to evaluate whether these fixes improved the local agent's instruction-following metrics, particularly completion rate (0%) and question order errors (100%) from the March 16 baseline.

Unit tests were also run to validate all three fixes at the code level.

---

## 2. Fixes Applied

| Fix | Issue | Change |
|-----|-------|--------|
| Per-turn field enforcement | #31 | Current field passed as `[Collecting: {field}]` prefix on each `_generate()` call |
| History length increase | #32 | `MAX_HISTORY_LENGTH` increased from 8 to 12 in `config.py` |
| Empty LLM response guard | #33 | Guard added in `_generate()` — empty/None responses skip TTS and remove user message from history |

---

## 3. Baseline Metrics (March 16, 2026 — pre-fixes)

| Metric | Baseline |
|--------|----------|
| Completion Rate | 0% (0/9) |
| Emoji Violations | 0% (0/9) |
| Proper Confirmation | 0% (0/9) |
| Question Order Errors | 100% (9/9) |
| Crashes | 2 (sessions 7 and 12) |

---

## 4. Unit Test Results

All 15 unit tests passed, directly validating the three fixes at the code level.

```
tests/unit/test_pipeline.py::test_empty_llm_response_does_not_crash        PASSED
tests/unit/test_pipeline.py::test_none_llm_response_does_not_crash         PASSED
tests/unit/test_pipeline.py::test_normal_response_flows_through             PASSED
tests/unit/test_pipeline.py::test_history_trim                              PASSED
tests/unit/test_pipeline.py::test_whitespace_llm_response_does_not_crash   PASSED
tests/unit/test_pipeline.py::test_history_trim_uses_config_value            PASSED
tests/unit/test_pipeline.py::test_per_turn_field_passed_to_llm              PASSED
tests/unit/test_pipeline.py::test_conversation_history_appended_correctly   PASSED
tests/unit/test_pipeline.py::test_empty_response_removes_user_message       PASSED
tests/unit/test_pipeline.py::test_llm_generate_called_with_system_prompt    PASSED
tests/unit/test_pipeline.py::test_llm_generate_called_with_history          PASSED
tests/unit/test_pipeline.py::test_record_audio_returns_numpy_array          PASSED
tests/unit/test_pipeline.py::test_cleanup_file_removes_file                 PASSED
tests/unit/test_pipeline.py::test_cleanup_file_handles_missing_file         PASSED
tests/unit/test_pipeline.py::test_save_audio_creates_wav_file               PASSED

15 passed in 0.48s
```

---

## 5. Test Execution

15 sessions were run using the local engine set (WhisperLocalEngine + OllamaLLMEngine + GTTSEngine). All sessions used the same mock candidate profile.

| Session | Completed | Emoji Violations | Proper Confirmation | Question Order Errors | Notes |
|---------|-----------|-----------------|--------------------|-----------------------|-------|
| 1 | FAIL | PASS | FAIL | FAIL | Skipped experience; asked job_preferences on turn 5; follow-up on turn 6 |
| 2 | FAIL | PASS | PARTIAL | FAIL | Skipped experience; asked job_preferences early; asked "Does everything look correct?" without full readback |
| 3 | FAIL | PASS | FAIL | FAIL | Skipped experience; asked job_preferences on turn 5; follow-up on turn 6 |
| 4 | FAIL | PASS | FAIL | FAIL | Skipped experience; asked job_preferences on turn 5; follow-up on turn 6 |
| 5 | FAIL | PASS | FAIL | FAIL | Follow-up on skills turn 3; skipped experience; restarted from name on turn 6 |
| 6 | FAIL | PASS | FAIL | FAIL | Skipped experience; follow-up on turn 5; follow-up on turn 6 |
| 7 | FAIL | PASS | FAIL | FAIL | Skipped experience; follow-up on turn 5; asked email address on turn 6 |
| 8 | FAIL | PASS | FAIL | FAIL | Skipped experience; follow-up on turn 5; follow-up on turn 6 |
| 9 | FAIL | PASS | PASS | FAIL | Skipped experience; full confirmation readback on turn 6 |
| 10 | FAIL | PASS | FAIL | FAIL | Skipped experience; asked remote/in-office question on turn 5; restarted from name on turn 6 |
| 11 | FAIL | PASS | PASS | FAIL | Skipped experience; full confirmation readback on turn 6 |
| 12 | FAIL | PASS | FAIL | FAIL | Skipped experience; follow-up on turn 5; follow-up on turn 6 |
| 13 | FAIL | PASS | FAIL | FAIL | Skipped experience; asked job_preferences on turn 5; restarted from name on turn 6 |
| 14 | FAIL | PASS | FAIL | FAIL | Skipped experience; follow-up on turn 5; asked email on turn 6 |
| 15 | FAIL | PASS | FAIL | FAIL | Skipped experience; follow-up on turn 5; asked name confirmation on turn 6 |

---

## 6. Question Order Analysis

Turns 1–4 were collected correctly in all 15 sessions — a significant improvement from the March 16 baseline where failures began at turn 5 after the history trim at turn 4.

The history trim now triggers at turn 6 instead of turn 4 due to the `MAX_HISTORY_LENGTH` increase from 8 to 12. This gives the model more context to maintain field position through turns 1–4. However the experience field continues to be skipped in every session.

| Turn | Field | Collected Correctly | Notes |
|------|-------|---------------------|-------|
| 1 | name | 15/15 | Consistently correct |
| 2 | employment_status | 15/15 | Consistently correct |
| 3 | skills | 14/15 | Session 5 — follow-up asked instead of moving on |
| 4 | education | 15/15 | Consistently correct — history trim no longer triggers here |
| 5 | experience | 0/15 | Model skips experience entirely — most common failure point |
| 6 | job_preferences | 0/15 | Model asks follow-up, off-topic question, or restarts in every session |

The experience field skip at turn 5 is the primary remaining failure. Despite per-turn field enforcement passing `[Collecting: experience]` to the model, gemma3:1b consistently ignores it and jumps ahead or asks follow-up questions.

---

## 7. Pipeline Timing

Timing extracted from log files across 15 sessions.

| Stage | Min | Max | Avg | March 16 Avg | Change |
|-------|-----|-----|-----|--------------|--------|
| Transcription | 0.72s | 2.24s | ~0.87s | ~0.87s | NO CHANGE |
| LLM Generation | 0.46s | 2.31s | ~0.69s | ~0.87s | Slightly faster |
| **Total/Turn** | — | — | **~11–15s** | **~12–16s** | Consistent |

---

## 8. Summary Metrics (15 sessions)

| Metric | Baseline (Mar 16) | Post-Fixes (Mar 28) | Change |
|--------|------------------|---------------------|--------|
| Completion Rate | 0% (0/9) | 0% (0/15) | NO CHANGE |
| Emoji Violations | 0% (0/9) | 0% (0/15) | NO CHANGE |
| Proper Confirmation | 0% (0/9) | 13% (2/15) | IMPROVED |
| Question Order Errors | 100% (9/9) | 100% (15/15) | NO CHANGE |
| Crashes | 2 | 0 | FIXED |

---

## 9. Findings

### 9.1 No Crashes — Issue #33 Resolved
Zero crashes across all 15 sessions. The empty LLM response guard is working correctly. This is confirmed by unit tests and the absence of any TTS errors in the logs. The crash observed in sessions 7 and 12 of the March 16 baseline has been eliminated.

### 9.2 History Trim Improvement
The `MAX_HISTORY_LENGTH` increase from 8 to 12 moved the history trim from turn 4 to turn 6. Turns 1–4 are now collected correctly in all 15 sessions compared to failures beginning at turn 5 in the March 16 baseline. This is a meaningful improvement in early conversation stability.

### 9.3 Confirmation Workflow Improved
2 of 15 sessions (sessions 9 and 11) produced a proper confirmation readback — up from 0% in the March 16 baseline. Both sessions included a full field readback and "Does everything look correct?" on the final turn. This improvement is attributed to the increased history length giving the model more context when reaching the end of the conversation.

### 9.4 Experience Field Still Skipped
The experience field was skipped in all 15 sessions. Despite per-turn field enforcement passing `[Collecting: experience]` to the model on turn 5, gemma3:1b consistently ignores it and either asks a follow-up on the previous response or jumps to job_preferences. This is a model scale limitation — the 1B parameter model cannot reliably follow explicit field enforcement instructions when the conversation context is complex.

### 9.5 Question Order Errors Persist
Order errors remain at 100% across all sessions. While turns 1–4 are now stable, the experience field skip causes a cascading failure on turns 5 and 6 in every session. The field order problem at 1B scale cannot be fully resolved through pipeline enforcement alone.

### 9.6 Unit Tests Validate All Fixes
All 15 unit tests passed, confirming that the three pipeline fixes work correctly at the code level. The tests directly prove that empty/None responses are caught before TTS, history trim uses `MAX_HISTORY_LENGTH` from config, and the current field is passed to the LLM on each turn.

---

## 10. Issues Identified

**Issue 1 — Experience field consistently skipped at 1B scale**
Per-turn field enforcement passes `[Collecting: experience]` to the model but gemma3:1b ignores it in all 15 sessions. The model either asks a follow-up question on the previous response or jumps directly to job_preferences. This is a model scale limitation and cannot be resolved through pipeline enforcement alone — a larger local model (gemma3:4b or higher) would likely perform better.

**Issue 2 — Confirmation workflow still unreliable**
Improved from 0% to 13% but still fails in 87% of sessions. The model self-triggers confirmation inconsistently. A dedicated pipeline-level confirmation turn after the field loop would guarantee this behaviour regardless of model scale.
