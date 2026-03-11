
# Test Results: Cloud Agent Updated Prompt Validation

**Date**: March 11, 2026
**Tester**: Brendan Dileo
**Branch**: `fix/local-agent-prompt-improvements`
**Operating System**: macOS Sonoma 14.1
**Hardware**: MacBook Air M2, 8GB RAM
**Models Tested**: VoiceAgent (GPT-4 + Whisper-1 + OpenAI TTS)

---

## 1. Background
Following the local agent prompt improvements tested on March 10, 2026, the same updated system prompt was validated against the cloud agent to confirm that changes which improved emoji compliance did not regress any metrics that were already passing on the cloud agent, and to establish an updated cloud baseline for comparison with local agent results.

---

## 2. Baseline Metrics (March 2, 2026 - original prompt, GPT-4)
| Metric | Baseline |
|--------|----------|
| Completion Rate | 100% (7/7) |
| Emoji Violations | 0% (0/7) |
| Proper Confirmation | 100% (7/7) |
| Question Order Errors | 0% (0/7) |

---


## 3. Validation Testing

### 3.1 Test Execution - 12 Sessions (GPT-4 + Updated Prompt)

| Session | Interface | Completed | Emoji Violations | Proper Confirmation | Question Order Errors |
|---------|-----------|-----------|------------------|-------------------|-----------------------|
| 1  | CLI | PASS | PASS | PASS | PASS |
| 2  | CLI | PASS | PASS | PASS | PASS |
| 3  | CLI | PASS | PASS | PASS | PASS |
| 4  | CLI | PASS | PASS | PASS | PASS |
| 5  | CLI | PASS | PASS | PASS | PASS |
| 6  | CLI | PASS | PASS | PASS | PASS |
| 7  | CLI | PASS | PASS | PASS | PASS |
| 8  | CLI | PASS | PASS | PASS | PASS |
| 9  | CLI | PASS | PASS | PASS | PASS |
| 10 | CLI | PASS | PASS | PASS | PASS |
| 11 | CLI | PASS | PASS | PASS | PASS |
| 12 | CLI | PASS | PASS | PASS | PASS |

### 3.2 Emoji Violation Detail
Zero violations across all 12 sessions. The cloud agent was already compliant
on the original prompt, and the updated prompt did not introduce any regression.

### 3.3 Confirmation Workflow Detail
All 12 sessions produced a proper confirmation with full field readback ending
with "Does everything look correct?" The model generated correct and complete
readbacks in every session without any prompting or correction from the user.

### 3.4 Question Order Detail
Zero order errors across all 12 sessions. Sessions 9, 11, and 12 include
explicit turn logging (`Starting turn X of 6 — collecting: Y`) confirming the
pipeline moved through all 6 fields in the correct sequence. The remaining
sessions show correct sequential questioning in the agent response log.

---

## 4. Summary Metrics (12 sessions)

| Metric | Baseline (Mar 2) | Updated Prompt (Mar 11) | Change |
|--------|-----------------|------------------------|--------|
| Completion Rate | 100% (7/7) | 100% (12/12) | NO CHANGE |
| Emoji Violations | 0% (0/7) | 0% (0/12) | NO CHANGE |
| Proper Confirmation | 100% (7/7) | 100% (12/12) | NO CHANGE |
| Question Order Errors | 0% (0/7) | 0% (0/12) | NO CHANGE |

---

## 5. Findings

### 5.1 Emoji Violations - NO REGRESSION
The cloud agent maintained 0% emoji violations under the updated prompt,
consistent with the March 2 baseline. No change in behaviour observed.

### 5.2 Confirmation Workflow - NO REGRESSION
All 12 sessions produced a correct confirmation with full field readback.
The cloud agent maintained 100% compliance under the updated prompt with no
regression from the March 2 baseline.

### 5.3 Question Order - NO REGRESSION
Zero order errors under the updated prompt, consistent with the baseline. The
cloud agent maintained correct sequential field collection across all 12 sessions.

### 5.4 Cloud vs Local Comparison (Updated Prompt)
With the same updated prompt applied to both agents, the performance gap is
significant across all metrics:

| Metric | Cloud (GPT-4) | Local (gemma3:1b) |
|--------|--------------|------------------|
| Completion Rate | 100% | 27% |
| Emoji Violations | 0% | 0% |
| Proper Confirmation | 100% | 0% |
| Question Order Errors | 0% | 55% |

Emoji compliance is the only metric where both agents perform equally. All other metrics show the local agent failing at a rate that the cloud agent does not, confirming that the remaining local agent failures are due to the model scale rather than prompt quality.

---

## 6. Issues Identified

**Issue 1 — Turn logging inconsistent across sessions**
Sessions 1-8 and 10 do not include turn-level logging (`Starting turn X of 6`).
Sessions 9, 11, and 12 do. This suggests the turn logging added to main.py is not present in all execution paths, likely because some sessions were run via an older version of main.py or a different entry point.