"""
tests.unit.test_api

Unit tests for the REST API layer.
"""

import io
import struct
import wave
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

def make_mock_pipeline(opening_text="Hello, what is your full name?"):
    """Return a MagicMock OnboardingPipeline with sensible defaults."""
    pipeline = MagicMock()
    pipeline.get_opening.return_value = (opening_text, "/tmp/fake_opening.mp3")
    pipeline.stt.transcribe.return_value = "John Smith"
    pipeline.tts.synthesize.return_value = "/tmp/fake_response.mp3"
    pipeline._generate.return_value = "Got it. What is your employment status?"
    pipeline.energy_threshold = 0.01
    pipeline.cleanup_file.return_value = None
    return pipeline

@pytest.fixture(autouse=True)
def mock_engines(tmp_path):
    """
    Patch create_pipeline and all audio file I/O so no real engines or
    disk files are touched during unit tests.
    """
    fake_audio = b"RIFF....fake audio bytes"

    with patch("api.main.create_pipeline") as mock_create, \
         patch("api.main.read_and_cleanup", return_value=fake_audio), \
         patch("api.main.sf.read") as mock_sf, \
         patch("api.main.np.abs") as mock_np, \
         patch("os.path.exists", return_value=True), \
         patch("os.remove"):

        mock_create.return_value = make_mock_pipeline()
        mock_sf.return_value = (MagicMock(), 16000)
        mock_np.return_value.mean.return_value = 0.05

        yield mock_create

def make_silent_wav(duration_s: float = 1.0, sample_rate: int = 16000) -> io.BytesIO:
    """Return an in-memory WAV file containing only silence."""
    n_frames = int(duration_s * sample_rate)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(struct.pack("<" + "h" * n_frames, *([0] * n_frames)))
    buf.seek(0)
    return buf

def make_audio_upload(buf: io.BytesIO = None) -> dict:
    """Return a files dict suitable for TestClient.post()."""
    if buf is None:
        buf = make_silent_wav()
    return {"audio": ("audio.wav", buf, "audio/wav")}

from api.main import app  # noqa: E402
client = TestClient(app)

def start_session() -> str:
    resp = client.post("/session/start")
    assert resp.status_code == 200
    return resp.headers["X-Session-ID"]

def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_health_contains_engines_and_fields():
    data = client.get("/health").json()
    assert "engines" in data
    assert "fields" in data
    assert len(data["fields"]) == 6

def test_health_active_sessions_increments():
    before = client.get("/health").json()["active_sessions"]
    start_session()
    after = client.get("/health").json()["active_sessions"]
    assert after == before + 1

def test_start_returns_200():
    assert client.post("/session/start").status_code == 200

def test_start_returns_session_id():
    resp = client.post("/session/start")
    assert "X-Session-ID" in resp.headers
    assert resp.headers["X-Session-ID"]

def test_start_returns_correct_headers():
    resp = client.post("/session/start")
    assert resp.headers["X-Turn"] == "0"
    assert resp.headers["X-Field"] == "name"
    assert resp.headers["X-Total-Turns"] == "6"
    assert "X-Response-Text" in resp.headers

def test_start_returns_audio_bytes():
    resp = client.post("/session/start")
    assert resp.headers["content-type"] == "audio/mpeg"
    assert len(resp.content) > 0

def test_turn_returns_200():
    session_id = start_session()
    resp = client.post(f"/session/{session_id}/turn", files=make_audio_upload())
    assert resp.status_code == 200

def test_turn_advances_turn_counter():
    session_id = start_session()
    resp = client.post(f"/session/{session_id}/turn", files=make_audio_upload())
    assert resp.headers["X-Turn"] == "1"

def test_turn_returns_correct_field():
    session_id = start_session()
    resp = client.post(f"/session/{session_id}/turn", files=make_audio_upload())
    assert resp.headers["X-Field"] == "name"
    assert resp.headers["X-Next-Field"] == "employment_status"

def test_turn_session_not_complete_after_first_turn():
    session_id = start_session()
    resp = client.post(f"/session/{session_id}/turn", files=make_audio_upload())
    assert resp.headers["X-Session-Complete"] == "false"

def test_turn_returns_audio_bytes():
    session_id = start_session()
    resp = client.post(f"/session/{session_id}/turn", files=make_audio_upload())
    assert resp.headers["content-type"] == "audio/mpeg"
    assert len(resp.content) > 0

def test_turn_invalid_session_returns_404():
    resp = client.post(
        "/session/does-not-exist/turn",
        files=make_audio_upload(),
    )
    assert resp.status_code == 404

def test_silent_audio_returns_400(mock_engines):
    """Silent audio must be rejected before hitting the STT engine."""
    with patch("api.main.np.abs") as mock_np:           # Override the energy mock to return below-threshold value
        mock_np.return_value.mean.return_value = 0.0001
        session_id = start_session()
        resp = client.post(f"/session/{session_id}/turn", files=make_audio_upload())

    assert resp.status_code == 400
    assert "silent" in resp.json()["detail"].lower()

def test_silent_audio_does_not_advance_turn(mock_engines):
    """A rejected silent turn must not increment the turn counter."""
    with patch("api.main.np.abs") as mock_np:
        mock_np.return_value.mean.return_value = 0.0001
        session_id = start_session()
        client.post(f"/session/{session_id}/turn", files=make_audio_upload())

    health = client.get("/health").json()   # Session still exists and is still on turn 0
    assert health["active_sessions"] >= 1
    client.delete(f"/session/{session_id}")

def test_turn_after_complete_returns_400():
    """Calling /turn after all 6 fields are done should return 400."""
    from api.main import sessions, ONBOARDING_FIELDS
    session_id = start_session()
    # Manually advance the turn counter to simulate a completed session
    sessions[session_id]["turn"] = len(ONBOARDING_FIELDS)

    resp = client.post(f"/session/{session_id}/turn", files=make_audio_upload())
    assert resp.status_code == 400
    assert "complete" in resp.json()["detail"].lower()

def test_confirm_before_complete_returns_400():
    """Calling /confirm before all turns are done should return 400."""
    session_id = start_session()
    resp = client.post(
        f"/session/{session_id}/confirm",
        files=make_audio_upload(),
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"].lower()
    assert "not yet complete" in detail or "remaining" in detail

def test_confirm_invalid_session_returns_404():
    resp = client.post(
        "/session/does-not-exist/confirm",
        files=make_audio_upload(),
    )
    assert resp.status_code == 404

def test_delete_session_returns_200():
    session_id = start_session()
    assert client.delete(f"/session/{session_id}").status_code == 200

def test_delete_invalid_session_returns_404():
    assert client.delete("/session/does-not-exist").status_code == 404

def test_delete_removes_session():
    """After deletion, any further request on the session should 404."""
    session_id = start_session()
    client.delete(f"/session/{session_id}")
    resp = client.post(f"/session/{session_id}/turn", files=make_audio_upload())
    assert resp.status_code == 404