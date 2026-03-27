"""
src.app.core.engines.llm.groq_llm

Groq LLM engine implementation.
Implements LLMEngine using the Groq API with an OpenAI-compatible client.
Requires GROQ_API_KEY to be set in the environment.
"""

import os
import time
from utils.logger import setup_logger
from core.engines.base import LLMEngine
from config import LLM_MAX_TOKENS, LLM_TEMPERATURE, LLM_PRESENCE_PENALTY, LLM_FREQUENCY_PENALTY, GROQ_MODEL

logger = setup_logger(__name__, log_type="pipeline")


class GroqLLMEngine(LLMEngine):
    """Generates responses using a Groq-hosted model via OpenAI-compatible API."""

    def __init__(self, model: str = GROQ_MODEL):
        """
        Initialise the Groq client and model selection.

        Args:
            model: Groq model ID to use for generation.

        Raises:
            RuntimeError: If GROQ_API_KEY is not available.
        """
        from dotenv import load_dotenv
        from openai import OpenAI

        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY not set in environment. "
                "Set it in src/app/.env or as an environment variable."
            )

        self._client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        self._model = model

    def generate(self, messages: list[dict]) -> str:
        """
        Generate a response from chat messages using Groq.

        Args:
            messages: OpenAI-style message dicts with role and content keys.

        Returns:
            The assistant response text.

        Raises:
            RuntimeError: If the Groq API call fails.
        """
        logger.info(f"Generating response with Groq ({self._model})...")
        t = time.time()
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
                presence_penalty=LLM_PRESENCE_PENALTY,
                frequency_penalty=LLM_FREQUENCY_PENALTY,
            )
            ai_response = response.choices[0].message.content
            logger.info(f"Assistant: '{ai_response}' [{time.time() - t:.2f}s]")
            return ai_response
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise RuntimeError(f"Failed to generate response from Groq: {e}")
