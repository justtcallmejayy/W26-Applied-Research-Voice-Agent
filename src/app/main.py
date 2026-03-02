

"""
src.app.main

Entry point for the voice agent prototype via command line.
"""

import numpy as np
import soundfile as sf
from dotenv import load_dotenv
from openai import OpenAI
from agent.voice_agent import VoiceAgent
from agent.local_voice_agent import LocalVoiceAgent
from agent.onboarding_config import ONBOARDING_FIELDS
from utils.logger import setup_logger

# Initialize logging to file and console
logger = setup_logger(__name__, log_type="main")

def main():
    print("=" * 50)
    print("VOICE ASSISTANT PROTOTYPE")
    print("=" * 50)

    # Change to True/False depending on choice of local vs cloud agent
    USE_LOCAL = False

    if USE_LOCAL:
        logger.info("Using LocalVoiceAgent")
        agent = LocalVoiceAgent()
    else:
        load_dotenv()
        client = OpenAI()
        logger.info("Using VoiceAgent with OpenAI client")
        agent = VoiceAgent(client=client)

    try:
        logger.info("Starting onboarding session...")
        opening = agent.generate_response("Begin the onboarding conversation.")
        speech_path = agent.text_to_speech(opening)
        agent.play_audio(speech_path)
        agent.cleanup_file(speech_path)

        for turn in range(len(ONBOARDING_FIELDS)):
            logger.info(f"Starting turn {turn + 1} of {len(ONBOARDING_FIELDS)}")
            audio_data = agent.record_audio()
            recorded_path = agent.save_audio(audio_data)

            try:
                audio_data_arr, sample_rate = sf.read(recorded_path)
                audio_energy = np.abs(audio_data_arr).mean()
                logger.info(f"Audio Energy: {audio_energy}")

                if audio_energy < 0.01:
                    logger.warning(f"Silent audio on turn {turn + 1} (energy: {audio_energy:.4f}), skipping...")
                    continue

                user_text = agent.transcribe_audio(recorded_path)        
                if not user_text.strip():
                    logger.warning(f"Empty transcription on turn {turn + 1}, skipping...")
                    continue

                response = agent.generate_response(user_text)
                speech_path = agent.text_to_speech(response)
                agent.play_audio(speech_path)
                agent.cleanup_file(speech_path)
            finally:
                agent.cleanup_file(recorded_path)
        
        logger.info("Onboarding session complete.")
    except KeyboardInterrupt:
        logger.info("Session terminated by user during onboarding.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during onboarding: {e}")

if __name__ == "__main__":
    main()