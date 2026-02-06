# Prototype API Specification

This document outlines the proposed REST API endpoints for the voice onboarding assistant. These endpoints will allow a front‑end (i.e. Streamlit dashboard) or external system to interact with the backend in a decoupled manner. Implementing this API is optional right.

### API Endpoints

| Method | Endpoint | Request Body | Response | Description |
| :--- | :--- | :--- | :--- | :--- |
| **POST** | `/session/start` | `{}` | `{ "session_id": "uuid" }` | Create a new session and return its unique identifier. |
| **POST** | `/session/turn` | `{ "session_id": "uuid", "user_input": "string" }` | `{ "assistant_response": "string", "state": { ... } }` | Process a user input (text or STT transcription). Returns the assistant’s next message and updated state. |
| **GET** | `/session/{id}/state` | *(none)* | `{ "current_step": "field", "fields": { ... }, "confirmed": { ... }, "turn_count": integer }` | Retrieve the current state of a session, including which field is being asked and captured values. |
| **POST** | `/session/{id}/confirm` | `{ "field": "string", "confirm": true/false }` | `{ "state": { ... } }` | Explicitly confirm or reject a specific field value. |
| **GET** | `/session/{id}/logs` | `?limit=int` (optional) | `{ "events": [ { "timestamp": "...", "event_type": "...", ... } ] }` | Return the most recent `limit` log entries for debugging and evaluation (default 10). |

---

*This specification is intentionally simple. In a production system, we could add authentication, error handling, pagination for logs, and additional fields. For the purposes of an AR-1 prototype, but the above endpoints are sufficient to demonstrate integration and to support future UI developments.*