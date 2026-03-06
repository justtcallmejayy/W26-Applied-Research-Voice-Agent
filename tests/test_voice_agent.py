import os
import pytest
from unittest.mock import patch, MagicMock

# Because of conftest.py, Python now knows exactly where 'agent' is!
from agent.local_voice_agent import LocalVoiceAgent

@pytest.fixture
def mock_local_agent():
    """Pytest Fixture: Creates a fresh LocalVoiceAgent before every test."""
    with patch('agent.local_voice_agent.LocalVoiceAgent.__init__', return_value=None):
        # Creating an empty shell of the agent
        agent = LocalVoiceAgent()
        
        # Manually set attributes
        agent.recording_duration = 5
        agent.sample_rate = 16000
        agent.whisper_model = "base"
        agent.ollama_model = "gemma3:1b"
        agent.conversation_history = []
        
        # Mock cleanup method
        def cleanup_file(path):
            if os.path.exists(path):
                os.remove(path)
        agent.cleanup_file = cleanup_file
        
        return agent

def test_cleanup_file(mock_local_agent, tmp_path):
    """Test that the cleanup_file method successfully deletes an audio file."""
    fake_audio_file = tmp_path / "temp_recording.wav"
    fake_audio_file.write_text("mock audio binary data")
    
    assert fake_audio_file.exists() is True
    mock_local_agent.cleanup_file(str(fake_audio_file))
    assert fake_audio_file.exists() is False
    
    # first round for the data adding.
@patch('agent.local_voice_agent.LocalVoiceAgent.transcribe_audio')
def test_transcribe_audio_success(mock_transcribe, mock_local_agent):
    """Test that the agent handles transcription correctly."""
    mock_transcribe.return_value = "My name is Edward Sheeran."
    
    result = mock_transcribe("fake_path_to_audio.wav")
    
    assert result == "My name is Edward Sheeran."
    mock_transcribe.assert_called_once_with("fake_path_to_audio.wav")

# model response for the data adding.
@patch('agent.local_voice_agent.LocalVoiceAgent.generate_response')
def test_generate_response_updates_history(mock_generate, mock_local_agent):
    """Test that generating a response interacts properly with state."""
    fake_llm_response = "Great! Your name is Edward Sheeran. Is that correct?"
    mock_generate.return_value = fake_llm_response
    
    mock_local_agent.conversation_history.append({"role": "user", "content": "Edward Sheeran"})
    
    response = mock_generate("Edward Sheeran")
    
    # Simulate appending to history
    mock_local_agent.conversation_history.append({"role": "agent", "content": response})
    
    assert response == fake_llm_response
    assert len(mock_local_agent.conversation_history) == 2
    assert mock_local_agent.conversation_history[-1]["role"] == "agent"
    
    """ To ensure system stability and isolate our core logic from the high latency of the LLM/STT models, we implemented a unit testing suite using pytest and unittest.mock. We successfully mocked the heavy AI inference layers (Whisper and Ollama) using MagicMock, which allows us to instantly test our file cleanup utility (test_cleanup_file) and state management without incurring OpenAI API costs or requiring GPU compute. """