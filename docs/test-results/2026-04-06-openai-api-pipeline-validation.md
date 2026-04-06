# Test Results: Cloud API Pipeline Validation

**Date**: April 6, 2026
**Tester**: Brendan Dileo
**Branch**: `feat/api-hardening`
**Operating System**: macOS Sonoma 14.1
**Hardware**: MacBook Air M2, 8GB RAM
**Test Method**: Automated — `pytest tests/integration/test_api_sess.py -v -s` with `@pytest.mark.parametrize("run_number", range(10))`
**Engines**: OpenAILLMEngine (gpt-4), WhisperAPIEngine (Whisper-1), OpenAITTSEngine (TTS-1)

---

## Summary

| Metric | Result |
|--------|--------|
| Sessions completed | 10 / 10 |
| Fields collected per session | 6 / 6 |
| API 200 OK on all turns | 10 / 10 |
| Correct field order | 10 / 10 |
| Confirmation summary produced | 10 / 10 |
| Emoji violations | 0 / 10 |
| Empty / None response | 0 / 10 |
| Pipeline crashes | 0 |
| History trim triggered | 10 / 10 (expected) |

---

## Instruction-Following Detail

| Session | Field Order Correct | Confirmation Summary | Notes |
|---------|--------------------|-----------------------|-------|
| 1 | PASS | PASS | Numbered list summary, "Does everything look correct?" |
| 2 | PASS | PASS | Numbered list summary, "Does everything look correct?" |
| 3 | PASS | PASS | Numbered list summary, "Does everything look correct?" |
| 4 | PASS | PASS | Numbered list summary, "Does everything look correct?" |
| 5 | PASS | PASS | Numbered list summary, "Does everything look correct?" |
| 6 | PASS | PASS | Numbered list summary, "Does everything look correct?" |
| 7 | PASS | PASS | Bulleted list summary, "Does everything look correct?" |
| 8 | PASS | PASS | Numbered list summary, "Does everything look correct?" |
| 9 | PASS | PASS | Numbered list summary, "Does everything look correct?" |
| 10 | PASS | PASS | Bulleted list summary, "Does everything look correct?" |

All 10 sessions collected all 6 fields in the correct order (name -> employment_status -> skills -> education -> experience -> job_preferences) and produced a structured confirmation summary ending with "Does everything look correct?".

---

## LLM Timing (OpenAILLMEngine — gpt-4)

Extracted from logs across all 10 sessions:

| Turn | Min | Max | Avg |
|------|-----|-----|-----|
| Turn 1 (name) | 1.03s | 2.06s | 1.37s |
| Turn 2 (employment_status) | 0.84s | 1.92s | 1.35s |
| Turn 3 (skills) | 0.99s | 2.15s | 1.57s |
| Turn 4 (education) | 1.23s | 1.73s | 1.41s |
| Turn 5 (experience) | 0.98s | 1.74s | 1.24s |
| Turn 6 (job_preferences) | 1.04s | 1.64s | 1.28s |
| Summary / confirmation | 1.93s | 3.99s | 2.87s |
| **Overall avg** | | | **~1.58s** |

Notable: Summary turn is consistently the slowest LLM call as expected - GPT-4 must collate all 6 fields into a structured response. All individual turn averages are well within the 3-second per-stage success criterion.

---

## STT Timing (WhisperAPIEngine — Whisper-1)

| Turn | Min | Max | Avg |
|------|-----|-----|-----|
| All turns | 0.61s | 8.30s | ~1.48s |

One outlier observed in session 7 - employment_status turn took 8.30s (Whisper API latency spike). All other turns were within the normal 0.61–2.66s range. This is consistent with previously documented Whisper API latency variability and is not a pipeline issue.

---

## TTS Timing (OpenAITTSEngine — TTS-1)

| Stage | Min | Max | Avg |
|-------|-----|-----|-----|
| Short responses (turns 1–3) | 1.34s | 3.05s | ~2.00s |
| Medium responses (turns 4–6) | 1.75s | 5.21s | ~2.70s |
| Summary / confirmation turn | 4.03s | 8.04s | ~6.07s |

Summary turn TTS is the single slowest stage in the pipeline — generating audio for the full 6-field confirmation block takes significantly longer than single-field responses. The 8.04s outlier in session 10 is consistent with prior OpenAI TTS latency variability on longer outputs.

---

## Per-Session Total (approx)

~40–55s per session end-to-end via API. The summary turn alone accounts for approximately 10–12s (LLM + TTS combined), dominating total session time.

---

## Confirmation Summary Quality

All 10 sessions produced a well-formed 6-field confirmation summary. GPT-4 used varied formatting across sessions (numbered list, bulleted list, inline prose) but all summaries contained all 6 fields and ended with "Does everything look correct?".

| Field | Captured Correctly | Notes |
|-------|--------------------|-------|
| Name | 10 / 10 | "Brendan" captured correctly every session |
| Employment Status | 10 / 10 | Student / unemployed correctly identified |
| Skills | 10 / 10 | Python, NumPy, Machine Learning — full transcription, no truncation |
| Education | 10 / 10 | High school diploma + post-secondary in progress |
| Experience | 10 / 10 | Limited professional experience, project-based correctly characterised |
| Job Preferences | 10 / 10 | Data industry / data engineering captured correctly |

Notable: WhisperAPIEngine (Whisper-1) correctly transcribed "NumPy and Machine Learning" in full across all sessions, unlike WhisperLocalEngine (base) which consistently truncated to "NumPy and machine". This is consistent with prior transcription accuracy findings.

---

## History Trim

`pipeline.py - _generate() - Trimmed conversation history to last 12 messages` triggered at the end of every session. This is expected: 6 user turns + 7 assistant turns (including seeded opening) = 13 messages, which exceeds MAX_HISTORY_LENGTH = 12. No instruction-following issues observed as a result of the trim.

---

## Comparison: Cloud vs Groq (April 6, 2026)

| Metric | Cloud (GPT-4) | Groq (llama-3.1-8b-instant) |
|--------|--------------|------------------------------|
| Sessions tested | 10 | 10 |
| Completion rate | 100% | 100% |
| Correct field order | 100% | 100% |
| Confirmation summary | 100% | 100% |
| Emoji violations | 0% | 0% |
| LLM avg latency (field turns) | ~1.37s | ~0.21–2.19s (varies by turn) |
| LLM avg latency (summary turn) | ~2.87s | ~3.18s |
| STT avg latency | ~1.48s | ~0.84s (local) |
| TTS avg latency (field turns) | ~2.00–2.70s | ~0.30–0.85s (gTTS) |
| TTS avg latency (summary turn) | ~6.07s | ~2.26–4.98s |
| Skills transcription accuracy | Full — "Machine Learning" | Truncated — "machine" |
| Pipeline crashes | 0 | 0 |

---

## Issues Found

| # | Severity | Description | Status |
|---|----------|-------------|--------|
| 1 | Low | Whisper API latency spike on session 7 employment_status turn (8.30s) | Known — API latency variability, not a pipeline issue |
| 2 | Low | Summary turn TTS latency high (up to 8.04s) | Expected — longer structured output |

---

## Conclusion

The cloud engine set (GPT-4 + Whisper-1 + OpenAI TTS-1) integrates correctly with OnboardingPipeline via the REST API. All 10 sessions completed with 100% field collection, correct field order, no emoji violations, no crashes, and well-formed confirmation summaries in every session. Results are consistent with all prior cloud validation runs.

The conversation history seeding fix is confirmed working across the cloud engine set — GPT-4 correctly treats name as already collected from turn 1 in all 10 sessions. WhisperAPIEngine correctly transcribes full skill names including trailing words, outperforming the local Whisper base model on transcription accuracy.

Both the cloud and Groq engine sets achieve identical instruction-following metrics (100% across all criteria), validating the plug-and-play architecture. The primary difference is cost and latency profile — cloud TTS is significantly slower and more expensive on the summary turn, while Groq LLM is faster on early turns but shows higher variability on later turns due to free-tier infrastructure.
