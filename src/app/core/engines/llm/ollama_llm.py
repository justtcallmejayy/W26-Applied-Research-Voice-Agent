

"""
src.app.core.engines.llm.ollama_llm

Ollama local LLM engine implementation.
Implements LLMEngine using a locally running Ollama instance.
Requires Ollama to be running at the configured base_url before use.
"""

import time
import requests
from core.engines.base import LLMEngine
from utils.logger import setup_logger

logger = setup_logger(__name__, log_type="engine-llm")

class OllamaLLMEngine(LLMEngine):
    """Generates a response using a local Ollama model via the Ollama REST API."""


    def __init__(self, model: str = "gemma3:1b", base_url: str = "http://localhost:11434"):
        """
        Initialise the Ollama engine and verify the model is available.

        Args:
            model: Ollama model tag to use for generation. Defaults to gemma3:1b.
            base_url: Base URL of the running Ollama instance.
        
        Raises:
            RuntimeError: If Ollama is unreachable or no models are installed.
        """
        self._model = model
        self._url = f"{base_url}/api/chat"
        self._check_ollama(base_url)

    def _check_ollama(self, base_url: str):
        """
        Verify Ollama is running and the configured model is available.
        Falls back to the first available model if the requested one is not found.

        Args:
            base_url: Base URL of the Ollama instance to check.

        Raises:
            RuntimeError: If Ollama is unreachable or no models are installed.
        """
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = [m["name"] for m in response.json().get("models", [])]
            if self._model not in models:
                logger.warning(f"Model {self._model} not found. Available: {models}")
                if models:
                    self._model = models[0]
                    logger.info(f"Falling back to {self._model}")
                else:
                    raise RuntimeError("No Ollama models found. Run: ollama pull gemma3:1b")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Cannot connect to Ollama: {e}\n"
                "Make sure Ollama is running: ollama serve"
            )

    def generate(self, messages: list[dict]) -> str:
        """
        Generate a response from a list of chat messages using the local Ollama model.

        Args:
            messages: OpenAI-style message dicts with role and content keys.

        Returns:
            The assistant's response text.

        Raises:
            RuntimeError: If the Ollama server does not respond.
        """
        logger.info(f"Generating response with local {self._model}...")
        t = time.time()
        try:
            response = requests.post(
                self._url,
                json={"model": self._model, "messages": messages, "stream": False},
                timeout=30,
            )
            response.raise_for_status()
            ai_response = response.json()["message"]["content"]
            logger.info(f"Assistant: '{ai_response}' [{time.time() - t:.2f}s]")
            return ai_response
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama error: {e}")
            raise RuntimeError("Ollama not responding. Is it running?")

