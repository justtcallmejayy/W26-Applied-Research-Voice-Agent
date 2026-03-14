
"""
src.app.core.engines.tts.gtts_tts

gTTS (Google Text-to-Speech) engine implementation.
Implements TTSEngine using the gTTS library.
Requires internet connection despite being used as the local agent TTS.
"""

import time
import tempfile
from core.engines.base import TTSEngine
from utils.logger import setup_logger

logger = setup_logger(__name__, log_type="engine-tts")


class GTTSEngine(TTSEngine):
    """Synthesises speech using gTTS (Google Text-to-Speech)."""

    def __init__(self, lang: str = "en"):
        """
        Initialise the gTTS engine with the target language.

        Args:
            lang: Language code for speech synthesis. Defaults to English.
        """
        self._lang = lang

    def synthesize(self, text: str) -> str:
        """
        Convert text to speech and save to a temporary MP3 file.

        Args:
            text: The text to synthesise into speech.

        Returns:
            Absolute path to the generated MP3 file.
            Caller is responsible for deleting the file after playback.

        Raises:
            RuntimeError: If gTTS synthesis fails. Check internet connection.
        """
        logger.info("Converting response to speech with gTTS...")
        t = time.time()
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        filepath = temp.name
        temp.close()
        try:
            from gtts import gTTS
            gTTS(text=text, lang=self._lang, slow=False).save(filepath)
            logger.info(f"TTS complete! [{time.time() - t:.2f}s]")
            return filepath
        except Exception as e:
            logger.error(f"gTTS failed: {e}")
            raise RuntimeError(f"gTTS error (check internet connection): {e}")


