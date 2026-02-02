

"""
src.app.main

Entry point for the voice agent prototype via command line.
"""


import logging
from agent.voice_agent import VoiceAgent

# Initialize logging to file and console
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('src/app/logs/app.log'), # to file
        logging.StreamHandler()              # to console
    ]
)



def main():

    print("=" * 50)
    print("VOICE ASSISTANT PROTOTYPE")
    print("=" * 50)

    agent = VoiceAgent()

    try:
        logging.info("Starting up...")
        pass
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")



if __name__ == "__main__":
    main()