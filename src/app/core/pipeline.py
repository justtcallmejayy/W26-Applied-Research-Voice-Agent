"""
src.app.core.pipeline

Dynamic engine loader and OnboardingPipeline.
All audio I/O, conversation history management, and turn sequencing lives here.
STT, LLM, and TTS are injected as engine instances, the pipeline is provider-agnostic.
"""

import os
import time
import pygame
import tempfile
import importlib
import numpy as np
import sounddevice as sd
import soundfile as sf
from core.engines.base import STTEngine, LLMEngine, TTSEngine
from config import MAX_HISTORY_LENGTH, OPENING_TEXT
from utils.logger import setup_logger

logger = setup_logger(__name__, log_type="pipeline")

def load_engine(dotted_path: str) -> STTEngine | LLMEngine | TTSEngine:
    """
    Instantiate an engine class from a dotted import path.

    Args:
        dotted_path: Dotted path to the engine class,
                     e.g. "core.engines.stt.whisper_api.WhisperAPIEngine"

    Returns:
        An instance of the resolved engine class.

    Raises:
        ImportError: If the module or class cannot be found.
    """
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls()


class OnboardingPipeline:
    """
    Drives the voice onboarding conversation loop.
    Audio I/O (record, save, play, cleanup) lives here. 
    """

    def __init__(
        self,
        stt: STTEngine,
        llm: LLMEngine,
        tts: TTSEngine,
        system_prompt: str,
        onboarding_fields: list[str],
        recording_duration: int = 5,
        sample_rate: int = 16000,
        energy_threshold: float = 0.01,
    ):
        """
        Initialise the pipeline with engine instances and audio settings.

        Args:
            stt: STT engine instance for transcribing audio.
            llm: LLM engine instance for generating responses.
            tts: TTS engine instance for synthesising speech.
            system_prompt: System prompt passed to the LLM on every turn.
            onboarding_fields: Ordered list of fields to collect from the user.
            recording_duration: Seconds of audio to record per turn.
            sample_rate: Microphone sample rate in Hz.
            energy_threshold: RMS amplitude below which a turn is skipped as silent.
        """
        self.stt = stt
        self.llm = llm
        self.tts = tts
        self.system_prompt = system_prompt
        self.onboarding_fields = onboarding_fields
        self.recording_duration = recording_duration
        self.sample_rate = sample_rate
        self.energy_threshold = energy_threshold
        self.conversation_history: list[dict] = []

    def get_opening(self) -> tuple[str, str]:
        """
        Return the hardcoded opening text and synthesise it to a temp audio file.

        This is the single source of truth for the opening message — used by
        both the CLI runner and the REST API so behaviour is consistent.

        Returns:
            Tuple of (opening_text, audio_filepath).
            The caller is responsible for cleaning up the audio file.
        """
        audio_path = self.tts.synthesize(OPENING_TEXT)
        return OPENING_TEXT, audio_path

    def record_audio(self) -> np.ndarray:
        """
        Record audio from the default microphone for the configured duration.

        Returns:
            Raw audio samples as a float32 numpy array of shape (samples, 1).

        Raises:
            RuntimeError: If microphone recording fails.
        """
        logger.info(f"Recording for {self.recording_duration} seconds... Speak now!")
        t = time.time()
        try:
            audio_data = sd.rec(
                int(self.recording_duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
            )
            sd.wait()
            logger.info(f"Recording complete! [{time.time() - t:.2f}s]")
            return audio_data
        except Exception as e:
            logger.error(f"Microphone recording failed: {e}")
            raise RuntimeError(f"Failed to record audio: {e}")

    def save_audio(self, audio_data: np.ndarray) -> str:
        """
        Write raw audio samples to a temporary WAV file on disk.

        Args:
            audio_data: Audio samples as returned by record_audio().

        Returns:
            Absolute path to the saved WAV file.

        Raises:
            RuntimeError: If the file write fails.
        """
        try:
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            filepath = temp.name
            temp.close()
            sf.write(filepath, audio_data, self.sample_rate)
            return filepath
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            raise RuntimeError(f"Audio file write error: {e}")

    def play_audio(self, filepath: str):
        """
        Play an audio file through the default output device using pygame.
        Blocks until playback is complete.

        Args:
            filepath: Path to the audio file to play (MP3 or WAV).

        Raises:
            RuntimeError: If audio playback fails.
        """
        logger.info("Playing response...")
        t = time.time()
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            logger.info(f"Playback complete! [{time.time() - t:.2f}s]")
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
            raise RuntimeError(f"Failed to play audio: {e}")

    def cleanup_file(self, filepath: str):
        """
        Delete a temporary file from disk, logging a warning on failure.

        Args:
            filepath: Path to the file to delete.
        """
        try:
            os.remove(filepath)
            logger.info("Removed temporary file")
        except Exception as e:
            logger.warning(f"Could not delete {filepath}: {e}")

    def _generate(self, user_input: str) -> str:
        """
        Append user input to history, call the LLM, append the response,
        and trim history to MAX_HISTORY_LENGTH if exceeded.

        Args:
            user_input: The user's transcribed message or initial prompt.

        Returns:
            The assistant's response text, or empty string if LLM returns nothing.
        """
        self.conversation_history.append({"role": "user", "content": user_input})
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
        response = self.llm.generate(messages)
        if not response or not response.strip():
            logger.warning("LLM returned empty response, skipping turn...")
            self.conversation_history.pop()
            return ""

        self.conversation_history.append({"role": "assistant", "content": response})
        if len(self.conversation_history) > MAX_HISTORY_LENGTH:
            self.conversation_history = self.conversation_history[-MAX_HISTORY_LENGTH:]
            logger.info(f"Trimmed conversation history to last {MAX_HISTORY_LENGTH} messages")
        return response

    def _speak(self, text: str):
        """
        Synthesise text to speech, play the audio, and delete the temp file.

        Args:
            text: The text to speak aloud.
        """
        filepath = self.tts.synthesize(text)
        self.play_audio(filepath)
        self.cleanup_file(filepath)

    def run(self):
        """
        Run the full onboarding session.

        Plays the hardcoded opening message, then loops through each onboarding
        field collecting one user response per turn. Silent or empty turns
        are skipped. Temporary audio files are cleaned up after each turn.
        """
        logger.info("Starting onboarding session...")

        opening_text, opening_path = self.get_opening()
        self.play_audio(opening_path)
        self.cleanup_file(opening_path)

        for turn in range(len(self.onboarding_fields)):
            current_field = self.onboarding_fields[turn]
            logger.info(f"Starting turn {turn + 1} of {len(self.onboarding_fields)} — collecting: {current_field}")
            audio_data = self.record_audio()
            recorded_path = self.save_audio(audio_data)

            try:
                audio_arr, _ = sf.read(recorded_path)
                energy = np.abs(audio_arr).mean()
                logger.info(f"Audio energy: {energy:.4f}")

                if energy < self.energy_threshold:
                    logger.warning(f"Silent audio on turn {turn + 1} (energy: {energy:.4f}), skipping...")
                    continue

                user_text = self.stt.transcribe(recorded_path)
                if not user_text.strip():
                    logger.warning(f"Empty transcription on turn {turn + 1}, skipping...")
                    continue

                response = self._generate(f"[Collecting: {current_field}]\n{user_text}")
                if not response:
                    logger.warning(f"Skipping TTS on turn {turn + 1} - empty LLM response")
                    continue

                self._speak(response)
            finally:
                self.cleanup_file(recorded_path)

        logger.info("Onboarding session complete.")