
"""
src.app.core.engines.llm.openrouter_llm

OpenRouter LLM engine implementation.
Supports any model available on OpenRouter via a single endpoint, but requires a API key set in .env.
"""

import time
from core.engines.base import LLMEngine
from utils.logger import setup_logger
from config import LLM_MAX_TOKENS, LLM_TEMPERATURE, OPENROUTER_MODEL

logger = setup_logger(__name__, log_type="pipeline")


class OpenRouterLLMEngine(LLMEngine):
    """Generates responses using any model via the OpenRouter API."""

    def __init__(self, model: str = OPENROUTER_MODEL):
        from dotenv import load_dotenv
        from openai import OpenAI
        import os
        load_dotenv()
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self._model = model

    def generate(self, messages: list[dict]) -> str:
        """
        Generate a response from a list of chat messages using OpenRouter.

        Args:
            messages: OpenAI-style message dicts with role and content keys.

        Returns:
            The assistant's response text.

        Raises:
            RuntimeError: If the OpenRouter API call fails.
        """
        logger.info(f"Generating response with OpenRouter ({self._model})...")
        t = time.time()
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
            )
            ai_response = response.choices[0].message.content
            logger.info(f"Assistant: '{ai_response}' [{time.time() - t:.2f}s]")
            return ai_response
        except Exception as e:
            logger.error(f"OpenRouter API call failed: {e}")
            raise RuntimeError(f"Failed to generate response: {e}")
        
