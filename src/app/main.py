

"""
src.app.main

Entry point for the voice agent prototype via command line.
"""


import logging
from dotenv import load_dotenv
from openai import OpenAI
from agent.voice_agent import VoiceAgent
from agent.local_voice_agent import LocalVoiceAgent
from agent.onboarding_config import ONBOARDING_FIELDS


# Initialize logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
    handlers=[
        logging.FileHandler('src/app/logs/app.log'), # to file
        logging.StreamHandler()                      # to console
    ]
)

# Load env vars and initialize OpenAI client
load_dotenv()
client = OpenAI()

def main():

    print("=" * 50)
    print("VOICE ASSISTANT PROTOTYPE")
    print("=" * 50)

    # Change to True/False depending on choice of local vs cloud agent
    USE_LOCAL = True

    if USE_LOCAL:
        logging.info("Using LocalVoiceAgent")
        agent = LocalVoiceAgent()
    else:
        # Could change the recording_duration, sample_rate as those are the params it takes
        # we could also change the client from openai if it works with the class
        logging.info("Using VoiceAgent with OpenAI client")
        agent = VoiceAgent(client=client)

    try:
        logging.info("Starting onboarding session...")
        opening = agent.generate_response("Begin the onboarding conversation.")
        speech_path = agent.text_to_speech(opening)
        agent.play_audio(speech_path)
        agent.cleanup_file(speech_path)

        for turn in range(len(ONBOARDING_FIELDS)):
            logging.info(f"Starting turn {turn + 1} of {len(ONBOARDING_FIELDS)}")
            audio_data = agent.record_audio()
            recorded_path = agent.save_audio(audio_data)

            try:
                user_text = agent.transcribe_audio(recorded_path)
                response = agent.generate_response(user_text)
                speech_path = agent.text_to_speech(response)
                agent.play_audio(speech_path)
                agent.cleanup_file(speech_path)
            finally:
                agent.cleanup_file(recorded_path)
    except KeyboardInterrupt:
        logging.info("Session terminated by user during onboarding.")
    except Exception as e:
        logging.error(f"An unexpected error occurred during onboarding: {e}")

if __name__ == "__main__":
    main()