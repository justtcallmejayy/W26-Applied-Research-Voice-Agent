
"""
src.app.core.engines.tts.openai_tts

OpenAI TTS-1 engine implementation.
Implements TTSEngine using the OpenAI audio speech API.
Requires the OPENAI_API_KEY in .env.
"""

import time
import tempfile
from core.engines.base import TTSEngine
from utils.logger import setup_logger

logger = setup_logger(__name__, log_type="pipeline")


class OpenAITTSEngine(TTSEngine):
    """Synthesises speech via the OpenAI TTS-1 API."""

    def __init__(self, model: str = "tts-1", voice: str = "alloy"):
        """
        Initialise the OpenAI client and load the API key from .env.

        Args:
            model: The OpenAI TTS model to use. Defaults to tts-1.
            voice: The voice to use for synthesis. Defaults to alloy.
        """
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        self._client = OpenAI()
        self._model = model
        self._voice = voice

    def synthesize(self, text: str) -> str:
        """
        Convert text to speech and save to a temporary MP3 file.

        Args:
            text: The text to synthesise into speech.

        Returns:
            Absolute path to the generated MP3 file.
            Caller is responsible for deleting the file after playback.

        Raises:
            RuntimeError: If the TTS API call fails.
        """
        logger.info("Converting response to speech with OpenAI TTS...")
        t = time.time()
        try:
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            filepath = temp.name
            temp.close()
            response = self._client.audio.speech.create(
                model=self._model,
                voice=self._voice,
                input=text,
            )
            with open(filepath, "wb") as f:
                    f.write(response.content)
            logger.info(f"TTS complete! [{time.time() - t:.2f}s]")
            return filepath
        except Exception as e:
            logger.error(f"OpenAI TTS failed: {e}")
            raise RuntimeError(f"Failed to convert text to speech: {e}")
