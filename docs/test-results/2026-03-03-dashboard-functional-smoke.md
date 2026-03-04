# Test Results: Dashboard Functional Smoke Testing (Local Agent)

**Date**: 2026-03-03  
**Tester**: Dhairya Patel  
**Branch**: test/dashboard-functional-smoke  
**Operating System**: macOS  
**Hardware**: MacBook Air M2, 8GB RAM  
**Models Tested**: gemma3:1b (Ollama local), Whisper (base/small/medium/large)

---

## Test Scope

This report focuses on validating the **primary dashboard workflow and configuration behaviour** for the onboarding prototype when using the LocalVoiceAgent implementation.

The goal of this smoke test is to confirm that the **core dashboard workflow functions correctly**, including:

- Dashboard loading and UI rendering
- Configuration control behaviour
- Session lifecycle management
- Turn execution flow
- Recording and transcription pipeline
- Application of runtime configuration parameters

The following areas are **intentionally out of scope** for this report and are covered in a separate debug-focused test report:

- Debug panel validation
- Runtime log analysis
- JSON conversation history validation
- Detailed error handling and retry behaviour

---

## 1. Dashboard initialization and UI validation

This test validates that the Streamlit onboarding dashboard loads correctly and displays all required UI elements before a session begins.

The purpose of this section is to confirm that the user interface is functional and that all major dashboard components render correctly.

Testing was performed by opening the dashboard locally in a browser and refreshing the page to ensure consistent UI rendering.

**Components validated:**

- Dashboard title and subtitle
- Instruction banner
- Sidebar configuration panel
- Agent selection controls
- Audio configuration controls
- Model configuration controls
- Onboarding field list
- Start session button

This section focuses only on **initial UI rendering and layout validation** before any agent interaction occurs.

| Test Case | Steps | Expected | Actual | Pass? |
|-----------|------|----------|--------|-------|
| Dashboard loads successfully | Open dashboard and refresh page | Dashboard loads without errors | Dashboard loaded successfully with all UI sections visible. Minor visual jitter observed in dropdown menus when scrolling, likely related to Streamlit rendering behaviour. | PASS |
| Title and description visible | Observe main header area | Title and subtitle displayed | Title "Voice Agent Onboarding Dashboard" displayed prominently in bold with caption "Onboarding prototype - browser interface" shown below in lighter faded text. Layout appears correct and readable. | PASS |
| Sidebar configuration visible | Inspect sidebar panel | Configuration controls visible | Sidebar rendered correctly with Configuration, Audio, Local Models, and Onboarding Fields sections visible. All controls accessible and functional. Keyboard navigation also works for slider and dropdown controls using arrow keys. | PASS |
| Start session button present | Inspect bottom of sidebar | Button visible and clickable | "▶ Start session" button visible at bottom of sidebar with primary styling and full-width layout. Button appears enabled and ready to start a session. | PASS |
| Onboarding fields displayed | Inspect field list | All onboarding fields visible | Six onboarding fields displayed in bullet list format with code-style formatting: name, employment_status, skills, experience, education, job_preferences. | PASS |
| Instruction banner displayed | No session active | Instruction banner prompts user to start session | Dashboard displays the instruction banner: “Configure agent in the sidebar and press ▶ Start session to begin.” when no session is active. Message is clearly visible and guides the user to start the onboarding workflow. | PASS |

**Key Findings:**

- Dashboard loads successfully without runtime errors.
- All expected UI sections render correctly including the header, sidebar configuration panel, and onboarding field list.
- Minor visual jitter observed in dropdown menus when scrolling the page. This appears to be a Streamlit UI rendering behaviour and does not affect functionality.
- Dashboard header renders correctly with bold title and lighter caption formatting.
- Sidebar configuration controls are fully accessible and support both mouse and keyboard interaction.
- Start session button is clearly visible with primary styling and appears ready for user interaction.
- Onboarding fields are displayed correctly in the sidebar and match the configured field list from `onboarding_config.py`.

---

## 2. Configuration controls validation

This section validates that all dashboard configuration controls behave correctly and allow the user to modify runtime parameters before starting a session.

The configuration options tested include:

- Agent selection (Local vs Cloud)
- Recording duration
- Sample rate
- Whisper model selection
- Ollama model input

These parameters influence how the voice agent operates during the onboarding session.

The test also verifies that configuration controls become **disabled during an active session**, as intended in the dashboard implementation.

| Test Case | Steps | Expected | Actual | Pass? |
|-----------|-------|----------|--------|-------|
| Agent selection toggle | Switch between Local and Cloud agents | Selected option updates correctly | Switching between Local and Cloud agent updates the sidebar correctly. Local model settings disappear when Cloud is selected and reappear when switching back to Local. | PASS |
| Recording duration slider | Adjust duration between 3–15 seconds | Slider updates value | Slider works correctly across the full range (3–15 seconds). Value updates smoothly while dragging and can also be adjusted using keyboard arrow keys. | PASS |
| Sample rate selection | Change sample rate options | Selected rate updates correctly | Dropdown displays all available options (16000, 22050, 44100). Selection updates correctly and supports keyboard navigation using arrow keys and Enter key. | PASS |
| Whisper model selection | Change model (base → large) | Model selection updates | Whisper model dropdown displays all four models (base, small, medium, large). Selection updates correctly and dropdown works with both mouse and keyboard navigation. | PASS |
| Ollama model input | Edit model field | Input field accepts value | Default value `gemma3:1b` displayed. Input field allows editing and accepts custom values without UI issues. | PASS |
| Controls disabled during session | Start session and inspect sidebar controls | Configuration controls disabled while session is active | After starting the session, sidebar configuration controls (agent selection, recording duration, sample rate, and model settings) became disabled and greyed out, preventing changes during the active session. | PASS |

**Key Findings:**

- Agent selection toggle functions correctly and dynamically updates the configuration panel.
- Local model settings are displayed only when the Local agent is selected and are hidden when the Cloud agent is selected.
- Recording duration slider operates correctly across its full range (3–15 seconds) and supports both mouse and keyboard interaction.
- Sample rate dropdown works correctly and supports both mouse selection and keyboard navigation.
- Whisper model dropdown functions correctly and allows switching between base, small, medium, and large models.
- Ollama model input field displays the default model and allows editing without UI issues.

---

## 3. Session lifecycle and turn execution

This section validates the **core onboarding workflow**, ensuring that a session can be started and the agent can conduct the onboarding conversation across multiple turns.

The following behaviours are validated:

- Session initialization
- Recording activation
- User speech transcription
- Agent response generation
- Turn progression
- Completion of onboarding questions
- Session reset behaviour

Testing was performed by running the onboarding session through multiple turns using the dashboard interface.

**Results:**

- Total onboarding fields tested: 6  
- Session runs executed: 1 (full onboarding workflow)  
- Successful completions: 1 

| Test Case | Steps | Expected | Actual | Pass? |
|-----------|-------|----------|--------|-------|
| Start session | Click "Start session" | Session initializes successfully | Session started successfully. Dashboard loaded conversation interface with progress bar, record button, and debug panel. Agent generated an onboarding greeting message and asked for the user's name. Initial response generated in approximately 3 seconds. | PASS |
| Recording trigger | Press record button and speak response | System records audio, transcribes speech, generates response, and proceeds to next onboarding question | Audio recording started successfully. Speech was transcribed and the agent generated the next onboarding question. Transcription captured the tester's name but slightly misspelled it due to pronunciation/accent variation. Agent response quality was appropriate and the turn advanced correctly. | PASS |
| Turn progression | Answer onboarding question using the Record button | Turn counter increments and next onboarding question appears | Turn counter successfully incremented and conversation history updated. Agent generated the next onboarding question and the debug tracker updated to show the next active field. | PASS |
| Agent response generation | Speak response during onboarding turn | Agent returns appropriate reply | After speech input was transcribed, the agent generated a relevant follow-up question based on the onboarding field being collected. Responses were context-aware and maintained conversation flow. | PASS |
| Session completion | Complete all onboarding questions using the Record workflow | System displays completion message and stops further onboarding turns | All onboarding fields were successfully collected and the dashboard displayed the message “Onboarding complete — all fields collected.” The progress bar reached 100% and no further turns were requested by the system. | PASS |
| Record visual feedback | Click Record and observe UI feedback during recording | Recording status should appear immediately and clearly indicate recording state | Recording started successfully and the debug panel faded, indicating that the system entered the recording state. The Record button became disabled and later displayed the message “Recording now for 5 sec… speak now.” However, the visual status update was slightly delayed during the first interaction. | PASS (Minor UX observation) |
| End session reset | Click "End session" after session start | Session resets to initial state | Clicking the End session button stopped the active session, cleared the conversation interface, and returned the dashboard to the initial configuration state with sidebar controls re-enabled. | PASS |

**Key Findings:**

- Session starts successfully and initializes the onboarding workflow.
- Dashboard transitions from configuration view to conversation interface without errors.
- Agent generates an opening onboarding message and prompts for the first field (`name`).
- Initial agent response was generated in approximately 3 seconds.
- Debug panel correctly displays active session parameters.
- Record workflow functions correctly including audio recording, transcription, response generation, and turn progression.
- Minor transcription spelling variation observed due to accent and pronunciation differences, but meaning was correctly understood by the system.
- Turn progression works correctly across multiple onboarding fields and the dashboard correctly updates progress indicators and debug trackers.
- The onboarding workflow successfully completed after collecting all required fields (6 turns).
- The dashboard correctly displayed the completion state and prevented additional interaction after the workflow finished.
- Minor delay observed in visual feedback when pressing the Record button. Recording begins immediately, but the UI status indicator may update slightly later during the first interaction.

---

## 4. Configuration parameter testing (local agent)

Additional testing was performed to verify that different audio and model configurations function correctly during active sessions.

These tests ensure that the dashboard correctly applies configuration changes to the local agent runtime.

Parameters tested include:

- Recording duration: 3s, 5s, 10s, 15s
- Sample rate: 16000 Hz, 22050 Hz, 44100 Hz
- Whisper models: base, small, medium, large

Each configuration run verified:

- Session start
- Audio recording
- Transcription
- Agent response generation
- System stability

| Parameter | Values Tested | Session Start | Recording Works | Pass? |
|----------|---------------|--------------|----------------|------|
| Recording duration | 3s / 5s / 10s / 15s | PASS | PASS | PASS |
| Sample rate | 16000 / 22050 / 44100 | PASS | PASS | PASS |
| Whisper models | base / small / medium / large | PASS | PASS | PASS |

### Recording duration behavior

The recording duration slider correctly changed the configured recording time during testing.  
However, the observed recording phase consistently lasted slightly longer than the selected value.

Examples observed during testing:

- 3s setting → ~5 seconds observed
- 5s setting → ~7 seconds observed
- 10s setting → ~12–13 seconds observed
- 15s setting → ~17–18 seconds observed

This suggests that the dashboard measures not only the microphone recording time but also includes small additional overhead such as audio initialization, buffering, and file handling.

Despite this small delay, the feature functioned correctly and recording stopped automatically after the expected approximate duration.

### Sample rate testing

All tested sample rates successfully initialized the audio pipeline and allowed normal onboarding interaction.

Tested sample rates:

- 16000 Hz
- 22050 Hz
- 44100 Hz

No stability issues or failures were observed.  
Transcription accuracy and agent responses behaved consistently across all tested values.

### Whisper model testing

All available Whisper models were tested using the local agent configuration:

- base
- small
- medium
- large

Each model successfully performed speech transcription and allowed the onboarding session to continue normally.

Expected behaviour differences were observed:

- **base model** responded fastest but occasionally produced minor transcription inaccuracies.
- **larger models** required slightly more processing time but generally produced more accurate transcription.

No system crashes or session failures were observed during model switching.

### Key Findings

- All tested configuration parameters were applied correctly by the dashboard.
- Recording duration works reliably but includes a small timing overhead (~2 seconds).
- Sample rate configuration does not negatively impact system stability.
- All Whisper models function correctly with the onboarding workflow.
- Larger Whisper models may improve transcription accuracy at the cost of slightly longer processing time.

Overall, the dashboard remained stable and functional across all tested configurations.

## Summary

Overall, the dashboard functional smoke test was successful. The core onboarding workflow, configuration controls, and voice interaction pipeline operated as expected when using the LocalVoiceAgent implementation. No critical failures or system crashes were observed during testing.

- Minor UI feedback delay when starting recording. The system correctly begins recording, but the status indicator may not immediately reflect the recording state on the first interaction.

Testing was performed interactively through the Streamlit dashboard interface using the system microphone and manual voice input.

**What Worked:**

- Dashboard UI loads reliably and displays all required interface elements.
- Configuration controls (agent selection, audio settings, and model selection) function correctly.
- Sidebar controls correctly become disabled during an active session to prevent configuration changes.
- The onboarding workflow successfully collects all required fields through a multi-turn conversation.
- Audio recording, transcription, and response generation pipeline works consistently.
- Conversation history, progress indicators, and onboarding prompts update correctly after each turn.
- Parameter changes (recording duration, sample rate, and Whisper model) are applied correctly and do not impact system stability.

**Issues Found:**

- Minor UI feedback delay when pressing the Record button. The system begins recording immediately, but the status indicator may not update instantly during the first interaction.
- Recording duration shows a consistent ~2 second overhead compared to the selected value (e.g., 10s selection observed as ~12–13s). Functionality still works but timing may appear longer than expected.
- Minor transcription variations were observed when using the Whisper base model, likely due to accent differences or pronunciation.

**Trade-offs:**

- Smaller Whisper models (such as base) provide faster responses but may reduce transcription accuracy slightly.
- Larger Whisper models increase transcription accuracy but introduce longer processing times.
- Local model execution avoids cloud dependency but requires sufficient local compute resources.

**Next Steps:**

- Perform dedicated debug panel validation testing.
- Validate runtime logs and conversation history JSON output.
- Conduct detailed error handling tests including silent audio and retry behavior.
- Perform comparative testing between Local and Cloud agent implementations.
- Evaluate performance and latency differences across Whisper model sizes.

---

## Notes


### UX Finding: Record button lacks immediate visual feedback (minor)

During the onboarding session, pressing the **Record** button correctly started the recording pipeline (UI elements faded/disabled and processing continued), however the status text near the Record area did not always update immediately to show **"RECORDING: speak now"**. In some cases, the tester perceived that nothing was happening until pressing Record a second time.

**Impact:** Minor usability issue — may confuse users and cause repeated clicks.  
**Observed behavior:** Debug panel fades/locks (indicating state change), but Record area does not clearly show recording state on first click.  
**Expected behavior:** Status text should update instantly on first click to confirm recording started.  
**Severity:** Low (UX), functionality still works.
