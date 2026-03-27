"""
tests.pipeline_test

Unit tests related to the OnboardingPipeline.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from src.app.core.pipeline import OnboardingPipeline
from src.app.config import MAX_HISTORY_LENGTH

@pytest.fixture
def pipeline():
    """ Creates a pipeline with mocked engines for testing """
    stt = MagicMock()
    llm = MagicMock()
    tts = MagicMock()
    tts.synthesize.return_value = "/tmp/fake_audio.mp3"

    return OnboardingPipeline(
        stt=stt,
        llm=llm,
        tts=tts,
        system_prompt="Test Prompt",
        onboarding_fields=["name", "employment_status"],
        recording_duration=5,
        sample_rate=16000,
        energy_threshold=0.01
    )

def test_empty_llm_response_does_not_crash(pipeline):
    """ Empty LLM response should be caught before reaching TTS """
    pipeline.llm.generate.return_value = ""
    result = pipeline._generate("Hello")
    assert result == ""
    pipeline.tts.synthesize.assert_not_called()

def test_none_llm_response_does_not_crash(pipeline):
    """ None LLM response should be caught before reaching TTS """
    pipeline.llm.generate.return_value = None
    result = pipeline._generate("Hello")
    assert result == ""
    pipeline.tts.synthesize.assert_not_called()

def test_normal_response_flows_through(pipeline):
    """ Valid LLM response should reach TTS normally """
    pipeline.llm.generate.return_value = "What is your name?"
    result = pipeline._generate("Begin the onboarding conversation.")
    assert result == "What is your name?"

def test_history_trim(pipeline):
    """ Conversation history should be trimmed to MAX_HISTORY_LENGTH """
    pipeline.llm.generate.return_value = "response"
    for i in range(10):
        pipeline._generate(f"message {i}")
    assert len(pipeline.conversation_history) <= MAX_HISTORY_LENGTH

def test_whitespace_llm_response_does_not_crash(pipeline):
    """ Whitespace-only LLM response should be treated as empty """
    pipeline.llm.generate.return_value = "   "
    result = pipeline._generate("Hello")
    assert result == ""
    pipeline.tts.synthesize.assert_not_called()

def test_history_trim_uses_config_value(pipeline):
    """ History trim should use MAX_HISTORY_LENGTH from config, not hardcoded 8 """
    pipeline.llm.generate.return_value = "response"
    for i in range(MAX_HISTORY_LENGTH + 5):
        pipeline._generate(f"message {i}")
    assert len(pipeline.conversation_history) <= MAX_HISTORY_LENGTH

def test_per_turn_field_passed_to_llm(pipeline):
    """Current field should be passed to LLM on each turn """
    pipeline.llm.generate.return_value = "What is your name?"
    pipeline._generate("[Collecting: name]\nMy name is Brendan")
    call_args = pipeline.llm.generate.call_args[0][0]
    assert any("name" in str(msg) for msg in call_args)

def test_conversation_history_appended_correctly(pipeline):
    """User and assistant messages should both be appended to history """
    pipeline.llm.generate.return_value = "Nice to meet you!"
    pipeline._generate("My name is Brendan")
    assert len(pipeline.conversation_history) == 2
    assert pipeline.conversation_history[0]["role"] == "user"
    assert pipeline.conversation_history[1]["role"] == "assistant"

def test_empty_response_removes_user_message(pipeline):
    """Empty LLM response should remove the user message from history """
    pipeline.llm.generate.return_value = ""
    initial_length = len(pipeline.conversation_history)
    pipeline._generate("Hello")
    assert len(pipeline.conversation_history) == initial_length

def test_llm_generate_called_with_system_prompt(pipeline):
    """System prompt should always be prepended to messages """
    pipeline.llm.generate.return_value = "response"
    pipeline._generate("Hello")
    call_args = pipeline.llm.generate.call_args[0][0]
    assert call_args[0]["role"] == "system"
    assert call_args[0]["content"] == "Test Prompt"

def test_llm_generate_called_with_history(pipeline):
    """LLM should receive full conversation history on each call """
    pipeline.llm.generate.return_value = "response"
    pipeline._generate("first message")
    pipeline._generate("second message")
    call_args = pipeline.llm.generate.call_args[0][0]
    assert len(call_args) == 4

def test_record_audio_returns_numpy_array(pipeline):
    """record_audio should return a numpy array """
    import numpy as np
    with patch("sounddevice.rec") as mock_rec, \
        patch("sounddevice.wait"):
        mock_rec.return_value = np.zeros((80000, 1), dtype="float32")
        result = pipeline.record_audio()
        assert isinstance(result, np.ndarray)

def test_cleanup_file_removes_file(pipeline, tmp_path):
    """cleanup_file should delete the file from disk """
    test_file = tmp_path / "test.wav"
    test_file.write_text("fake audio")
    pipeline.cleanup_file(str(test_file))
    assert not test_file.exists()

def test_cleanup_file_handles_missing_file(pipeline):
    """cleanup_file should not raise if file does not exist """
    pipeline.cleanup_file("/tmp/nonexistent_file.wav")

def test_save_audio_creates_wav_file(pipeline):
    """save_audio should write a valid WAV file to disk """
    import numpy as np
    audio_data = np.zeros((80000, 1), dtype="float32")
    path = pipeline.save_audio(audio_data)
    assert os.path.exists(path)
    os.remove(path)
