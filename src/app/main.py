

"""
src.app.main

Entry point for the voice agent prototype via command line.
"""


import logging
from dotenv import load_dotenv
from openai import OpenAI
from agent.voice_agent import VoiceAgent
from agent.local_voice_agent import LocalVoiceAgent

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
        # Start onboarding interaction
        agent.start_onboarding()        # Agent asks for users name
        max_turns = 1                   # Number of conversational turns

        for turn in range(max_turns):
            logging.info(f"Starting turn {turn + 1} of {max_turns}")

            recorded_audio_path = None
            speech_audio_path = None

            try:
                # First record audio from microphone on user computer
                # then save the audio file locally
                audio_data = agent.record_audio()                   # User would say their name here
                recorded_audio_path = agent.save_audio(audio_data)

                # Next transcribe the audio file to text and 
                # generate response
                user_text = agent.transcribe_audio(recorded_audio_path)
                agent_response = agent.generate_response(user_text)

                # Then generate audio file from text and play audio to the user
                speech_audio_path = agent.text_to_speech(agent_response)
                agent.play_audio(speech_audio_path)

            # Delete both temp files after interaction is complete
            finally:
                if recorded_audio_path:
                    agent.cleanup_file(recorded_audio_path)
                if speech_audio_path:
                    agent.cleanup_file(speech_audio_path)
        logging.info("Session Complete")

    except KeyboardInterrupt:
        logging.info("Session terminated by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()