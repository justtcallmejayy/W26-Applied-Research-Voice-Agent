
"""
src.app.core.engines.llm.openai_llm

OpenAI GPT-4 LLM engine implementation.
Implements LLMEngine using the OpenAI chat completions API.
Requires OPENAI_API_KEY to be set in .env.
"""

import time
from config import LLM_MAX_TOKENS, LLM_TEMPERATURE, LLM_PRESENCE_PENALTY, LLM_FREQUENCY_PENALTY
from core.engines.base import LLMEngine
from utils.logger import setup_logger

logger = setup_logger(__name__, log_type="pipeline")

class OpenAILLMEngine(LLMEngine):
    """Generates responses using GPT-4 via OpenAI. """

    def __init__(self, model: str = "gpt-4"):
        """
        Initialise the OpenAI client and load key

        Args:
            model: The OpenAI model to use for text generation. Defaults to gpt-4.
        """
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        self._client = OpenAI()
        self._model = model

    def generate(self, messages: list[dict]) -> str:
        """
        Generate a response from a list of chat messages using GPT-4.

        Args:
            messages: OpenAI-style message dicts with role and content keys.

        Returns:
            The assistant's response text.

        Raises:
            RuntimeError: If the OpenAI API call fails.
        """
        logger.info(f"Generating response with {self._model}...")
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
            logger.error(f"OpenAI API call failed: {e}")
            raise RuntimeError(f"Failed to generate response: {e}")



