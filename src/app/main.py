

"""
src.app.main

Entry point for the voice agent prototype via command line.
To switch providers, update the ENGINES dict in config.py
"""

from utils.logger import setup_logger
from config import ENGINES, ONBOARDING_FIELDS, SYSTEM_PROMPT, RECORDING_DURATION, AUDIO_SAMPLE_RATE, ENERGY_THRESHOLD
from core.pipeline import load_engine, OnboardingPipeline

logger = setup_logger(__name__, log_type="main")

def main():
    print("=" * 50)
    print("VOICE ASSISTANT PROTOTYPE")
    print("=" * 50)

    logger.info(f"Loading engines: {ENGINES}")
    stt = load_engine(ENGINES["stt"])
    llm = load_engine(ENGINES["llm"])
    tts = load_engine(ENGINES["tts"])

    pipeline = OnboardingPipeline(
        stt=stt,
        llm=llm,
        tts=tts,
        system_prompt=SYSTEM_PROMPT,
        onboarding_fields=ONBOARDING_FIELDS,
        recording_duration=RECORDING_DURATION,
        sample_rate=AUDIO_SAMPLE_RATE,
        energy_threshold=ENERGY_THRESHOLD,
    )

    try:
        pipeline.run()
    except KeyboardInterrupt:
        logger.info("Session terminated by user.")
    except Exception as e:
        logger.error(f"Unexpected error during onboarding: {e}")

if __name__ == "__main__":
    main()