
# Test Results: OpenRouter LLM Engine Integration

**Date**: March 25, 2026
**Tester**: Brendan Dileo
**Branch**: `feat/openrouter-llm-engine`
**Operating System**: macOS Sonoma 14.1
**Hardware**: MacBook Air M2, 8GB RAM
**Models Tested**: Multiple free models via OpenRouter API

---

## 1. Background
Following the plug-and-play pipeline implementation, this test validates that a third-party LLM provider (OpenRouter) can be integrated by creating a single engine file and updating one line in config.py, with no changes to `pipeline.py`, `main.py`, or `dashboard.py`.

OpenRouter provides access to a wide range of LLM models through a single OpenAI compatible API endpoint. The client requested OpenRouter integration to enable flexible model testing and comparison without requiring separate API integrations for each provider.

This test documents all free models available on OpenRouter as of March 25, 2026, and identifies which ones are compatible with the pipeline's system prompt requirements.

---

## 2. Integration Changes
- Created `core/engines/llm/openrouter_llm.py`, implementing `LLMEngine` using the OpenAI SDK with OpenRouter's base URL
- Added `OPENROUTER_API_KEY` to `.env`
- Added `OPENROUTER_FREE_MODELS` dict and `OPENROUTER_MODEL` to `config.py`
- Updated `ENGINES` dict in `config.py` to use OpenRouterLLMEngine
- No changes made to pipeline.py, main.py, or dashboard.py

This validates the plug-and-play architecture, a new LLM provider was fully integrated with one new file and one line change in config.py.

---

## 3. Test Execution
Each model was tested by starting a session and observing whether the opening response was generated successfully. A model is marked as working if it returned a valid text response from the pipeline 

Generation time is recorded from the log for working models.
Models were tested using the OpenRouter engine set:
```
STT: WhisperAPIEngine
LLM: OpenRouterLLMEngine
TTS: OpenAITTSEngine
```

---

## 4. Model Compatibility Results

### 4.1 Confirmed Working
 
| Model | Generation Time | Notes |
|-------|----------------|-------|
| `stepfun/step-3.5-flash:free` | 10.45s | Slower but reliable |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 0.95s | Fastest confirmed working |
| `nvidia/nemotron-3-super-120b-a12b:free` | 1.23s – 3.04s | Consistent across two runs |
| `z-ai/glm-4.5-air:free` | 4.70s | Reliable |
| `liquid/lfm-2.5-1.2b-instruct:free` | 0.40s | Fastest overall |
| `arcee-ai/trinity-large-preview:free` | 1.77s | Reliable |

### 4.2 Failed — Rate Limited (429)
 
Models exist and are functional but were temporarily unavailable on the free tier due to upstream rate limiting via Venice provider. These may work at a different time or with a paid account.
 
| Model | Provider | Notes |
|-------|----------|-------|
| `meta-llama/llama-3.3-70b-instruct:free` | Venice | Rate limited |
| `mistralai/mistral-small-3.1-24b-instruct:free` | Venice | Rate limited |
| `qwen/qwen3-next-80b-a3b-instruct:free` | Venice | Rate limited |
| `qwen/qwen3-4b:free` | Venice | Rate limited |
| `nousresearch/hermes-3-llama-3.1-405b:free` | Venice | Rate limited |
| `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | Venice | Rate limited |
| `google/gemma-3-12b-it:free` | Google AI Studio | Rate limited |
| `google/gemma-3-27b-it:free` | Google AI Studio | Rate limited |
 
### 4.3 Failed — System Prompt Not Supported (400)
 
Google AI Studio does not support system prompts (developer instructions) on any of its free models. Since the pipeline relies on a system prompt to guide the agent's behaviour, all Google AI Studio models are incompatible with the current pipeline.
 
| Model | Provider | Error |
|-------|----------|-------|
| `google/gemma-3-4b-it:free` | Google AI Studio | Developer instruction is not enabled |

### 4.4 Failed — Empty LLM Response (TTS 400)
 
These models connected successfully and returned a response, but the response content was `None` or an empty string. The empty string was passed to OpenAI TTS which threw "Field required" and crashed the session. This is the known empty LLM response bug tracked in Issue #33.
 
| Model | Generation Time | LLM Response | Error |
|-------|----------------|--------------|-------|
| `nvidia/nemotron-nano-9b-v2:free` | 6.09s | `'None'` | TTS 400 — no input |
| `nvidia/nemotron-nano-12b-v2-vl:free` | 3.60s | `'None'` | TTS 400 — no input |
| `liquid/lfm-2.5-1.2b-thinking:free` | — | Empty | TTS 400 — no input |
| `arcee-ai/trinity-mini:free` | — | Empty | TTS 400 — no input |

### 4.5 Failed — Privacy Policy / No Endpoint (404)
 
These models are blocked by OpenRouter account data policy settings. Configuring privacy settings at openrouter.ai/settings/privacy may resolve these.
 
| Model | Error |
|-------|-------|
| `minimax/minimax-m2.5:free` | No endpoints matching data policy |
| `openai/gpt-oss-120b:free` | No endpoints matching data policy |
| `openai/gpt-oss-20b:free` | No endpoints matching data policy |

---

## 5. Summary
 
| Result | Count | Models |
|--------|-------|--------|
| Working | 6 | stepfun-flash, nemotron-30b, nemotron-120b, glm-4.5-air, lfm-instruct, trinity-large |
| Rate limited (429) | 8 | llama-3.3, mistral-small, qwen3-next, qwen3-4b, hermes-405b, dolphin-mistral, gemma-3-12b, gemma-3-27b |
| System prompt not supported (400) | 1 | gemma-3-4b |
| Empty response → TTS crash (400) | 4 | nemotron-9b, nemotron-12b, lfm-thinking, trinity-mini |
| Privacy policy block (404) | 3 | minimax-m2.5, gpt-oss-120b, gpt-oss-20b |
| **Total tested** | **22** | |
 
---

## 6. Findings
 
### 6.1 Plug-and-Play Validated with Third-Party Provider
The OpenRouter integration required one new engine file (`openrouter_llm.py`) and one line change in `config.py`. No changes were made to `pipeline.py`, `main.py`, or `dashboard.py`. This confirms the plug-and-play architecture works as designed for LLM provider swapping.
 
### 6.2 Six Free Models Confirmed Working
Six free models are confirmed compatible with the pipeline as of March 25, 2026. These are documented in `config.py` as `OPENROUTER_FREE_MODELS` for easy reference and swapping.
 
### 6.3 Google AI Studio Models Incompatible
All Google AI Studio models either failed with a system prompt error or were rate limited. Google AI Studio does not support developer instructions on free tier models, making them incompatible with any pipeline that uses a system prompt.
 
### 6.4 Empty LLM Response Bug Exposed by Four Models
Four models returned `None` or an empty string instead of a valid response. The empty string was passed directly to OpenAI TTS which crashed the session.
 
### 6.5 Rate Limited Models May Work Later
Eight models failed with 429 rate limiting via the Venice provider. These models are functional but the free tier is heavily shared. They may work at off-peak times or with a paid OpenRouter account.
 
### 6.6 Privacy Policy Blocks Three Models
Three models returned 404 due to OpenRouter account data policy restrictions. These can potentially be unblocked by configuring privacy settings at openrouter.ai/settings/privacy.
 
---
 
## 7. Issues Identified
 
**Issue 1 — Empty LLM response crashes pipeline via TTS**
Four models returned `None` or empty string responses which were passed directly to OpenAI TTS, crashing the session. The pipeline needs a guard in `pipeline.py` to check for empty responses before passing to TTS.
 
**Issue 2 — Google AI Studio models incompatible with system prompt**
All Google AI Studio free models either block system prompts entirely or are rate limited. These models cannot be used with the current pipeline design. Need to exclude Google AI Studio models from the confirmed working list and documenting this limitation for the client.
 
**Issue 3 — Free tier rate limiting is unreliable**
Eight models were rate limited during testing. The Venice provider rate limits are shared across all free OpenRouter users making free tier testing inconsistent. Models that fail today may work tomorrow.
