
"""
src.app.core.engines.base

Abstract base interfaces for the voice agent engine layer.
"""

from abc import ABC, abstractmethod

class STTEngine(ABC):
    """Base class for Speech-to-Text engines"""

    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """Transcribe a WAV audio file to text.

        Args:
            audio_path (str): Path to the audio file to transcribe
        
        Returns:
            str: The transcribed text from the audio
        """


class LLMEngine(ABC):
    """Base class for LLM engines"""

    @abstractmethod
    def generate(self, messages: list[dict]) -> str:
        """Generate a response from a list of messages.

        Args:
            messages: OpenAI-style message dicts
        
        Returns:
            str: The assistant's response text
        """

class TTSEngine(ABC):
    """Base class for Text-to-Speech engines"""

    @abstractmethod
    def synthesize(self, text: str) -> str:
        """Convert text to speech and write the result to a temporary file.

        Args:
            text (str): The input text to synthesize
        
        Returns:
            str: The absolute file path to the generated audio file (WAV format).
                 Caller is responsible for deleting the temporary file after playback.
        """