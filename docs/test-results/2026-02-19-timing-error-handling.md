
# Test Results: Timing Metrics & Error Handling

**Date**: February 19 & 20, 2026  
**Tester**: Brendan Dileo  
**Branch**: `docs/add-test-results`
**Operating System**: macOS Sonoma 14.1
**Hardware**: MacBook Air M2, 16GB RAM  
**Models Tested**: gemma3:1b (local)

---

## 1. Timing Performance

Measured execution time for each pipeline stage across 10 complete onboarding sessions.

### Local Agent (gemma3:1b)

**Aggregated Statistics** (30 generations, 20 recordings, 20 transcriptions, 30 TTS, 30 playbacks):

| Operation | Min | Max | Avg |
|-----------|-----|-----|-----|
| Recording | 5.22s | 5.25s | 5.23s | 
| Transcription | 0.70s | 1.63s | 0.94s |
| Generation (LLM) | 0.72s | 2.64s | 1.22s |
| TTS (gTTS) | 0.37s | 2.22s | 1.36s |
| Playback | 3.83s | 14.78s | 10.01s |
| **Total/Turn** | — | — | **~18.8s** |

**Sample per-turn totals:**
- Run 1: Turn 1 = 23.1s, Turn 2 = 13.4s
- Run 5: Turn 1 = 21.2s, Turn 2 = 19.6s
- Run 10: Turn 1 = 18.0s, Turn 2 = 19.2s

**Key Findings:**
- Recording is very consistent (always around 5.23s)
- Transcription is fast and stable (under 1 second on average)
- Generation is the fastest operation (1.22s average for gemma3:1b)
- TTS takes about 1.4 seconds on average
- Playback time varies the most (4-15 seconds depending on response length)
- Total time per turn averages about 19 seconds

---

## 2. Error Handling

Tested error scenarios to ensure failures are handled gracefully.

| Test Case | Steps | Expected | Actual | Pass? |
|-----------|-------|----------|--------|-------|
| **Ollama not running** | Stop Ollama, run agent | Clear error message | `RuntimeError: Cannot connect to Ollama... Make sure Ollama is running: ollama serve` | PASS |
| **No internet (TTS)** | Turn off WiFi, run agent | Error when TTS called with network hint | `[ERROR] Text to speech failed: Failed to connect. Probable cause: Unknown` <br> `RuntimeError: gTTS error (check internet connection)` | PASS |
| **Mic permission denied** | Deny mic access in System Settings, run agent | Record silence, empty transcript, skip turns | Records silence → `You said: ''` → `Empty transcription on turn X, skipping...` | PASS |
| **No model available** | `ollama rm gemma3:1b`, run agent | Clear error with guidance | `RuntimeError: No Ollama models found. Run: ollama pull llama3.2` | PASS |
| **Wrong model specified** | Set `ollama_model="gemma9000:1b"`, run agent | Same as no model (fallback fails if none exist) | `RuntimeError: No Ollama models found. Run: ollama pull llama3.2` | PASS |
| **Corrupted audio file** | Feed invalid WAV to transcription | RuntimeError from Whisper/ffmpeg | `RuntimeError: Audio transcription failed: Failed to load audio... Invalid data found when processing input` | PASS |

**Key Findings:**
- All tested error scenarios handled gracefully with descriptive messages
- Ollama connection errors are caught and display helpful messages
- No internet: Agent generates response successfully (local LLM), but crashes when TTS tries to use gTTS (requires internet)
- Mic denied: Doesn't crash - records silence, skips turns, completes session
- Missing models: Clear guidance provided (`ollama pull llama3.2`)
- Corrupted audio: Whisper/ffmpeg error is caught and wrapped in RuntimeError with context
- Error messages include actionable next steps for the user

---

## 3. Model Behavior

### 3.1 Emoji Usage

Tested whether gemma3:1b follows the system prompt instruction: "Do not use emojis or special characters."

**Results:**
- Total Responses Tested: 30 (across 10 runs)
- Responses with Emojis: 4
- Emoji Usage Rate: 13.3%
- Runs with at least one emoji: 3 out of 10

**Examples:**
| Run | Response | Emoji |
|-----|----------|-------|
| 2 | "Great to meet you, Brendan! 😊" | 😊 |
| 3 | "Great to meet you, Brendan! 😊" | 😊 |
| 10 | "Great to meet you, Brendan! 😊" | 😊 |

**Key Findings:**
- gemma3:1b uses emojis in about 1 out of 7 responses despite being told not to 
- Emojis appear most frequently in greeting messages
- Research indicates smaller models (1B parameters) struggle to follow negative instructions (dont do X)

### 3.2 Confirmation-Seeking Behavior

gemma3:1b frequently asks for confirmation despite not being prompted to do so:
- "Just to confirm, you're currently looking for a new job, is that right?"
- "Just to confirm, you're currently employed, is that correct?"
- "Okay, fantastic! Just to confirm, you're currently employed, is that correct?"

**Key Findings:**
- Model exhibits unprompted confirmation-seeking behavior. Although this could be beneficial, it may slow down the onboarding process. Should be evaluated based on user experience goals.

---

## 4. Transcription Accuracy

Tested whether transcriptions are accurate enough for the agent to understand and respond appropriately.

**Name Recognition Issues:**

OpenAI Whisper (local) occasionally misheard "Brendan" during testing:
- Run 5: Transcribed as "Perendin"
- Run 7: Transcribed as "Burndan"
- Other runs: Correct ("Brendan")

**Key Findings:**
- Local OpenAI Whisper struggles with proper nouns, especially less common names.

---

## Summary

**What Worked:**
- Timing metrics successfully capture performance across all pipeline stages
- gemma3:1b generates responses quickly (1.2s on average)
- Error handling works for Ollama connection failures
- Recording and transcription are consistent and fast

**Issues Found:**
- gemma3:1b does not reliably follow the "no emojis" instruction (13.3% failure rate)
- Playback time varies significantly (4-15s) based on response length
- Confirmation-seeking behavior is present without being prompted
- Whisper misrecognizes proper nouns (2 out of 10 runs had name errors)
- gTTS requires internet connection (no offline fallback)

**Next Steps:**
- Add timing metrics to cloud agent (GPT-4) for comparison
- Test with gemma3:4b to evaluate instruction-following improvements
- Consider implementing emoji stripping as a defensive measure
- Evaluate whether to use larger Whisper model (medium/large) for better name recognition
- Explore offline TTS fallback options 
- Decide if confirmation-seeking behavior is intended or if it should be controlled through prompt engineering