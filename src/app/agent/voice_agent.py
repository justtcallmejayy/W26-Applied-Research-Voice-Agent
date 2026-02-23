

"""
src.app.agent.voice_agent

Defines the VoiceAgent class, which implements a voice based conversational agent for applied research.
It supports end to end voice interaction by recording audio from the users microphone, transcribing speech to text, generating a response using a LLM,
converting text to synthesized speech, and playing audio output to the user.

This module relies on external services for speech to text, text generation, and text to speech, and assumes the presence of functional audio input and output devices on the users system.
"""

import logging
import sounddevice as sd
import soundfile as sf
import tempfile
import pygame
import os
import time


class VoiceAgent:

    def __init__(self, client, recording_duration=5, sample_rate=16000):
        """
        Constructor to initialize the VoiceAgent with audio settings.
        
        Args:
            client: The client instance used to communicate with external voice services.
            recording_duration (int): The length of each recording in seconds.
            sample_rate (int): Audio sample rate in Hz.
        """
        self.client = client
        self.recording_duration = recording_duration
        self.sample_rate = sample_rate
        self.conversation_history = []


    def record_audio(self):
        """
        Records audio from the users default microphone.

        Captures mono audio input from the systems default input device for a fixed duration 
        using the configured sample rate.

        The recorded audio is returned as a numpy array containing floating point amplitude values,
        where each value represents sound pressure level at a specific moment in time.

        Returns:
            numpy.ndarray: a 2D numpy array of shape (samples, 1) containing float32 audio samples
            with values typically in the range [-1.0, 1.0].
        """
        logging.info(f"Recording for {self.recording_duration} seconds... Speak now!")
        t = time.time()

        audio_data = sd.rec(
            int(self.recording_duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,  # Mono audio
            dtype='float32'
        )
        sd.wait()

        logging.info(f"Recording complete! [{time.time() - t:.2f}s]")
        return audio_data
    

    def save_audio(self, audio_data):
        """
        Saves recorded audio samples to a temporary WAV file.
        
        Converts raw audio samples stored as a numpy array into a WAV file on disk using the configured sample rate.
        The file is created as a temporary file and is not automatically deleted, allowing it to be passed to external services.

        Args:
            audio_data (numpy.ndarray): A numpy array containing audio amplitude samples (float32).

        Returns:
            str: The file path to the saved temporary WAV file.
        """
        logging.info("Creating temporary file")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        filepath = temp_file.name
        temp_file.close()
        
        # Write audio data to file
        sf.write(filepath, audio_data, self.sample_rate)
        return filepath

    def transcribe_audio(self, audio_filepath):
        """
        Transcribes spoken audio into stored in a WAV file into text using the Whisper API.

        Reads an audio file from disk and sends it to an external API for transcription.
        The returned text represents the spoken content of the audio.

        Args:
            audio_filepath (str): A path to the WAV audio file containing the recorded speech.
        
        Returns:
            str: The transcribed text representing the spoken content produced by the speech to text model.
        """
        logging.info("Transcribing audio...")
        t = time.time()
        
        with open(audio_filepath, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",          # Whisper 1 for now
                file=audio_file,
                response_format="text"
            )
        logging.info(f"You said: '{transcript}' [{time.time() - t:.2f}s]")
        return transcript

    def generate_response(self, user_input):
        """
        Generates a conversational response using a language model based on user speech input.

        Sends the the users transcribed text to a GPT-based language model and returns a short, conversational response suitable for spoken output.

        Args:
            user_input (str): The transcribed text representing the users spoken input.

        Returns:
            str: The generated response text from the language model.
        """
        logging.info("Generating response...")
        t = time.time()

        # Add user input to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Build list of messages for chat completion
        messages = [
            {
                "role": "system",
                "content": "You are a helpful onboarding voice assistant. Keep responses concise and conversational."
            }
        ] + self.conversation_history

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            temperature=0.7,
            presence_penalty=0.5,
            frequency_penalty=0.2
        )
        ai_response = response.choices[0].message.content

        # Add model response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })

        # Limit conversation history to last 8 messages
        max_messages = 8
        if (len(self.conversation_history) > max_messages):
            self.conversation_history = self.conversation_history[-max_messages:]
            logging.info("Trimming conversation history to last 8 messages")

        logging.info(f"Assistant Response: '{ai_response}' [{time.time() - t:.2f}s]")
        return ai_response

    def text_to_speech(self, text):
        """
        Converts a text response into synthesized speech audio using a TTS API.

        Sends text to an external text to speech service and saves the generated audio to a temporary file on disk.

        Args:
            text (str): The text response to be converted to speech.
        
        Returns:
            str: The file path to the saved temporary MP3 audio file.
        """
        logging.info("Converting response to speech...")
        t = time.time()
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        speech_filepath = temp.name
        temp.close()
        
        response = self.client.audio.speech.create(
            model="tts-1",  # Audio model, quality will differ
            voice="alloy",  # Type of voice that the user will hear
            input=text
        )
        
        response.stream_to_file(speech_filepath)
        logging.info(f"TTS complete! [{time.time() - t:.2f}s]")
        return speech_filepath

    def play_audio(self, audio_filepath):
        """
        Plays an audio file through the systems default audio output.

        Loads and plays an audio file using the pygame mixer module and blocks execution until playback is complete.
        
        Args:
            audio_filepath (str): The file path to the audio file to be played.
        """
        logging.info("Playing response...")
        t = time.time()
        
        # This approach relies on the PYGAME module - may not be ideal long term
        pygame.mixer.init()
        pygame.mixer.music.load(audio_filepath)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        logging.info(f"Playback complete! [{time.time() - t:.2f}s]")


    def cleanup_file(self, filepath):
        """
        Deletes a temporary file from the file system.

        Attemps to remove a file from disk and logs a warning if deletion fails.

        Args:
            filepath (str): The path to the file to be deleted.
        """
        try:
            os.remove(filepath)
            logging.info("Removed temporary file")
        except Exception as e:
            logging.warning(f"Could not delete {filepath} : {e}")


    def start_onboarding(self):
        """
        Initates the onboarding conversation with a greeting and prompts the user for their name.
        """
        greeting = "Hi! Welcome to onboarding. Whats your name?"
        logging.info(f"Assistant Greeting: '{greeting}'")

        # Convert greeting to speech and play
        speech_filepath = self.text_to_speech(greeting)
        self.play_audio(speech_filepath)
        self.cleanup_file(speech_filepath)

        # Add to convo history to maintain context
        self.conversation_history.append({
            "role": "assistant",
            "content": greeting
        })