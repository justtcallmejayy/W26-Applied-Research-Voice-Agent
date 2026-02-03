

"""
src.app.main

Entry point for the voice agent prototype via command line.
"""


import logging
from dotenv import load_dotenv
from openai import OpenAI
from agent.voice_agent import VoiceAgent

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

    # Could change the recording_duration, sample_rate as those are the params it takes
    # we could also change the client from openai if it works with the class
    agent = VoiceAgent(client=client)

    recorded_audio_path = None
    speech_audio_path = None

    try:
        # First record audio from microphone on user computer
        # then save the audio file locally
        audio_data = agent.record_audio()
        recorded_audio_path = agent.save_audio(audio_data)
        
        # Next transcribe the audio file to text and 
        # generate response
        user_text = agent.transcribe_audio(recorded_audio_path)
        agent_response = agent.generate_response(user_text)
        
        # Then generate audio file from text and play audio to the user
        speech_audio_path = agent.text_to_speech(agent_response)
        agent.play_audio(speech_audio_path)
        logging.info("Session Complete")
        print("[LOG] Session complete")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    # Delete both temp files after interaction is complete
    finally:
        if recorded_audio_path:
            agent.cleanup_file(recorded_audio_path)
        if speech_audio_path:
            agent.cleanup_file(speech_audio_path)



if __name__ == "__main__":
    main()