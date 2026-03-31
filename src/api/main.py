"""
src.api.main

FastAPI REST API wrapper around the OnboardingPipeline.
Exposes endpoints for starting a session and processing each turn.
"""

import os
import sys
import uuid
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "app"))


from app.config import (
    ENGINES,
    SYSTEM_PROMPT,
    ONBOARDING_FIELDS,
    RECORDING_DURATION,
    AUDIO_SAMPLE_RATE,
    ENERGY_THRESHOLD,
)

from app.core.pipeline import OnboardingPipeline, load_engine
from app.utils.logger import setup_logger

logger = setup_logger(__name__, log_type="api")

def safe_header(text: str) -> str:
    """Strip non-latin-1 and illegal header characters from text """
    text = text.replace("\n", " ").replace("\r", " ")
    return text.encode("latin-1", errors="ignore").decode("latin-1")



app = FastAPI(
    title="Voice Onboarding API",
    description="REST API for the Enabled Talent voice onboarding pipeline.",
    version="1.0.0",
)

# Allow all origins for prototype - in prod this would be restricted
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session store
sessions: dict[str, dict] = {}


def create_pipeline() -> OnboardingPipeline:
    """ Instantiate a new OnboardingPipeline from config """
    return OnboardingPipeline(
        stt=load_engine(ENGINES["stt"]),
        llm=load_engine(ENGINES["llm"]),
        tts=load_engine(ENGINES["tts"]),
        system_prompt=SYSTEM_PROMPT,
        onboarding_fields=ONBOARDING_FIELDS,
        recording_duration=RECORDING_DURATION,
        sample_rate=AUDIO_SAMPLE_RATE,
        energy_threshold=ENERGY_THRESHOLD,
    )



@app.post("/session/start")
def start_session():
    """
    Start a new onboarding session.
    Returns a session ID and the opening audio message.

    Response headers:
        X-Session-ID: unique session identifier
        X-Turn: current turn number (0)
        X-Field: current field being collected
        X-Total-Turns: total number of fields
    """
    session_id = str(uuid.uuid4())
    pipeline = create_pipeline()
    sessions[session_id] = {
        "pipeline": pipeline,
        "turn": 0,
    }

    opening_text = pipeline._generate("Begin the onboarding conversation.")
    if not opening_text:
        raise HTTPException(status_code=500, detail="Failed to generate opening message.")

    audio_path = pipeline.tts.synthesize(opening_text)

    logger.info(f"Session {session_id} started.")

    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        headers={
            "X-Session-ID": session_id,
            "X-Turn": "0",
            "X-Field": ONBOARDING_FIELDS[0],
            "X-Total-Turns": str(len(ONBOARDING_FIELDS)),
            "X-Response-Text": safe_header(opening_text),
        },
    )


@app.post("/session/{session_id}/turn")
async def process_turn(session_id: str, audio: UploadFile = File(...)):
    """
    Process a single onboarding turn.
    Accepts audio from the frontend, runs STT -> LLM -> TTS, returns audio response.

    Args:
        session_id: Session ID returned from /session/start
        audio: Audio file recorded by the frontend (WAV format)

    Response headers:
        X-Transcript: what the user said
        X-Response-Text: what the agent said
        X-Turn: turn number just completed
        X-Field: field that was collected
        X-Next-Field: next field to collect (empty if session complete)
        X-Session-Complete: true if all fields collected
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    session = sessions[session_id]
    pipeline = session["pipeline"]
    turn = session["turn"]

    if turn >= len(ONBOARDING_FIELDS):
        raise HTTPException(status_code=400, detail="Session already complete.")

    current_field = ONBOARDING_FIELDS[turn]

    # Save uploaded audio to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        # STT
        user_text = pipeline.stt.transcribe(tmp_path)
        if not user_text.strip():
            raise HTTPException(status_code=400, detail="No speech detected in audio.")

        # LLM
        response_text = pipeline._generate(
            f"[Collecting: {current_field}]\n{user_text}"
        )
        if not response_text:
            raise HTTPException(status_code=500, detail="LLM returned empty response.")

        # TTS
        audio_path = pipeline.tts.synthesize(response_text)

        # Advance turn
        session["turn"] += 1
        next_turn = session["turn"]
        session_complete = next_turn >= len(ONBOARDING_FIELDS)
        next_field = ONBOARDING_FIELDS[next_turn] if not session_complete else ""

        logger.info(f"Session {session_id} — turn {turn + 1} complete — field: {current_field}")

        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            headers={
                "X-Transcript": safe_header(user_text),
                "X-Response-Text": safe_header(response_text),
                "X-Turn": str(turn + 1),
                "X-Field": current_field,
                "X-Next-Field": next_field,
                "X-Session-Complete": str(session_complete).lower(),
            },
        )
    finally:
        os.remove(tmp_path)


@app.post("/session/{session_id}/confirm")
async def confirm_session(session_id: str, audio: UploadFile = File(...)):
    """
    Process the user's confirmation response after all fields are collected.
    Returns a closing audio message.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    session = sessions[session_id]
    pipeline = session["pipeline"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        user_text = pipeline.stt.transcribe(tmp_path)
        response_text = pipeline._generate(user_text)
        audio_path = pipeline.tts.synthesize(response_text)

        # Clean up session
        del sessions[session_id]
        logger.info(f"Session {session_id} confirmed and closed.")

        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            headers={
                "X-Transcript": safe_header(user_text),
                "X-Response-Text": safe_header(response_text),
                "X-Session-Complete": "true",
            },
        )
    finally:
        os.remove(tmp_path)


@app.delete("/session/{session_id}")
def end_session(session_id: str):
    """
    End and clean up a session.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    del sessions[session_id]
    logger.info(f"Session {session_id} ended.")
    return {"message": "Session ended."}


@app.get("/health")
def health_check():
    """ 
    Health check endpoint 
    """
    return {
        "status": "ok",
        "engines": ENGINES,
        "fields": ONBOARDING_FIELDS,
        "active_sessions": len(sessions),
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)