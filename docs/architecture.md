## System Architecture

### Basic architecture (end-to-end)

![Basic architecture](docs/diagrams/basic_architecture_diagram.drawio.png)

### Detailed architecture (internal components)

![Detailed architecture](docs/diagrams/detailed_architecture_diagram_v1.png)

# System Architecture Notes

## Figure A — Basic Architecture (End-to-End)

This diagram shows the end-to-end voice onboarding loop:

1. The user interacts through the dashboard (voice input + output).
2. The backend orchestrates conversation flow and session state.
3. External AI services perform STT, reasoning (LLM), and TTS.
4. Logging/monitoring captures events and errors for evaluation.

## Figure B — Detailed Architecture (Internal Components)

This diagram expands the internal pipeline:

- Presentation layer: dashboard + accessibility trigger (keyboard shortcut / UI control).
- Input layer: audio capture + STT (speech-to-text) + transcript normalization.
- Validation layer: required-field validation, reprompt logic, and correction handling.
- Conversation controller: manages state machine for onboarding steps.
- Session context manager: stores captured fields (name, interests, skills) and conversation memory.
- Prompt safeguard: controls prompt format and prevents unsafe/unbounded responses.
- Output layer: LLM generates response text + TTS generates speech output.
- Logging manager: writes logs/events/metrics for weekly reporting and usability evaluation.
