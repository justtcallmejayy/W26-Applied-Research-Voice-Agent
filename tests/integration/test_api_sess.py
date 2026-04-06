"""
tests.integration.test_api_sess

Integration tests for the REST API wrapper around the OnboardingPipeline 
using pre-recorded audio files.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.mark.parametrize("run_number", range(10))
def test_full_api_session(run_number):

    # Start the session
    response = client.post("/session/start")
    assert response.status_code == 200
    session_id = response.headers["X-Session-ID"]
    assert session_id

    # Run all 6 turns with pre-recorded audio fixtures
    audio_files = [
        "tests/audio/name.wav",
        "tests/audio/employment.wav",
        "tests/audio/skills.wav",
        "tests/audio/education.wav",
        "tests/audio/experience.wav",
        "tests/audio/job_prefs.wav",
    ]

    fields = ["name", "employment_status", "skills", "education", "experience", "job_preferences"]

    for i, (audio_path, expected_field) in enumerate(zip(audio_files, fields)):
        with open(audio_path, "rb") as f:
            response = client.post(
                f"/session/{session_id}/turn",
                files={"audio": ("audio.wav", f, "audio/wav")},
            )
        assert response.status_code == 200
        assert response.headers["X-Field"] == expected_field
        assert response.headers["X-Turn"] == str(i + 1)

    assert response.headers["X-Session-Complete"] == "true"
    assert response.status_code == 200
    assert response.headers["X-Session-Complete"] == "true"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "engines" in data
    assert "fields" in data
    assert len(data["fields"]) == 6

def test_invalid_session_turn():
    """Turn request with a non-existent session ID should return 404."""
    with open("tests/audio/name.wav", "rb") as f:
        response = client.post(
            "/session/invalid-session-id/turn",
            files={"audio": ("audio.wav", f, "audio/wav")},
        )
    assert response.status_code == 404

def test_invalid_session_delete():
    """Deleting a non-existent session should return 404."""
    response = client.delete("/session/invalid-session-id")
    assert response.status_code == 404

def test_delete_session():
    """Start a session then delete it early — should return 200."""
    response = client.post("/session/start")
    assert response.status_code == 200
    session_id = response.headers["X-Session-ID"]

    response = client.delete(f"/session/{session_id}")
    assert response.status_code == 200

    # Confirm session is gone
    with open("tests/audio/name.wav", "rb") as f:
        response = client.post(
            f"/session/{session_id}/turn",
            files={"audio": ("audio.wav", f, "audio/wav")},
        )
    assert response.status_code == 404
