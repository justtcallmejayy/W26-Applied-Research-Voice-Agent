"""
tests.integration.test_pipelines_sess

Integration tests for the OnboardingPipeline using pre-recorded audio files.
"""

import os
import pytest
from src.app.core.pipeline import OnboardingPipeline
from src.app.config import SYSTEM_PROMPT, ONBOARDING_FIELDS
from src.app.core.engines.stt.whisper_api import WhisperAPIEngine
from src.app.core.engines.llm.openai_llm import OpenAILLMEngine
from src.app.core.engines.tts.openai_tts import OpenAITTSEngine

def test_full_session_with_prerecorded_audio():
    """Run a full onboarding session using pre-recorded audio files."""
    stt = WhisperAPIEngine()
    llm = OpenAILLMEngine()
    tts = OpenAITTSEngine()

    pipeline = OnboardingPipeline(
        stt=stt,
        llm=llm,
        tts=tts,
        system_prompt=SYSTEM_PROMPT,
        onboarding_fields=ONBOARDING_FIELDS,
    )

    audio_files = [
        "tests/audio/name.wav",
        "tests/audio/employment.wav",
        "tests/audio/skills.wav",
        "tests/audio/education.wav",
        "tests/audio/experience.wav",
        "tests/audio/job_prefs.wav",
    ]

    for f in audio_files:
        if not os.path.exists(f):
            pytest.skip(f"Audio fixture missing: {f} — record files to run integration tests")

    results = []
    for i, audio_path in enumerate(audio_files):
        user_text = stt.transcribe(audio_path)
        current_field = ONBOARDING_FIELDS[i]
        response = pipeline._generate(
            f"[Collecting: {current_field}]\n{user_text}"
        )
        results.append({
            "field": current_field,
            "transcript": user_text,
            "response": response,
        })
        print(f"Turn {i+1} — {current_field}: {user_text} → {response}")

    # Assert all fields got a response
    assert all(r["response"] for r in results)
    assert all(r["transcript"] for r in results)

