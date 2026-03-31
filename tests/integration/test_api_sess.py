"""
tests.integration.test_api_sess

Integration tests for the REST API wrapper around the OnboardingPipeline 
using pre-recorded audio files.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_full_api_session():
    # 1. Start session
    response = client.post("/session/start")
    assert response.status_code == 200
    session_id = response.headers["X-Session-ID"]
    assert session_id

    # 2. Run all 6 turns with pre-recorded audio fixtures
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

    # 3. Confirm
    with open("tests/audio/confirm.wav", "rb") as f:
        response = client.post(
            f"/session/{session_id}/confirm",
            files={"audio": ("audio.wav", f, "audio/wav")},
        )
    assert response.status_code == 200
    assert response.headers["X-Session-Complete"] == "true"

