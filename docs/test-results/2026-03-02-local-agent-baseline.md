# **Test Results: Dashboard UI, Edge Cases & Debug Panel Validation**

**Date**: 2026-03-04

**Tester**: Jay Choksi

**Branch**: test/2026-03-04-bad-edge-case

**Operating System**: macOS Tahoe 26.1

**Hardware**: MacBook Pro M4 Pro, 24GB RAM

**Models Tested**: gemma3:1b (Ollama local), Whisper (base)

## **1\. Dashboard Initialization & Configuration Controls**

This section validates that the Streamlit onboarding dashboard loads correctly, displays all required UI elements, and allows the user to modify parameters (which correctly lock during an active session).

| Test Case                            | Steps                                 | Expected                                 | Actual                                                                                                          | Pass/Fail |
| :----------------------------------- | :------------------------------------ | :--------------------------------------- | :-------------------------------------------------------------------------------------------------------------- | :---- |
| **Dashboard loads successfully**     | Open dashboard and refresh page       | Dashboard loads without errors           | Dashboard loaded successfully. All CSS styles and container layouts appeared correctly.                         | PASS  |
| **Title and description visible**    | Observe main header area              | Title and subtitle displayed             | "Voice Agent Onboarding Dashboard" is prominent. Caption correctly identifies it as a prototype.                | PASS  |
| **Sidebar configuration visible**    | Inspect sidebar panel                 | Configuration controls visible           | Sidebar rendered correctly with all four main sections (Configuration, Audio, Local Models, Onboarding Fields). | PASS  |
| **Start session button present**     | Inspect bottom of sidebar             | Button visible and clickable             | "▶ Start session" button is visible and active.                                                                 | PASS  |
| **Onboarding fields displayed**      | Inspect field list                    | All 6 onboarding fields visible          | Correctly lists: name, employment_status, skills, experience, education, job_preferences.                       | PASS  |
| **Agent selection toggle**           | Switch between Local and Cloud agents | Selected option updates correctly        | Toggling between options works. UI state is maintained correctly.                                               | PASS  |
| **Recording duration slider**        | Adjust duration (3–15s)               | Value updates correctly                  | Slider is responsive. Recorded overhead (approx. \+2s) was noted in execution phase.                            | PASS  |
| **Local model settings visibility**  | Toggle Agent choice                   | Local models hide when Cloud is selected | Logic works as intended; local inputs disappear when OpenAI is selected.                                        | PASS  |
| **Controls disabled during session** | Start session and check sidebar       | Controls become un-editable              | All sidebar inputs were successfully greyed out/disabled while the session was active.                          | PASS  |

**Key Findings:**

- Initial UI rendering is stable.
- The sidebar provides a clear separation between audio settings and model settings.
- The dynamic UI logic (hiding/showing local model inputs) is working correctly.
- Disabling inputs during the session prevents runtime crashes from mid-session config changes.

## **2\. Error Handling & Edge Cases**

Validating UI resilience when the agent fails to transcribe audio (e.g., silent audio, mumbling, or missing microphone permissions).

**Normal Recording State:**

| Test Case               | Steps                          | Expected                   | Actual                                                                             | Pass/Fail |
| :---------------------- | :----------------------------- | :------------------------- | :--------------------------------------------------------------------------------- | :---- |
| **Error: Empty Audio**  | Click record but do not speak  | System shows error message | UI displayed "ERROR: Nothing was transcribed, please speak clearly and try again." | PASS  |
| **Retry Functionality** | Click "Retry turn" after error | Returns to READY state     | Button successfully cleared the error and re-enabled the Record button.            | PASS  |

**Key Findings:**

- The "Nothing was transcribed" error handling is robust.
- The "Retry" button successfully prevents session deadlocks and keeps the current turn context intact.

**Error State Evidence:**

![alt text](<../diagrams/test-report-images/Screenshot 2026-03-04 at 19.32.32.png>)
## **3\. Session Lifecycle, Turn Execution & Observability**

This section validates the core onboarding workflow, the accuracy of the debug trackers, and the runtime observability required for Applied Research performance tracking.

| Test Case                | Steps                                      | Expected                    | Actual                                                                                 | Pass/Fail   |
| :----------------------- | :----------------------------------------- | :-------------------------- | :------------------------------------------------------------------------------------- | :------ |
| **Start session**        | Click "Start session"                      | Opening greeting starts     | Session initialized. Agent asked "First off, could you please tell me your name?"      | PASS    |
| **Turn progression**     | Speak "I am student" for employment status | Turn counter increments     | Tracker moved employment_status to DONE and skills to ACTIVE.                          | PASS    |
| **Debug: System Prompt** | Expand "System prompt" tab                 | Displays correct guidelines | Guidelines for concise, conversational, and emoji-free responses were clearly visible. | PASS    |
| **Debug: Raw JSON**      | Expand "Raw conversation history"          | Shows structured log        | Valid JSON displayed roles for "assistant" and "user" with correct text content.       | PASS    |
| **Progress sync**        | Check top header vs tracker                | Header matches tracker      | **Mismatch**: Top header showed "Turn 2 of 6" while tracker showed Turn 3 as ACTIVE.   | PARTIAL |
| **Session Parameters**   | Expand Session Parameters                  | Accurate metadata display   | Correctly lists agent_class, gemma3:1b, etc.                                           | PASS    |
| **Runtime log output**   | Expand Runtime Log tab                     | Real-time logs from app.log | Panel displays "No log output yet."                                                    | FAIL    |

**Key Findings:**

- **Logic Validation:** The agent successfully extracts fields (e.g., recognizing "I am student" as a valid employment status).
- **Visual Sync:** An off-by-one error exists in the progress header that needs to be synced with the 0-indexed tracker logic.
- **Runtime Log Disconnect:** System logs are not appearing in the dashboard debug tab. This is a high-priority fix for the next sprint to allow for real-time latency monitoring.

**Observability Evidence:**
![alt text](<../diagrams/test-report-images/Screenshot 2026-03-04 at 12.56.07.png>)

## **Summary**

**What Worked:**

- Conversational flow for 6 profile fields is stable.
- Error handling for silent audio and the retry workflow is fully implemented.
- Sidebar configuration successfully manages agent and model states.
- The integration of the debug panel provides excellent visibility into the LLM's thought process (via the System Prompt) and the data structure (via JSON history).

**Issues Found:**

- **Runtime Log Disconnect:** System logs are not appearing in the dashboard debug tab.
- **Turn Indexing Mismatch:** The progress bar header text is one turn behind the actual debug tracker.

**Next Steps:**

- Update the DashboardLogHandler in dashboard.py to ensure it captures all agent events.
- Sync the current_turn variable to ensure the header and tracker labels match.
- Implement the Latency Metrics UI once the logging handler is fixed.

## **Notes**

**File Naming Convention:**

[2026-03-04-dashboard-edge-cases.md](2026-03-02-local-agent-baseline.md)

**UX Finding: Empty Audio Feedback (PASS)**

The implementation of PR \#13 (Empty audio validation) was confirmed. When the user remains silent, the system does not crash or send empty strings to the LLM. Instead, it prompts the user to try again, which is essential for accessibility.

**Technical Finding: JSON structure (PASS)**

The JSON export format follows the A3: Session data schema defined in the proposal, ensuring that conversation history can be exported for future analysis by the Enabled Talent team.

