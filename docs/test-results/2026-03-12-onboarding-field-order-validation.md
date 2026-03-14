# Test Results: Onboarding Field Order Validation (Local Agent)

**Date**: March 12, 2026  
**Tester**: Dhairya Patel  
**Branch**: `test/onboarding-field-order-validation`  
**Operating System**: macOS Sonoma 14.1  
**Hardware**: MacBook Air M2, 8GB RAM  
**Models Tested**: gemma3:1b (local), Whisper base (local), gTTS

---

## 1. Test Objective

This test validates whether the voice onboarding agent correctly follows the **field order defined in `ONBOARDING_FIELDS` within `agent.onboarding_config`**.

The onboarding configuration determines the sequence of user information collected during onboarding sessions. The system prompt dynamically inserts the fields from `ONBOARDING_FIELDS`, instructing the voice assistant to collect them in that exact order.

The main goals of this test were:

- Verify that the agent asks questions in the correct order
- Confirm that changing the `ONBOARDING_FIELDS` order updates the agent behavior
- Evaluate how reliably the local agent follows multi-step onboarding instructions
- Observe system stability while running multiple onboarding sessions

All testing was performed through the **Streamlit dashboard interface** rather than CLI interaction.

---

## 2. Test Setup

Testing was conducted on the **LocalVoiceAgent implementation** using the Streamlit dashboard UI.

Each onboarding session involved speaking responses through the dashboard microphone and observing the agent’s question progression during the onboarding conversation.

The following configuration was used during testing:

- `ONBOARDING_FIELDS` defined in `onboarding_config.py`
- `gemma3:1b` used for response generation
- Whisper used for speech transcription
- gTTS used for audio response playback

---

## 3. Session Summary

A total of **15 onboarding sessions** were executed.

| Metric | Result |
|------|------|
| Total Sessions | 15 |
| Completed Sessions | 12 |
| Partial Sessions | 3 |
| Correct Field Order | 12 |
| Field Order Deviations | 3 |

Sessions were executed through the **dashboard UI workflow**, simulating real user onboarding conversations.

---

## 4. Field Order Validation

The expected field order during onboarding was:

1. name  
2. employment_status  
3. skills  
4. education  
5. experience  
6. job_preferences  

During testing, the agent generally followed this sequence when generating onboarding questions.

Example of correct onboarding progression:

name → employment_status → skills → education → experience → job_preferences

However, a few sessions showed minor deviations when the model lost conversational context or attempted to ask clarification questions.

---

## 5. Configuration Change Testing

To verify that onboarding behavior is controlled through configuration, the order of `ONBOARDING_FIELDS` was modified and onboarding sessions were repeated.

| Test Case | Action | Expected Result | Actual Result | Status |
|-----------|-------|----------------|--------------|--------|
| Prompt update validation | Modify `ONBOARDING_FIELDS` order | Prompt reflects new field order | Prompt updated dynamically | PASS |
| Sequential question flow | Run onboarding session | Agent follows configured sequence | Majority of sessions followed expected order | PASS |
| Field order modification | Move education before experience | Agent asks education earlier | Agent followed updated order in most sessions | PASS |
| System stability | Run repeated sessions | System remains stable | No crashes observed | PASS |

These tests confirmed that the onboarding sequence is primarily controlled through the configuration file.

---

## 6. Confirmation Behavior

After collecting all fields, the agent is expected to summarize the collected information and end the session with the confirmation prompt:

**Does everything look correct?**

In completed sessions, the agent generated a summary similar to the following format:

Name: Dhairya  
Employment Status: Student  
Skills: Java, Python  
Education: Diploma in Software Development  
Experience: Internship experience  
Job Preferences: Software developer role  

Does everything look correct?

This behavior confirms that the agent followed the full onboarding workflow when sessions completed successfully.

---

## 7. System Stability

System stability was also evaluated during the dashboard-based testing.

| Metric | Result |
|------|------|
| Sessions executed | 15 |
| System crashes | 0 |
| Dashboard failures | 0 |
| Agent initialization errors | 0 |

The dashboard interface remained stable throughout testing.

Audio capture, speech transcription, response generation, and audio playback all operated consistently across sessions.

---

## 8. Observations

The Local Voice Agent generally follows the onboarding configuration and prompt instructions during testing.

Most sessions progressed through the expected field order without issues. When deviations occurred, they were usually caused by the model attempting clarification questions or temporary conversational context loss.

Despite these minor deviations, the onboarding workflow completed successfully in the majority of sessions.

---

## 9. Next Steps

Potential improvements for the onboarding system include:

- Implementing pipeline-level field tracking to enforce strict field order
- Adding explicit conversation state management
- Evaluating larger local models for improved instruction-following reliability
- Expanding automated onboarding testing coverage