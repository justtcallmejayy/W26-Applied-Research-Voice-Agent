# API

# API

REST API wrapper around the `OnboardingPipeline`. Exposes the voice onboarding session over HTTP so any frontend can record audio and interact with the pipeline without requiring the full Python environment.

Built with FastAPI. Interactive docs available at `http://localhost:8000/docs` when running locally.

---

## Running the API

```bash
cd src
python3 api/main.py
```

The API starts on `http://localhost:8000` by default. Provider selection is controlled by the `ENGINES` dict in `src/app/config.py` — no API code changes needed to swap STT, LLM, or TTS.

---

## Endpoints

### `GET /health`
Returns the current engine configuration, onboarding field list, and number of active sessions. Use this to confirm the API is running and engines are loaded correctly.

**Response:**
```json
{
  "status": "ok",
  "engines": {
    "stt": "core.engines.stt.whisper_local.WhisperLocalEngine",
    "llm": "core.engines.llm.openrouter_llm.OpenRouterLLMEngine",
    "tts": "core.engines.tts.gtts_tts.GTTSEngine"
  },
  "fields": ["name", "employment_status", "skills", "education", "experience", "job_preferences"],
  "active_sessions": 0
}
```

---

### `POST /session/start`
Starts a new onboarding session. Instantiates a fresh `OnboardingPipeline`, generates an opening message via the LLM, synthesizes it to audio, and returns the audio file. The session ID must be saved by the client for all subsequent requests.

**Response:** Audio file (`audio/mpeg`) with metadata in headers.

| Header | Description |
|--------|-------------|
| `X-Session-ID` | UUID for this session — pass this in all subsequent requests |
| `X-Turn` | Current turn number (`0`) |
| `X-Field` | First field being collected (`name`) |
| `X-Total-Turns` | Total number of fields (`6`) |
| `X-Response-Text` | Opening message text |

---

### `POST /session/{session_id}/turn`
Processes a single onboarding turn. Accepts a WAV audio file from the frontend, runs it through STT → LLM → TTS, and returns the agent's response as audio. Call this once per field in order.

**Request:** `multipart/form-data` with a `audio` field containing a WAV file.

**Response:** Audio file (`audio/mpeg`) with metadata in headers.

| Header | Description |
|--------|-------------|
| `X-Transcript` | What the user said (STT output) |
| `X-Response-Text` | What the agent said (LLM output) |
| `X-Turn` | Turn number just completed |
| `X-Field` | Field that was collected this turn |
| `X-Next-Field` | Next field to collect (empty if session complete) |
| `X-Session-Complete` | `true` if all 6 fields have been collected |

**Errors:**
- `404` — session ID not found
- `400` — session already complete, or no speech detected in audio
- `500` — LLM returned empty response

---

### `POST /session/{session_id}/confirm`
Processes the user's confirmation response after all 6 fields have been collected. Accepts a WAV audio file, runs STT → LLM → TTS, returns a closing audio message, and deletes the session from the store.

**Request:** `multipart/form-data` with an `audio` field containing a WAV file.

**Response:** Audio file (`audio/mpeg`) with metadata in headers.

| Header | Description |
|--------|-------------|
| `X-Transcript` | What the user said |
| `X-Response-Text` | Closing message text |
| `X-Session-Complete` | Always `true` |

---

### `DELETE /session/{session_id}`
Ends and cleans up a session without going through confirmation. Use this to cancel a session early or clean up after an error.

**Response:**
```json
{ "message": "Session ended." }
```

---

## Typical Session Flow

```
POST /session/start
  → save X-Session-ID from response headers

POST /session/{id}/turn   ← name.wav
POST /session/{id}/turn   ← employment_status.wav
POST /session/{id}/turn   ← skills.wav
POST /session/{id}/turn   ← education.wav
POST /session/{id}/turn   ← experience.wav
POST /session/{id}/turn   ← job_preferences.wav
  → X-Session-Complete: true in final turn response

POST /session/{id}/confirm  ← confirmation.wav
  → session closed
```

---

## Example curl Commands

```bash
# Health check
curl http://localhost:8000/health

# Start a session
curl -X POST http://localhost:8000/session/start \
  --output opening.mp3 -D -

# Submit a turn (replace SESSION_ID with value from X-Session-ID header)
curl -X POST http://localhost:8000/session/SESSION_ID/turn \
  -F "audio=@tests/audio/name.wav" \
  --output response.mp3 -D -

# Confirm session
curl -X POST http://localhost:8000/session/SESSION_ID/confirm \
  -F "audio=@tests/audio/confirm.wav" \
  --output closing.mp3 -D -

# End session early
curl -X DELETE http://localhost:8000/session/SESSION_ID
```

The `-D -` flag prints response headers to stdout so you can see `X-Session-ID`, `X-Transcript`, etc. alongside the audio output.

---

## Notes

- **Session store is in-memory.** Sessions are lost if the server restarts. Production deployment would require Redis or a database.
- **Audio format.** The API expects WAV input from the frontend. Response audio is MP3 (gTTS and OpenAI TTS both output MP3).
- **Header encoding.** LLM and STT output in response headers is sanitised to latin-1 with newlines stripped. Typographic characters are removed silently.
- **OpenRouter rate limits.** The free tier allows 50 requests/day across all free models. Each turn consumes one request. At 7 LLM calls per session (including the opening message), the cap supports ~7 full sessions per day.
