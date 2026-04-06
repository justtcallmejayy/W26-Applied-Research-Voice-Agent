"""
Unit tests for Groq LLM engine.
"""

from unittest.mock import patch
from types import SimpleNamespacefrom unittest.mock import patchfrom types import SimpleNamespacefrom unittest.mock import patch

import pytest

from src.app.config import (
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_PRESENCE_PENALTY,
    LLM_FREQUENCY_PENALTY,
))))
from src.app.core.engines.llm.groq_llm import GroqLLMEngine


@pytest.fixture
def fake_openai_client():
    """Create a minimal fake OpenAI-compatible client object."""
    return SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=lambda **_: None)
        )
    )


def test_init_raises_when_groq_api_key_missing():
    """Engine should fail fast when GROQ_API_KEY is not configured."""
    with patch("dotenv.load_dotenv", return_value=False):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="GROQ_API_KEY not set"):
                GroqLLMEngine()


def test_init_configures_openai_client_for_groq_base_url(fake_openai_client):
    """Engine should initialise OpenAI client with Groq base URL and API key."""
    with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}, clear=True):
        with patch("openai.OpenAI", return_value=fake_openai_client) as mock_openai:
            engine = GroqLLMEngine(model="llama-3.1-8b-instant")

    mock_openai.assert_called_once_with(
        api_key="test-key",
        base_url="https://api.groq.com/openai/v1",
    )
    assert engine._model == "llama-3.1-8b-instant"


def test_generate_calls_client_with_expected_parameters(fake_openai_client):
    """Engine should pass config-driven generation parameters to Groq client."""
    mock_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Hello from Groq"))]
    )

    with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}, clear=True):
        with patch("openai.OpenAI", return_value=fake_openai_client):
            engine = GroqLLMEngine(model="llama-3.1-8b-instant")

    with patch.object(engine._client.chat.completions, "create", return_value=mock_response) as mock_create:
        messages = [{"role": "user", "content": "Hi"}]
        reply = engine.generate(messages)

    assert reply == "Hello from Groq"
    mock_create.assert_called_once_with(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=LLM_MAX_TOKENS,
        temperature=LLM_TEMPERATURE,
        presence_penalty=LLM_PRESENCE_PENALTY,
        frequency_penalty=LLM_FREQUENCY_PENALTY,
    )


def test_generate_wraps_client_exceptions(fake_openai_client):
    """Engine should wrap upstream client failures into RuntimeError."""
    with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}, clear=True):
        with patch("openai.OpenAI", return_value=fake_openai_client):
            engine = GroqLLMEngine()

    with patch.object(engine._client.chat.completions, "create", side_effect=Exception("upstream failure")):
        with pytest.raises(RuntimeError, match="Failed to generate response from Groq"):
            engine.generate([{"role": "user", "content": "Hi"}])
