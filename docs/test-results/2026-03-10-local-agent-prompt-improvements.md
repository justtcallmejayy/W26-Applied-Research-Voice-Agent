
# Test Results: Local Agent Prompt Improvements

**Date**: March 10, 2026
**Tester**: Brendan Dileo
**Branch**: `fix/local-agent-prompt-improvements`
**Operating System**: macOS Sonoma 14.1
**Hardware**: MacBook Air M2, 8GB RAM
**Models Tested**: LocalVoiceAgent (gemma3:1b + Whisper base + gTTS)

---

## 1. Background
While testing the expanded 6-field flow on March 2, 2026, the local agent showed three critical instruction-following failures: 71% emoji violation rate, 0% proper confirmation workflow compliance, and 29% question order errors.

The original system prompt relied heavily on negative constraints such as "do not use emojis" and "do not skip fields" which are known to perform poorly with smaller parameter models. This test validates whether rewriting the prompt using positive constraints and explicit field-specific instructions improves these metrics.

Testing was conducted across both the CLI (main.py) and the Streamlit dashboard to evaluate consistency across both interfaces.
---


## 2. Baseline Metrics (March 2, 2026 - original prompt, gemma3:1b)
| Metric | Baseline |
|--------|----------|
| Completion Rate | 71% (5/7) |
| Emoji Violations | 71% (5/7) |
| Proper Confirmation | 0% (0/7) |
| Question Order Errors | 29% (2/7) |

---

## 3. Validation Testing

### 3.1 Test Execution - 11 Sessions (gemma3:1b + Updated prompt)
Note: Sessions 3 and 7 excluded due to mic hardware failures (all-silent turns).
11 sessions used for metric calculations.

| Session | Interface | Completed | Emoji Violations | Proper Confirmation | Question Order Errors |
|---------|-----------|-----------|-----------------|--------------------|-----------------------|
| 1 | Dashboard | FAIL | PASS | FAIL | PASS |
| 2 | Dashboard | FAIL | PASS | FAIL | PASS |
| 3 | CLI | INVALID | N/A | N/A | N/A |
| 4 | CLI | PARTIAL | PASS | FAIL | PASS |
| 5 | CLI | FAIL | PASS | FAIL | FAIL |
| 6 | CLI | PARTIAL | PASS | FAIL | PASS |
| 7 | CLI | INVALID | N/A | N/A | N/A |
| 8 | CLI | PARTIAL | PASS | FAIL | PASS |
| 9 | CLI | PARTIAL | PASS | FAIL | PASS |
| 10 | CLI | FAIL | PASS | FAIL | FAIL |
| 11 | CLI | FAIL | PASS | FAIL | FAIL |
| 12 | CLI | FAIL | PASS | FAIL | FAIL |
| 13 | Dashboard | FAIL | PASS | FAIL | FAIL |

### 3.2 Emoji Violation Detail
Zero violations observed across all 13 sessions. The updated prompt instruction
"Use plain letters, numbers, and punctuation only in every response" proved
effective as a positive constraint. This is a significant improvement over the
original "Do not use emojis" instruction which was violated in 71% of sessions.

### 3.3 Confirmation Workflow Detail
Zero sessions produced a proper confirmation. Observed failure modes:

Session 1: Agent said "Does everything look correct?" with no field readback,
only after the user asked "Were you supposed to end?"

Sessions 4, 6, 8, 9: Agent collected all fields correctly but asked a follow-up
question instead of triggering confirmation:
- "Do you have any specific tools or libraries you're familiar with?"
- "Do you have any specific job titles you're considering?"
- "Do you have any specific data engineering roles you're aiming for?"
- "Do you have any specific areas within the data industry you're interested in?"

Sessions 10, 11, 12, 13: Agent lost track of field position entirely before
reaching confirmation.

### 3.4 Question Order Detail
Order errors occurred in 6 of 11 valid sessions (55%). The experience field
was the most common point of failure — the model consistently skipped or
misplaced it. Notable examples:

Session 5: Agent asked "What's your current job title?" as a follow-up on
employment_status turn, effectively skipping the skills collection on that turn.

Session 10: Agent moved to job_preferences on the experience turn, then
restarted from name when user pushed back.

Session 11: Agent jumped from employment_status directly to asking about
education/job_preferences, skipping skills collection entirely.

Session 13: Agent skipped experience. User said "Aren't you supposed to be
asking me about my experience?" — agent acknowledged and recovered but never
reached confirmation.

### 3.5 History Trim Correlation
A strong correlation was observed between conversation history trimming and
order errors. The log line "Trimmed conversation history to last 8 messages"
appears at turn 4-5 in all sessions and precedes the majority of order failures.
When the model loses its early context it loses track of which fields have been
collected, causing skipping and restarting behaviour.

### 3.6 Experience Field Ambiguity
Moving education before experience had a partial effect. The model used the
correct wording from the prompt — "professional work experience or any
internships and co-op placements" — in sessions where it reached the experience
field. However the field was skipped or misplaced so frequently that the
ambiguity improvement was difficult to isolate.

---

## 4. Summary Metrics (11 valid sessions)

| Metric | Baseline | Updated Prompt | Change |
|--------|----------|---------------|--------|
| Completion Rate | 71% (5/7) | 27% (3/11) | WORSE |
| Emoji Violations | 71% (5/7) | 0% (0/11) | FIXED |
| Proper Confirmation | 0% (0/7) | 0% (0/11) | NO CHANGE |
| Question Order Errors | 29% (2/7) | 55% (6/11) | WORSE |

---

## 5. Findings


### 5.1 Emoji Violations - RESOLVED via prompt engineering
Rewriting the emoji instruction as a positive constraint completely eliminated
violations. "Use plain letters, numbers, and punctuation only" produced 0%
violations vs 71% with the original negative constraint "Do not use emojis."
This confirms that positive constraints are significantly more effective than
negative constraints for a 1B parameter model.

### 5.2 Confirmation Workflow - NOT RESOLVED by prompt engineering
The confirmation failure persists at 0% compliance. The prompt improvement
alone is insufficient — the model either substitutes a follow-up question for
the confirmation step, or loses track of its position in the conversation before
reaching confirmation. This is a pipeline-level problem that requires the
pipeline itself to trigger and generate the confirmation rather than relying on
the model to do so.

### 5.3 Question Order - WORSENED
Order errors increased from 29% to 55%. The root cause identified is the
conversation history trim at 8 messages occurring at turn 4-5. When the model
loses its earlier context it cannot reliably track which fields have been
collected. This is a pipeline-level issue — the model needs to be told which
field to collect on each turn rather than inferring position from conversation
history alone.

### 5.4 Prompt Engineering vs Model Scale
The emoji result demonstrates that prompt engineering can solve certain
instruction-following failures even at 1B parameter scale. However, multi-step
sequential tasks such as field ordering and confirmation workflows appear to
exceed the reliable instruction-following capability of gemma3:1b regardless of
prompt quality. These behaviours require pipeline enforcement rather than prompt
engineering.

---

## 6. Issues Identified

**Issue 1 — Conversation history trim causes field order failures**
The 8-message history trim at turn 4-5 removes context the model needs to track
its position in the field collection sequence. This is the primary driver of
order errors in longer sessions.

**Issue 2 — Pipeline does not enforce field collection per turn**
Neither main.py nor dashboard.py passes the current field to generate_response().
The model is expected to determine what to collect next from conversation history
alone, which is unreliable at 1B scale.

**Issue 3 — No confirmation turn in the pipeline**
The pipeline ends immediately after the last field turn with no dedicated
confirmation step. The model is expected to self-trigger confirmation, which it
never does reliably.

**Issue 4 — Job preferences scope creep persists**
Even in sessions where all fields are collected correctly, the model asks
follow-up questions on the job_preferences turn instead of moving to
confirmation. Seen in 4 of 11 valid sessions.

