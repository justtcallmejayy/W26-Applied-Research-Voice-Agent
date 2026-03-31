
# Test Results: OpenRouter Pipeline Validation — Post Pipeline Fixes

**Date**: March 31, 2026
**Tester**: Brendan Dileo
**Branch**: `feat/pipeline-integration`
**Operating System**: macOS Sonoma 14.1
**Hardware**: MacBook Air M2, 8GB RAM
**Engines**: OpenRouterLLMEngine, WhisperLocalEngine, GTTSEngine
**Models Tested**: arcee-ai/trinity-large-preview:free + Whisper base + gTTS via OnboardingPipeline

---

## Summary

5 complete onboarding sessions run through `OnboardingPipeline` using the OpenRouter LLM engine. All 5 sessions completed all 6 fields and produced a correct confirmation summary. Testing was halted after session 5 due to OpenRouter's free-tier daily cap (50 requests/day).

| Metric | Result |
|--------|--------|
| Sessions completed | 5 / 5 |
| Fields collected per session | 6 / 6 |
| Completion rate | 100% (5/5) |
| Correct field order | 100% (5/5) |
| Emoji violations | 0% (0/5) |
| Confirmation summary produced | 100% (5/5) |
| Pipeline crashes | 0 |
| History trim triggered | 5 / 5 (expected) |

---

## Pipeline Timing

Timing extracted from logs across all 5 sessions (per turn, 7 LLM calls + 6 STT calls per session).

### LLM Generation (OpenRouter)

| Session | Turn 1 | Turn 2 | Turn 3 | Turn 4 | Turn 5 | Turn 6 | Summary Turn | Session Avg |
|---------|--------|--------|--------|--------|--------|--------|--------------|-------------|
| 1 | 1.13s | 2.28s | 0.95s | 2.62s | 3.87s | 2.40s | 6.94s | 2.88s |
| 2 | 1.90s | 1.41s | 1.53s | 6.62s | 6.36s | 1.01s | 10.65s | 4.21s |
| 3 | 1.37s | 2.15s | 4.37s | 2.67s | 5.97s | 3.78s | 6.60s | 3.84s |
| 4 | 2.49s | 3.44s | 2.78s | 2.96s | 1.97s | 2.58s | 9.48s | 3.67s |
| 5 | 2.41s | 1.78s | 4.26s | 3.49s | 1.65s | 4.20s | 9.98s | 3.97s |
| **Avg** | **1.86s** | **2.21s** | **2.78s** | **3.67s** | **3.96s** | **2.79s** | **8.73s** | **3.71s** |

**Notable:** The confirmation summary turn is consistently the slowest LLM call (~6–11s), as expected — it requires the model to collate all 6 fields into a structured response.

### STT Transcription (Whisper base — local)

All transcription times were consistent across sessions.

| Turn | Avg Time |
|------|----------|
| Name | ~0.91s |
| Employment Status | ~0.81s |
| Skills | ~0.92s |
| Education | ~0.94s |
| Experience | ~0.86s |
| Job Preferences | ~0.88s |
| **Overall Avg** | **~0.89s** |

Whisper local transcription was stable and fast across all sessions with no timeouts or errors.

---

## Instruction-Following

| Metric | Result | Notes |
|--------|--------|-------|
| Correct field order (name -> employment -> skills -> education -> experience -> job_preferences) | 5/5 | No order violations observed |
| One question per turn | 5/5 | No multi-question turns |
| Confirmation summary at end | 5/5 | All sessions produced a structured summary with all 6 fields |
| Emoji violations | 0/5 | None observed |
| Empty / None response | 0/5 | No empty response guard triggered |
| Appropriate field acknowledgement | 5/5 | Model acknowledged each answer before moving to next field |

---

## Confirmation Summary Quality

All 5 sessions produced a 6-field confirmation summary. Minor wording variation across sessions is expected and acceptable.

| Field | Consistent Across Sessions? | Notes |
|-------|-----------------------------|-------|
| Name | PASS | "Brendan" captured correctly every time |
| Employment Status | PASS | Correctly identified as student/unemployed |
| Skills | PARTIAL | "machine" instead of "machine learning" — Whisper truncation |
| Education | PASS | High school diploma + post-secondary diploma correctly captured |
| Experience | PASS | Correctly characterised as project-based, limited professional |
| Job Preferences | PASS | Data industry / data engineering captured correctly |

---

## History Trim

`pipeline.py:192` — `Trimmed conversation history to last 12 messages` - triggered at the end of every session. This is expected behaviour: 6 user turns + 7 assistant turns = 13 messages, which exceeds `MAX_HISTORY_LENGTH = 12`. No issues observed as a result of the trim.

---

## Rate Limit Behaviour

Testing halted after session 5 due to OpenRouter's free-tier daily cap:

```
Error: free-models-per-day limit exceeded
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1775001600000  (midnight UTC)
```

5 complete sessions × 7 LLM calls = 35 calls. Combined with earlier failed test attempts (stepfun rate limit + retry calls), the 50-call daily ceiling was reached. This is a meaningful constraint for integration testing on the free tier — see Known Limitations below.

---

## Issues Found

| # | Severity | Description | Status |
|---|----------|-------------|--------|
| 1 | Low | Whisper truncates "machine learning" → "machine" consistently | Known — Whisper proper noun / trailing word limitation |
| 2 | Medium | OpenRouter free tier caps at 50 requests/day — limits integration testing | Known — free tier constraint |
| 3 | Low | Summary turn LLM latency is significantly higher (~6–11s) than field turns (~1–5s) | Expected — longer structured output |

---

## Known Limitations

- **50 requests/day free cap**: At 7 LLM calls per session, only ~7 full sessions are possible per day before hitting the ceiling. Integration tests should mock the LLM by default and reserve real API calls for explicit smoke tests.
- **Whisper trailing word truncation**: "machine learning" -> "machine" observed in every session. Affects skills field accuracy. Not a pipeline issue — inherent Whisper behaviour with trailing words.
- **gTTS requires internet**: Despite being part of the local engine set, gTTS makes outbound requests. Not a blocker for this test environment.
- **Small sample size**: 5 sessions, single tester, fixed audio inputs. Results are indicative, not statistically significant.

---

## Conclusion

`arcee-ai/trinity-large-preview:free` via `OpenRouterLLMEngine` integrates correctly with `OnboardingPipeline`. All 5 sessions completed with 100% field collection, correct order, no emoji violations, and well-formed confirmation summaries. The plug-and-play architecture held — no pipeline code changes were required to validate a third-party LLM provider.

The primary constraint for ongoing testing is the 50 requests/day free tier cap. Recommend mocking the LLM in automated integration tests and reserving real OpenRouter calls for manual smoke tests only.