
"""
agent.local_voice_agent

A local voice agent for conversational onboarding. All processing runs on-device with no external
API calls - speech recognition via OpenAI Whisper, language model inference via Ollama, and 
text-to-speech via gTTS.
"""

import logging
import sounddevice as sd
import soundfile as sf
import tempfile
import pygame
import os
import requests
import whisper
import time
from gtts import gTTS
from agent.onboarding_config import SYSTEM_PROMPT

class LocalVoiceAgent:
    """
    A voice agent that handles a full spoken conversation loop entirely on-device.
    """

    def __init__(self, recording_duration=5, sample_rate=16000, whisper_model="base", ollama_model="gemma3:1b"):
        """
        Initialise the agent, loading all local models and verifying Ollama is reachable.
        
        Args:
            recording_duration (int): Seconds of audio to record per turn. Defaults to 5.
            sample_rate (int): Microphone sample rate in Hz. Defaults to 16000.
            whisper_model (str): Whisper model size to load (e.g. "base", "small", "medium").
            ollama_model (str): Ollama model tag to use for response generation.
        """
        self.recording_duration = recording_duration
        self.sample_rate = sample_rate
        self.conversation_history = []
        logging.info("Initializing local models...")
        
        logging.info(f"Loading Whisper model: {whisper_model}")
        self.whisper = whisper.load_model(whisper_model)
        
        logging.info("Checking Ollama connection...")
        self.ollama_model = ollama_model
        self.ollama_url = "http://localhost:11434/api/chat"
        self._check_ollama()
        
        logging.info("Using gTTS for text-to-speech")
        logging.info("All local models ready!")
    
    def _check_ollama(self):
        """
        Verify that Ollama is running and the configured model is available.

        Queries the local Ollama tags endpoint to retrieve installed models.
        If the requested model is not found but others exist, falls back to
        the first available model. Raises if Ollama cannot be reached at all.

        Raises:
            RuntimeError: If Ollama is not reachable or the specified model is not found.
        """
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            if self.ollama_model not in model_names:
                logging.warning(f"Model {self.ollama_model} not found. Available: {model_names}")
                if models:
                    self.ollama_model = models[0]["name"]
                    logging.info(f"Using {self.ollama_model} instead")
                else:
                    raise RuntimeError("No Ollama models found. Run: ollama pull llama3.2")
                    
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Cannot connect to Ollama: {e}\n"
                "Make sure Ollama is running: ollama serve"
            )

    def record_audio(self):
        """
        Record audio from the default microphone for the configured duration.
        Blocks until recording is complete.

        Returns:
            numpy.ndarray: Raw audio samples as a float32 array of shape (samples, 1).     

        Raises:
            RuntimeError: If microphone recording fails.   
        """
        logging.info(f"Recording for {self.recording_duration} seconds... Speak now!")
        t = time.time()

        try:
            audio_data = sd.rec(
                int(self.recording_duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            logging.info(f"Recording complete! [{time.time() - t:.2f}s]")
            return audio_data
        except Exception as e:
            logging.error(f"Audio recording error: {e}")
            raise RuntimeError("Failed to record audio from microphone: {e}")

    def save_audio(self, audio_data):
        """
        Write raw audio data to a temporary WAV file on disk.

        Args:
            audio_data (numpy.ndarray): Audio samples as returned by record_audio().
        
        Returns:
            str: Absolute file path to the saved WAV file.
        
        Raises:
            RuntimeError: If file write fails.
        """
        logging.info("Creating temporary file")

        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            filepath = temp_file.name
            temp_file.close()
            sf.write(filepath, audio_data, self.sample_rate)
            return filepath
        except Exception as e:
            logging.error(f"Failed to save audio file: {e}")
            raise RuntimeError(f"Auido file write error: {e}")

    def transcribe_audio(self, audio_filepath):
        """
        Transcribe a WAV audio file to text using the local Whisper model.

        Args:
            audio_filepath (str): Path to a WAV file to transcribe.

        Returns:
            str: The transcribed text with leading/trailing whitespace stripped.
        
        Raises:
            RuntimeError: If Whisper transcription fails.
        """
        logging.info("Transcribing audio with local Whisper...")
        t = time.time()
        
        try:
            result = self.whisper.transcribe(audio_filepath)
            transcript = result["text"].strip()

            logging.info(f"You said: '{transcript}' [{time.time() - t:.2f}s]")
            return transcript
        except Exception as e:
            logging.error(f"Whisper transcription error: {e}")
            raise RuntimeError(f"Audio transcription failed: {e}")

    def generate_response(self, user_input):
        """
        Generate a conversational response from the local Ollama LLM.

        Appends the user input to conversation history before the request and
        the model's reply afterwards. History is trimmed to the last 8 messages
        to avoid unbounded growth.

        Args:
            user_input (str): The user's transcribed message.

        Returns:
            str: The assistant's response text.

        Raises:
            RuntimeError: If the Ollama server does not respond within the timeout.
        """
        logging.info(f"Generating response with local {self.ollama_model}...")
        t = time.time()
        
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ] + self.conversation_history
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "messages": messages,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            ai_response = response.json()["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Ollama error: {e}")
            raise RuntimeError("Ollama not responding. Is it running?")
        
        self.conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })
        
        # This will get hit once more onboarding fields are added
        if len(self.conversation_history) > 8:
            self.conversation_history = self.conversation_history[-8:]
            logging.info("Trimmed conversation history to last 8 messages")
        
        logging.info(f"Assistant Response: '{ai_response}' [{time.time() - t:.2f}s]")
        return ai_response

    def text_to_speech(self, text):
        """
        Synthesise speech from text and save it to a temporary MP3 file.

        Uses gTTS (Google Text-to-Speech) to generate the audio. The caller
        is responsible for deleting the file after playback via :meth:`cleanup_file`.

        Args:
            text (str): The text to convert to speech.

        Returns:
            str: Absolute path to the generated MP3 file.

        Raises:
            RuntimeError: If TTS generation fails or file save fails.
        """
        logging.info("Converting response to speech with gTTS...")
        t = time.time()
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        speech_filepath = temp.name
        temp.close()
        
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(speech_filepath)
            logging.info(f"TTS complete! [{time.time() - t:.2f}s]")
            return speech_filepath
        except Exception as e:
            logging.error(f"Text to speech failed: {e}")
            raise RuntimeError(f"gTTS error (check internet connection): {e}")

    def play_audio(self, audio_filepath):
        """
        Play an audio file through the default output device using pygame.

        Blocks until playback is complete before returning.

        Args:
            audio_filepath (str): Path to the audio file to play (MP3 or WAV).
        
        Raises:
            RuntimeError: If audio playback fails.
        """
        logging.info("Playing response...")
        t = time.time()
        
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(audio_filepath)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            logging.info(f"Playback complete! [{time.time() - t:.2f}s]")
        except Exception as e:
            logging.error(f"Audio playback failed: {e}")
            raise RuntimeError(f"Failed to play audio: {e}")

    def cleanup_file(self, filepath):
        """
        Delete a temporary file from disk, logging a warning on failure.

        Args:
            filepath (str): Path to the file to delete.
        """
        try:
            os.remove(filepath)
            logging.info("Removed temporary file")
        except Exception as e:
            logging.warning(f"Could not delete {filepath}: {e}")
            