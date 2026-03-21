
"""
src.app.core.engines.stt.whisper_api

OpenAI Whisper-1 STT engine implementation.
Implements STTEngine using the OpenAI audio transcriptions API.
Requires OPENAI_API_KEY in .env.
"""

import time
from core.engines.base import STTEngine
from utils.logger import setup_logger

logger = setup_logger(__name__, log_type="pipeline")


class WhisperAPIEngine(STTEngine):
    """Transcribes audio via the OpenAI Whisper-1 API."""

    def __init__(self):
        """
        Initialize the OpenAI client and load the API key from .env.
        """
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        self._client = OpenAI()

    def transcribe(self, audio_filepath: str) -> str:
        """
        Transcribe a WAV audio file to text using the Whisper-1 API.

        Args:
            audio_filepath: Absolute path to the WAV file to transcribe.

        Returns:
            Transcribed text string. May be empty if audio contains no speech.

        Raises:
            RuntimeError: If the API call fails.
        """
        logger.info("Transcribing with Whisper API...")
        t = time.time()
        try:
            with open(audio_filepath, "rb") as f:
                transcript = self._client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="text",
                )
            logger.info(f"You said: '{transcript}' [{time.time() - t:.2f}s]")
            return transcript
        except Exception as e:
            logger.error(f"Whisper API transcription failed: {e}")
            raise RuntimeError(f"Failed to transcribe audio: {e}")


