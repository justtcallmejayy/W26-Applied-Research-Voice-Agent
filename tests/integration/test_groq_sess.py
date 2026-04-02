"""
Integration smoke test for Groq LLM engine.

Runs only when GROQ_API_KEY is available.
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from src.app.core.engines.llm.groq_llm import GroqLLMEngine


def test_groq_generate_smoke():
    """Validate Groq engine can return a non-empty response for a simple prompt."""
    env_path = Path("src/app/.env")
    if env_path.exists():
        load_dotenv(env_path)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        pytest.skip("GROQ_API_KEY not configured; skipping Groq integration smoke test")

    engine = GroqLLMEngine()
    reply = engine.generate([
        {"role": "user", "content": "Reply with exactly: hello"}
    ])

    assert isinstance(reply, str)
    assert reply.strip() != ""
