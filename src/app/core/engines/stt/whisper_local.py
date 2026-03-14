
"""
src.app.core.engines.stt.whisper_local

Local Whisper STT engine implementation.
Implements STTEngine using the openai-whisper package running entirely on-device.
Requires FFmpeg to be installed and available on PATH.
"""

import time
from core.engines.base import STTEngine
from utils.logger import setup_logger

logger = setup_logger(__name__, log_type="engine-stt")

class WhisperLocalEngine(STTEngine):
    """Transcribes audio using a local openai-whisper model."""

    def __init__(self, model: str = "base"):
        """
        Load the local Whisper model into memory.

        Args:
            model: Whisper model size to load.
        """
        import whisper
        logger.info(f"Loading local Whisper model: {model}")
        self._model = whisper.load_model(model)

    def transcribe(self, audio_filepath: str) -> str:
        """
        Transcribe a WAV audio file to text using the local Whisper model.

        Args:
            audio_filepath: Absolute path to the WAV file to transcribe.

        Returns:
            Transcribed text string with leading and trailing whitespace stripped.

        Raises:
            RuntimeError: If Whisper transcription fails.
        """
        logger.info("Transcribing with local Whisper...")
        t = time.time()
        try:
            result = self._model.transcribe(audio_filepath)
            transcript = result["text"].strip()
            logger.info(f"You said: '{transcript}' [{time.time() - t:.2f}s]")
            return transcript
        except Exception as e:
            logger.error(f"Local Whisper transcription failed: {e}")
            raise RuntimeError(f"Audio transcription failed: {e}")

