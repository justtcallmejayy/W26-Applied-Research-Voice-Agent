# Test Results: Local Agent Onboarding Flow Validation

**Date**: 2026-03-13  
**Tester**: Rishyu Babariya  
**Branch**: `feat/expand-onboarding-fields`  
**Operating System**: macOS Tahoe 26.3.1
**Hardware**: MacBook Air M3, 16GB RAM  
**Models Tested**: gemma3:1b (local), Whisper base (local), gTTS (local)

---

## 1. Timing performance

This test measured the runtime performance of the local onboarding flow across five test sessions. The interaction pipeline included response generation, text-to-speech conversion, audio playback, 5-second recording, and Whisper transcription.

### Local agent (gemma3:1b)

**Summary Statistics** (5 sessions):

| Operation | Min | Max | Avg |
|-----------|-----|-----|-----|
| Recording | 5.31s | 5.46s | ~5.38s |
| Transcription | 0.40s | 1.59s | ~0.53s |
| Response Generation | 0.32s | 9.19s | ~0.69s |
| TTS Conversion | 0.17s | 2.09s | ~0.52s |
| Playback | 1.97s | 9.60s | ~5.95s |
| **Total/Turn** | — | — | **~13–16s** |

**Sample per-turn totals:**
- Session 1: generally ~12–15s per turn, except the failure turn where TTS could not run
- Session 2: generally ~13–16s per turn, with one duplicate recording event
- Session 3: generally ~13–16s per turn
- Session 4: generally ~13–15s per turn
- Session 5: generally ~13–16s per turn

**Key Findings:**
- Recording time was very consistent across all sessions.
- Whisper transcription was usually fast, but some turns were slower when speech was unclear or misrecognized.
- Most response generation times were below 1 second, but one startup response took 9.19 seconds.
- Playback time varied the most because it depended on the length of the spoken response.

---

## 2. Error handling

This section tested how the local agent handled failures and unexpected outputs observed in the log file.

| Test Case | Steps | Expected | Actual | Pass? |
|-----------|-------|----------|--------|-------|
| **Empty LLM response** | User answered the final job preference question | Agent should return a valid response or fallback message | Agent returned an empty response | FAIL |
| **TTS failure after empty response** | Empty response passed to gTTS | System should prevent TTS call or provide fallback text | gTTS failed with `No text to speak` | FAIL |
| **Repeated name question** | User provided full name | Agent should store the name and move to the next field | Agent asked for the full name again | FAIL |
| **Empty transcription** | User responded after repeated prompt | System should request the answer again gracefully | Whisper returned an empty string | FAIL |
| **Duplicate recording trigger** | Recording started after repeated prompt | Only one recording should begin | Two recording events were triggered | FAIL |
| **Onboarding completion handling** | User answered the final required field | Agent should confirm collected data and stop | Agent continued asking new questions | FAIL |
| **Recovery after failure** | User repeated the answer after an empty response | Agent should continue without crashing | Agent resumed the conversation | PASS |
| **Basic question sequencing** | Normal onboarding run | Agent should ask fields in order | Most sessions followed the expected order until the end | PASS |

**Key Findings:**
- The most serious functional issue was the empty LLM response because it caused a downstream TTS failure.
- The agent could recover after some failures, but recovery was inconsistent.
- Several issues did not crash the system, but they still broke the intended onboarding workflow.

---

## 3. Model behavior and feature testing

### 3.1 Required field collection

This test evaluated whether the local agent collected the required onboarding fields:
- name
- employment_status
- skills
- education
- job_preferences

**Results:**
- Total Sessions Tested: 5
- Sessions that reached the job preference question: 5
- Sessions that collected all required fields: 5
- Sessions that completed cleanly and stopped correctly: 0

**Examples:**

| Session | Result |
|-----|-----------|
| 1 | All required fields were mostly collected, but an empty response occurred at the final stage |
| 2 | All required fields were collected, but the agent asked for the name twice |
| 3 | All required fields were collected, but the agent continued beyond onboarding |
| 4 | All required fields were collected, but job preference questioning reopened after completion |
| 5 | All required fields were collected, but extra follow-up questions were asked |

**Key Findings:**
- The agent was generally able to collect the required onboarding information.
- The main weakness was not field collection itself, but workflow control during and after collection.

### 3.2 Question order and workflow control

This test evaluated whether the agent followed the intended onboarding order and stopped after the required fields were complete.

**Results:**
- Correct initial order observed in most sessions
- Duplicate name prompt observed in 1 session
- Off-schema continuation observed in 3 sessions
- Hard stop after final field observed in 0 sessions

**Examples:**

| Run | Observed behavior | Outcome |
|-----|-------------------|---------|
| 2 | Asked for the user’s full name again after already receiving it | FAIL |
| 3 | Continued with “preferred experience level” after onboarding should have ended | FAIL |
| 4 | Reopened job-preference-style questioning after the user had already answered | FAIL |
| 5 | Asked additional experience-related follow-up questions outside the schema | FAIL |

**Key Findings:**
- The local agent usually started the onboarding flow correctly.
- Workflow control weakened near the end of the onboarding sequence.
- There was no reliable end-of-flow confirmation or termination behavior.

### 3.3 Transcription quality

This test evaluated Whisper transcription quality based on the captured user inputs in the log file.

**Results:**
- Most standard responses were transcribed correctly
- 1 empty transcription occurred
- Some responses were truncated
- Some names and phrases were misheard or distorted

**Examples:**

| Run | Input | Observed transcription |
|-----|-------|------------------------|
| 1 | Management job preference | `I'm looking for any management level jobs in` |
| 2 | User response after repeated prompt | `` |
| 3 | User location preference | `I would love to have a job in Toronto.` |
| Additional log case | Name response | `punk Gulched Trybotty` |

**Key Findings:**
- Whisper handled clear English responses well in many turns.
- Accuracy dropped for unclear names, partial answers, and noisier speech.
- The system currently accepts clearly incorrect transcriptions as valid onboarding inputs.

---

## 4. Comparative analysis

This section compares the five onboarding sessions included in the full log file.

**Results Table:**

| Metric | Local Agent (gemma3:1b) | Notes |
|----------|-----------------|--------------|
| Total Sessions | 5 | All sessions reached later onboarding stages |
| Sessions Collecting All Required Fields | 5 | Collection was generally successful |
| Sessions with Workflow Errors | 5 | Every session had at least one issue |
| Empty LLM Responses | 1 | Caused downstream TTS failure |
| TTS Failures | 1 | Triggered by empty response |
| Repeated Question Cases | 1 | Name asked twice |
| Empty Transcriptions | 1 | Occurred during Session 2 |
| Correct Stop After Final Field | 0 | Agent never stopped correctly |
| Extra Follow-up Questions After Completion | 3 | Sessions 3, 4, and 5 |

**Key Findings:**
- The local agent can usually gather the required onboarding fields.
- The largest reliability issue is conversation-state control rather than speed.
- Final-stage confirmation and termination are currently the weakest parts of the workflow.

---

## Summary

**What Worked:**
- The local pipeline remained stable across all five sessions.
- Recording and transcription timings were consistent.
- The agent usually followed the correct question order at the beginning.
- All five sessions reached the final onboarding stages and collected the main fields.

**Issues Found:**
- Empty LLM response caused a direct TTS failure.
- One session repeated the name question after already receiving it.
- One session produced an empty transcription.
- The agent never performed a proper final confirmation summary.
- The agent did not stop correctly after collecting all required fields.
- Several sessions included follow-up questions outside the onboarding schema.
- The full log also showed a configuration warning where `new-model-name` was not found and the system fell back to `deepseek-r1:latest` before later runs continued with gemma3:1b.

**Trade-offs (if comparing implementations):**
- **Speed:** The local system was responsive enough for testing, with most turns staying in the expected range.
- **Stability:** Core services stayed running, but workflow reliability was inconsistent.
- **Usability:** The agent could collect data, but poor stopping logic and follow-up drift reduce readiness for production use.

**Next Steps:**
- Add a validation check that prevents empty LLM responses from being sent to TTS.
- Add a fallback message such as “I did not catch that, could you repeat your last answer?”
- Enforce a strict conversation state machine so completed fields cannot be reopened.
- Stop the onboarding flow immediately after the final required field.
- Add a mandatory confirmation template that reads back all collected fields.
- Add validation for clearly invalid or corrupted transcriptions before accepting them.
- Review model initialization so the configured model and fallback model are consistent.

**Recommendations (optional):**
- Replace free-form prompting with explicit per-field state tracking.
- Separate onboarding data collection from follow-up coaching logic so extra career questions cannot appear during collection.
- Add automated regression tests for duplicate prompts, empty responses, and stop-after-final-field behavior.

---
