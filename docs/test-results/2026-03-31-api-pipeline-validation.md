# Test Results: API Pipeline Validation

**Date**: March 31, 2026
**Tester**: Brendan Dileo
**Branch**: `feat/pipeline-integration`
**Operating System**: macOS Sonoma 14.1
**Hardware**: MacBook Air M2, 8GB RAM
**Test Method**: Automated — `pytest tests/integration/test_api_sess.py -v -s` with `@pytest.mark.parametrize("run", range(5))`

---

## Local Engine Set

**Engines**: WhisperLocalEngine, OllamaLLMEngine (`gemma3:1b`), GTTSEngine

### Summary

| Metric | Result |
|--------|--------|
| Sessions completed | 5 / 5 |
| Fields collected per session | 6 / 6 |
| API 200 OK on all turns | 5/5 |
| Correct field order | 3/5 |
| Confirmation summary produced | 1/5 |
| Emoji violations | 0/5 |
| Empty / None response | 0/5 |
| Pipeline crashes | 0 |
| History trim triggered | 5/5 (expected) |

### Instruction-Following Detail

| Session | Field Order Correct | Confirmation Summary | Notes |
|---------|--------------------|-----------------------|-------|
| 1 | FAIL | FAIL | Skipped experience — asked "What kind of projects have you worked on?" on turn 5 instead of collecting job_preferences |
| 2 | FAIL | FAIL | Skipped experience — asked "What type of role or industry are you interested in?" on turn 4 (education turn), then re-asked experience-style question on turn 5 |
| 3 | PASS | PASS | All fields in order — produced "Does everything look correct?" summary on turn 6 |
| 4 | FAIL | FAIL | Skipped experience — asked "Do you have any internships or co-op placements?" on turn 5 after already moving past experience field, then asked for name again in summary turn |
| 5 | PASS | FAIL | Fields collected in correct order but summary turn asked "Do you have any specific tools or technologies?" instead of confirming |

### LLM Timing (OllamaLLMEngine — gemma3:1b)

| Stage | Avg Time |
|-------|----------|
| Opening message | ~1.08s |
| Field turns (1–5) | ~0.63s |
| Summary/final turn | ~0.59s |
| **Overall LLM avg** | **~0.68s** |

### STT Timing (WhisperLocalEngine — base)

| Stage | Avg Time |
|-------|----------|
| All turns | ~0.84s |

### TTS Timing (GTTSEngine)

| Stage | Avg Time |
|-------|----------|
| Short responses | ~0.30–0.45s |
| Medium responses | ~0.50–0.75s |
| Long responses (summary) | ~0.35–0.65s |

### Per-Session Total (approx)
~10–13s per session end-to-end via API.

---

## Cloud Engine Set

**Engines**: WhisperAPIEngine (Whisper-1), OpenAILLMEngine (GPT-4), OpenAITTSEngine (TTS-1)

### Summary

| Metric | Result |
|--------|--------|
| Sessions completed | 5 / 5 |
| Fields collected per session | 6 / 6 |
| API 200 OK on all turns | 5/5 |
| Correct field order | 5/5 |
| Confirmation summary produced | 5/5 |
| Emoji violations | 0/5 |
| Empty / None response | 0/5 |
| Pipeline crashes | 0 |
| History trim triggered | 5/5 (expected) |

### Instruction-Following Detail

| Session | Field Order Correct | Confirmation Summary | Notes |
|---------|--------------------|-----------------------|-------|
| 1 | PASS | PASS | Full numbered summary with all 6 fields, "Does everything look correct?" |
| 2 | PASS | PASS | Full numbered summary with all 6 fields, "Does everything look correct?" |
| 3 | PASS | PASS | Full bulleted summary with all 6 fields, "Does everything look correct?" |
| 4 | PASS | PASS | Full numbered summary with all 6 fields, "Does everything look correct?" |
| 5 | PASS | PASS | Full numbered summary with all 6 fields, "Does everything look correct?" |

### LLM Timing (OpenAILLMEngine — GPT-4)

| Session | Turn 1 | Turn 2 | Turn 3 | Turn 4 | Turn 5 | Turn 6 | Summary | Session Avg |
|---------|--------|--------|--------|--------|--------|--------|---------|-------------|
| 1 | 2.16s | 2.46s | 3.07s | 3.38s | 1.64s | 1.64s | 3.64s | 2.57s |
| 2 | 0.79s | 1.01s | 1.82s | 1.95s | 1.76s | 1.62s | 3.69s | 1.80s |
| 3 | 1.36s | 1.23s | 1.53s | 1.61s | 1.57s | 1.52s | 4.11s | 1.85s |
| 4 | 0.81s | 1.21s | 0.95s | 1.44s | 1.56s | 1.03s | 5.42s | 1.77s |
| 5 | 0.85s | 1.21s | 0.95s | 1.44s | 1.56s | 1.03s | 3.97s | 1.57s |
| **Avg** | **1.19s** | **1.42s** | **1.66s** | **1.98s** | **1.62s** | **1.37s** | **4.17s** | **1.91s** |

Summary turn is consistently the slowest LLM call, as expected — collating all 6 fields into a structured response.

### STT Timing (WhisperAPIEngine — Whisper-1)

| Turn | Avg Time |
|------|----------|
| All turns | ~1.38s |

Notable: One outlier in session 2 (experience turn: 6.42s) and session 4 (education turn: 4.92s) — likely Whisper API latency spikes.

### TTS Timing (OpenAITTSEngine — TTS-1)

| Stage | Avg Time |
|-------|----------|
| Short responses | ~1.50–2.00s |
| Medium responses | ~2.50–3.50s |
| Long responses (summary) | ~4.91–7.50s |

Summary turn TTS is the single slowest stage in the cloud pipeline — generating audio for a 6-field confirmation block takes significantly longer than single-field responses.

### Per-Session Total (approx)
~35–50s per session end-to-end via API (dominated by cloud TTS latency on summary turn).

---

## Local vs Cloud Comparison

| Metric | Local (gemma3:1b) | Cloud (GPT-4) |
|--------|-------------------|---------------|
| Completion rate | 100% (5/5) | 100% (5/5) |
| Correct field order | 60% (3/5) | 100% (5/5) |
| Confirmation summary | 20% (1/5) | 100% (5/5) |
| Emoji violations | 0% | 0% |
| LLM avg latency | ~0.68s | ~1.91s |
| STT avg latency | ~0.84s | ~1.38s |
| TTS avg latency (field turns) | ~0.45s | ~2.30s |
| TTS avg latency (summary turn) | ~0.45s | ~6.20s |
| Approx session duration | ~10–13s | ~35–50s |
| Pipeline crashes | 0 | 0 |

---

## Issues Found

| # | Severity | Description | Status |
|---|----------|-------------|--------|
| 1 | High | gemma3:1b skips experience field in 3/5 sessions — asks job_preferences-style question early | Known — 1B model instruction-following limitation |
| 2 | Medium | gemma3:1b fails to produce confirmation summary in 4/5 sessions | Known — prompt compliance unreliable at 1B scale |
| 3 | Low | Cloud TTS summary turn latency high (~4.9–7.5s) | Expected — longer output text, not a bug |
| 4 | Low | Whisper API latency spikes on some turns (up to 6.42s) | Known — API latency variability |

---

## Conclusion

The FastAPI wrapper integrates correctly with `OnboardingPipeline` for both engine sets. All 10 sessions (5 local, 5 cloud) completed with `200 OK` on every turn and no pipeline crashes. The API-level behaviour — session creation, per-turn audio upload, field tracking, and session cleanup — is stable across both engine sets.

Cloud (GPT-4) maintains 100% field order compliance and confirmation summary production through the API, consistent with previous CLI validation results. Local (gemma3:1b) continues to show the same instruction-following limitations seen in CLI testing — the API wrapper does not introduce new failures but also cannot compensate for the model's limitations at 1B scale.

For production use, the cloud engine set is recommended. The local engine set is suitable for development and offline testing where response quality is not critical.
