"""
api.py

This module defines a simple, synchronous API skeleton for the voice
onboarding prototype.  The goal of this module is to provide clear
function signatures that map to the REST endpoints documented in
``docs/api-spec.md``.  These functions do not perform any I/O (no
HTTP requests or responses) and can be called directly from a web
framework such as FastAPI or Flask.  Keeping the implementation in a
separate module makes it easy to expose the same business logic via
different interfaces (e.g. command line, Streamlit, API).

Each function accepts and returns plain Python types (dicts, strings,
etc.).  You should later wire these into your chosen web framework,
convert the return values to JSON and handle any necessary
serialization/deserialization.

Note: This skeleton assumes the existence of a ``SessionManager``
class and ``log_event`` function, as provided in ``session_manager.py``
and ``logging_manager.py``.  See those modules for details.
"""

from typing import Any, Dict, Optional

from logging_manager import log_event
from session_manager import SessionManager

# Global session manager instance.  In a real web application you might
# prefer to inject this or manage it via dependency injection.
manager = SessionManager()


def start_session() -> Dict[str, str]:
    """Create a new session and return its unique identifier.

    This corresponds to the ``POST /session/start`` endpoint in the API
    specification.  The function generates a session ID, creates a
    new session state object in the ``SessionManager``, logs the
    creation event, and returns the ID to the caller.

    Returns
    -------
    dict
        A dictionary containing a ``session_id`` key.  Example:

        ``{"session_id": "550e8400-e29b-41d4-a716-446655440000"}``
    """
    session_state = manager.create_session()
    session_id = session_state.session_id
    log_event(session_id, "session_start", {"message": "Session created via API"})
    return {"session_id": session_id}


def process_turn(session_id: str, user_input: str) -> Dict[str, Any]:
    """Process a user input and return the assistant's response and state.

    This function implements the ``POST /session/turn`` endpoint.  It
    accepts the session identifier and a user input string (which may
    come from speech‑to‑text or a text field), stores the value for the
    current field, asks for confirmation on the value, and returns the
    assistant's message along with the updated state.  The exact
    behavior of the assistant (e.g. what it says) is left to the
    frontend or the calling code; here we simply log the event and
    return a placeholder response.

    Parameters
    ----------
    session_id : str
        The unique identifier of the session.
    user_input : str
        The user's input for the current onboarding field.

    Returns
    -------
    dict
        A dictionary containing the assistant's response and the
        current session state.  Example:

        ``{
            "assistant_response": "You entered Jay. Is that correct?",
            "state": {"current_step": "name", "fields": {"name": "Jay"}, ...}
        }``
    """
    state = manager.get_session(session_id)
    if state is None:
        return {"error": "Invalid session ID"}

    # Update field value
    current_field = state.current_step
    manager.update_field(session_id, current_field, user_input.strip())
    log_event(session_id, "field_captured", {"field": current_field, "value": user_input.strip()})

    # Generate assistant message asking for confirmation
    response_text = f"You entered {state.fields[current_field]}. Is that correct?"
    return {
        "assistant_response": response_text,
        "state": state.as_dict(),
    }


def get_state(session_id: str) -> Dict[str, Any]:
    """Retrieve the current state of a session.

    Implements ``GET /session/{id}/state``.  Returns the current step,
    captured fields, confirmation flags, and any other metadata needed
    by the frontend or integration layer.

    Parameters
    ----------
    session_id : str
        The unique identifier of the session.

    Returns
    -------
    dict
        A dictionary describing the session state.  Example:

        ``{
            "current_step": "name",
            "fields": {"name": "Jay"},
            "confirmed": {"name": false},
            "turn_count": 1,
            "is_complete": false
        }``
    """
    state = manager.get_session(session_id)
    if state is None:
        return {"error": "Invalid session ID"}
    return state.as_dict()


def confirm_field(session_id: str, field: str, confirm: bool) -> Dict[str, Any]:
    """Confirm or correct the captured value for a field.

    Corresponds to ``POST /session/{id}/confirm``.  If ``confirm`` is
    ``True``, the captured value is marked as confirmed and the session
    advances to the next field.  If ``confirm`` is ``False``, the
    captured value is cleared and the user should be reprompted.

    Parameters
    ----------
    session_id : str
        The unique identifier of the session.
    field : str
        The name of the field being confirmed.
    confirm : bool
        Whether the user has confirmed (True) or rejected (False) the value.

    Returns
    -------
    dict
        The updated session state.  If the session is complete, the
        ``is_complete`` flag will be ``True``.
    """
    state = manager.get_session(session_id)
    if state is None:
        return {"error": "Invalid session ID"}

    manager.confirm_field(session_id, field, confirm)
    event_type = "field_confirmed" if confirm else "field_corrected"
    log_data = {"field": field}
    if confirm:
        log_data["value"] = state.fields.get(field)
    log_event(session_id, event_type, log_data)

    # If the session becomes complete after confirmation, log the event
    if state.is_complete():
        log_event(session_id, "session_complete", {"fields": state.fields.copy()})

    return state.as_dict()


def get_logs(session_id: str, limit: int = 10) -> Dict[str, Any]:
    """Return recent log entries for a session.

    Implements ``GET /session/{id}/logs``.  Reads the JSONL log file
    created by ``logging_manager`` and returns the most recent ``limit``
    events in reverse chronological order (most recent first).

    Parameters
    ----------
    session_id : str
        The unique identifier of the session.
    limit : int, optional
        The number of recent events to return.  Defaults to 10.

    Returns
    -------
    dict
        A dictionary with a single key ``events`` mapping to a list of
        event objects.  If the log file does not exist, returns an
        empty list.
    """
    import os
    import json
    from logging_manager import SESSIONS_DIR

    log_file = os.path.join(SESSIONS_DIR, f"session_{session_id}.jsonl")
    if not os.path.exists(log_file):
        return {"events": []}

    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Return the last `limit` events, most recent first
    recent_events = [json.loads(l) for l in lines][-limit:][::-1]
    return {"events": recent_events}