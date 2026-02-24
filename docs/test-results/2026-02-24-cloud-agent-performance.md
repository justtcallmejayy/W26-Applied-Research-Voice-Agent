
# Test Results: Cloud Agent (OpenAI) Performance

**Date**: February 23, 2026  
**Tester**: Brendan Dileo  
**Branch**: `docs/cloud-agent-performance`
**Operating System**: macOS Sonoma 14.1
**Hardware**: MacBook Air M2, 16GB RAM  
**Models Tested**: GPT-4, Whisper-1, TTS-1 (OpenAI API)

---

## 1. Timing Performance

Measured execution time for each pipeline stage across 10 complete onboarding sessions using the VoiceAgent (OpenAI).

**Aggregated Statistics** (30 generations, 20 recordings, 20 transcriptions, 30 TTS, 30 playbacks):

| Operation | Min | Max | Avg |
|-----------|-----|-----|-----|
| Recording | 5.21s | 5.26s | 5.24s |
| Transcription (API) | 0.74s | 2.87s | 1.36s |
| Generation (GPT-4) | 0.72s | 2.56s | 1.40s |
| TTS (OpenAI) | 1.53s | 4.33s | 2.48s |
| Playback | 3.30s | 13.57s | 8.11s |
| **Total/Turn** | — | — | **~18.6s** |

**Sample per-turn totals:**
- Run 1: Turn 1 = 20.9s, Turn 2 = 20.9s
- Run 5: Turn 1 = 18.8s, Turn 2 = 24.8s
- Run 10: Turn 1 = 19.0s, Turn 2 = 20.2s

**Comparison to Local Agent (gemma3:1b):**

| Metric | Cloud (GPT-4) | Local (gemma3:1b) | Difference |
|--------|---------------|-------------------|------------|
| Recording | 5.24s | 5.23s | +0.01s |
| Transcription | 1.36s | 0.94s | +0.42s (slower) |
| Generation | 1.40s | 1.22s | +0.18s (slower) |
| TTS | 2.48s | 1.36s | +1.12s (slower) |
| Playback | 8.11s | 10.01s | -1.90s (faster) |
| **Total/Turn** | **18.6s** | **18.8s** | **-0.2s (comparable)** |

**Key Findings:**
- Cloud based (OpenAI) agent is comparable in total speed to local agent implementation
- Recording is identical across both implementations (hardware dependant)
- Transcription is slower due to API call overhead vs local Whisper
- Generation is slightly slower (GPT-4 vs gemma3:1b)
- TTS is significantly slower (OpenAI TTS vs gTTS)
- Playback is faster on average (GPT-4 responses slightly shorter)
- GPT-4 responses are spoken quicker
- Network latency adds ~1.5s overhead across API calls

---

## 2. Instruction Following

## 2.1 Emoji Compliance

Tested whether GPT-4 follows the system prompt instruction: "Do not use emojis or special characters."

**Results:**
- Total Responses Tested: 30 (across 10 runs)
- Responses with Emojis: 0
- Emoji Usage Rate: 0%
- Runs with at least one emoji: 0 out of 10

**Comparison to Local:**
| Model | Emoji Usage Rate |
|-------|------------------|
| GPT-4 (cloud) | 0% |
| gemma3:1b (local) | 13.3% |

**Key Finding:** GPT-4 follows the "no emoji" instruction perfectly, while gemma3:1b violated it in 13.3% of responses. Seems as if the larger, more capable models, are better at instruction following as expected.

## 2.2 Confirmation Seeking Behaviour

GPT-4 frequently asks for confirmation at the end of onboarding:

**Confirmation Examples:**
- Run 1: "So just to confirm, your name is Brendan and you are currently unemployed. Is that correct?"
- Run 2: "So to confirm, your name is Brendan and you are currently a student. Is that correct?"
- Run 3: "To summarize, your name is Brandon and you're currently employed. Is this correct?"
- Run 4: "Let me confirm the details: Your name is Brendan and you are currently unemployed. Is that correct?"
- Run 7: "To summarize, your name is Brendan and your current employment status is employed. Is that correct?"
- Run 8: "So, let me confirm the details: Your name is Brendan and you are currently employed. Is that correct?"
- Run 10: "So to confirm, your name is Brendan and you're currently employed. Is that correct?"

**Results:**
- Runs with confirmation: 7 out of 10 (70%)
- Comparison to local: gemma3:1b also exhibited confirmation behavior, but less consistently

**Key Finding:** GPT-4 shows strong confirmation behavior (70% of sessions), likely due to the system prompt instruction "Once all fields are collected, confirm the details back to the user." Although this is out of scope, could be beneficial.

---

## 3. Transcription Accuracy

## 3.1 Name Recognition

OpenAI Whisper API occasionally misheard "Brendan" during testing:
- Run 1-2: "Brendan"
- Run 3: "Brandon"
- Run 4-10: "Brendan"

**Results:**
- Total name mentions: 10
- Correct transcriptions: 9
- Incorrect transcriptions: 1
- Error rate: 10%

**Comparison to Local Whisper:**
| Model | Name Error Rate |
|-------|-----------------|
| Whisper API (cloud) | 10% (1/10) |
| Whisper base (local) | 20% (2/10) |

**Key Finding:** Whisper API performs better than local Whisper base model for proper noun recognition. The reason is likely due to the larger model.

## 3.2 Edge Case Handling

GPT-4 showed better handling of ambiguous or unclear user input:

**Run 5 - Ambiguous Response:**
- User: "I'm currently in the middle."
- GPT-4: "I understand, Brendan. It sounds like you might be transitioning between jobs or balancing multiple responsibilities. Could you clarify a bit more? Are you currently employed, unemployed, or a student?"

**Run 6 - Clarification Request:**
- User: "Employment status?"
- GPT-4: "Yes, by employment status I mean are you currently employed, unemployed, a student, or perhaps self-employed?"

**Run 9 - Confused Response:**
- User: "What do you mean?"
- GPT-4: "Apologies for any confusion, Brendan. By employment status, I mean are you currently employed, unemployed, or perhaps a student or retiree? This information will help me find the most suitable job opportunities for you."

**Key Finding:** GPT-4 handles edge cases gracefully by providing clarification and rephrasing questions without breaking conversational flow. gemma3:1b struggled more with ambiguous inputs during local testing.

---

## 4. Response Quality

## 4.1 Greeting Variety

GPT-4 generated varied opening greetings across 10 runs:
- "Of course! I'm here to assist you in your job search. Could you please start by telling me your name?"
- "Hello there! I'm here to assist you in finding a job. May I know your name, please?"
- "Of course! Let's start by getting to know you a little better. May I have your name, please?"
- "Of course, I'd be happy to assist you. Let's start with the basics. May I know your name, please?"
- "Hi there! I'm here to assist you with your job search. May I know your name please?"
- "Of course, I'd be happy to assist you with that. May I start by asking your name?"
- "Absolutely, let's begin. May I know your name, please?"
- "Hello there! I'm here to assist you in your job search. Could you please start by telling me your name?"
- "Of course, let's get started! May I first know your name please?"
- "Sure, I'd be happy to help you with your job search. Could you please tell me your name?"

**Key Finding:** GPT-4 shows high variation in phrasing while maintaining consistent intent. gemma3:1b tended to use more repetitive phrasing across sessions.

## 4.2 Response Length

**Average response lengths (estimated by playback time):**
- Turn 1 (greeting): 3.3s - 6.5s playback (avg: ~5.2s)
- Turn 2 (employment): 5.1s - 9.0s playback (avg: ~7.8s)
- Turn 3 (confirmation): 6.7s - 13.6s playback (avg: ~10.4s)

**Key Finding:** GPT-4 responses increase in length as conversation progresses, with confirmation responses being longest. Responses are generally concise and appropriate for voice interaction.

---

## 5. Error Handling

Tested error scenarios to ensure cloud agent handles failures gracefully.

| Test Case | Steps | Expected | Actual | Pass? |
|-----------|-------|----------|--------|-------|
| **No internet** | Disable WiFi, run agent | Connection error with retry | `[ERROR] OpenAI API call failed: Connection error.` <br> Agent retries then fails gracefully | PASS |
| **Invalid API key** | Set wrong key in .env | Clear authentication error | `[ERROR] Incorrect API key provided... You can find your API key at https://platform.openai.com/account/api-keys` | PASS |
| **Mic permission denied** | Deny mic access in System Settings | Record silence, skip turns | Records silence → Whisper returns `'you'` → Continues with bad data (no skip logic) | FAIL |
| **Corrupted audio file** | Feed invalid file to Whisper API | API rejects with format error | `Error code: 400 - Invalid file format. Supported formats: ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']` | PASS |

**Key Findings:**
- No internet: Fails gracefully after retry attempts with clear error message
- Invalid API key: Very clear error with actionable guidance (link to API keys page)
- Mic permission denied: **CRITICAL ISSUE** - Does not skip empty/garbage transcriptions like local agent does. Whisper API returns `'you'` for silence, causing bad data to enter the conversation
- Corrupted audio: API validates file format and rejects with clear error message

**Issues Found:**
- **Mic permission handling broken**: Unlike local agent which skips empty transcriptions, the cloud agent (OpenAI API) continues with garbage data when Whisper API mishears silence as `'you'`
- Root cause: Empty transcript check in `main.py` only catches literal empty strings (`""`), but Whisper API returns `"you\n"` for silence/noise

- **Fix needed**: Improve transcript validation to catch near-empty or garbage transcripts (e.g., single-word responses under 3 characters)

---

## Summary

### What Worked:
- Timing performance comparable to local agent despite API overhead
- Perfect instruction-following (0% emoji usage vs 13.3% for local)
- Better transcription accuracy (10% name errors vs 20% for local)
- Superior edge case handling (clarifications, rephrasing)
- More natural and varied responses
- Consistent confirmation behavior (70% of sessions)
- Error handling for API failures (no internet, invalid key, corrupted files)

### Issues Found:
- TTS significantly slower (2.48s vs 1.36s for gTTS)
- Transcription slower due to API overhead (1.36s vs 0.94s)
- Cannot function without internet (all services are cloud-based)
- Confirmation behavior very consistent (may be too frequent)
- **CRITICAL: Mic permission denial not handled properly** - Whisper API returns garbage transcriptions (`'you'`) for silence instead of empty string, causing bad data to enter conversation without validation