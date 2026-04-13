# Test Results: Local Agent Onboarding Flow Validation

Date: 2026-03-13  
Tester: Rishyu Babariya  
Branch: feat/expand-onboarding-fields  
Operating System: macOS Tahoe 26.3.1  
Hardware: MacBook Air M3, 16GB RAM  
Models Tested: gemma3:1b (local), Whisper base (local), gTTS (local)

During this testing cycle, a total of **23 onboarding sessions were executed** to evaluate the stability and behavior of the local voice agent. Out of these runs, **5 sessions successfully completed the full onboarding workflow**, while the remaining sessions **terminated mid-way due to runtime interruptions, empty responses from the language model, or transcription errors caused by unclear or garbage voice input**. The detailed analysis below focuses on the **5 completed sessions**, as they provide consistent data for timing performance and workflow evaluation.

---

# 1. Timing performance

This test measured the runtime performance of the local onboarding flow across five completed test sessions. The interaction pipeline included response generation, text-to-speech conversion, audio playback, 5-second recording, and Whisper transcription.

## Local agent (gemma3:1b)

### Summary Statistics (5 sessions)

| Operation | Min | Max | Avg |
|-----------|-----|-----|-----|
| Recording | 5.31s | 5.46s | ~5.38s |
| Transcription | 0.40s | 1.59s | ~0.53s |
| Response Generation | 0.32s | 9.19s | ~0.69s |
| TTS Conversion | 0.17s | 2.09s | ~0.52s |
| Playback | 1.97s | 9.60s | ~5.95s |
| **Total/Turn** | — | — | ~13–16s |

### Sample per-turn totals

- Session 1: generally ~12–15s per turn, except the failure turn where TTS could not run  
- Session 2: generally ~13–16s per turn, with one duplicate recording event  
- Session 3: generally ~13–16s per turn  
- Session 4: generally ~13–15s per turn  
- Session 5: generally ~13–16s per turn  

### Key Findings

- Recording time was very consistent across all sessions.  
- Whisper transcription was usually fast, but some turns were slower when speech was unclear or misrecognized.  
- Most response generation times were below 1 second, but one startup response took 9.19 seconds.  
- Playback time varied the most because it depended on the length of the spoken response.

---

# 2. Error handling

This section tested how the local agent handled failures and unexpected outputs observed in the log file.

| Test Case | Steps | Expected | Actual | Pass? |
|-----------|------|----------|--------|-------|
| Empty LLM response | User answered the final job preference question | Agent should return a valid response or fallback message | Agent returned an empty response | FAIL |
| TTS failure after empty response | Empty response passed to gTTS | System should prevent TTS call or provide fallback text | gTTS failed with "No text to speak" | FAIL |
| Repeated name question | User provided full name | Agent should store the name and move to the next field | Agent asked for the full name again | FAIL |
| Empty transcription | User responded after repeated prompt | System should request the answer again gracefully | Whisper returned an empty string | FAIL |
| Duplicate recording trigger | Recording started after repeated prompt | Only one recording should begin | Two recording events were triggered | FAIL |
| Onboarding completion handling | User answered the final required field | Agent should confirm collected data and stop | Agent continued asking new questions | FAIL |
| Recovery after failure | User repeated the answer after an empty response | Agent should continue without crashing | Agent resumed the conversation | PASS |
| Basic question sequencing | Normal onboarding run | Agent should ask fields in order | Most sessions followed the expected order until the end | PASS |

### Key Findings

- The most serious functional issue was the empty LLM response because it caused a downstream TTS failure.  
- The agent could recover after some failures, but recovery was inconsistent.  
- Several issues did not crash the system, but they still broke the intended onboarding workflow.

---

# 3. Model behavior and feature testing

## 3.1 Required field collection

This test evaluated whether the local agent collected the required onboarding fields:

- name  
- employment_status  
- skills  
- education  
- job_preferences  

### Results
