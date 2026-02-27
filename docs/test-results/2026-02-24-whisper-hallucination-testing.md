
# Test Results: Whisper Hallucination Detection & Validation

**Date**: February 24, 2026  
**Tester**: Brendan Dileo  
**Branch**: `fix/empty-audio-validation`  
**Operating System**: macOS Sonoma 14.1  
**Hardware**: MacBook Air M2, 16GB RAM  
**Models Tested**: Whisper-1 (OpenAI API), GPT-4

---

## 1. Exploratory Testing - Whisper Hallucinations

During cloud agent performance testing, discovered that mic permission denial 
doesn't skip turns properly. Whisper API returns garbage transcripts for silence 
instead of empty strings.

**Issue Flow:** Mic denied → Records silence → Whisper returns 'you\n' → Agent continues with bad data

---

Tested various non-speech inputs to understand Whisper behaviour better:

| Input Type | Transcription | Expected | Actual Behavior |
|------------|--------------|----------|-----------------|
| Complete silence (mic off) | Empty string | Skip turn | Returns `'you\n'` - continues|
| Silence (no speech) | Empty string | Skip turn | Returns `'Thank you so much for watching !'`|
| Cough | Empty/noise | Skip turn | Returns `'Bye bye.'`|
| Background noise | Empty/noise | Skip turn | Returns `'. .'`|

**Key Finding:** Whisper-1 hallucinates common phrases from training data when given silence or non-speech audio.

**Common Hallucinations Observed:**
- "Thank you so much for watching", "Bye bye", "Please subscribe", ". ."
- "Oh! POOF! POOF! POOF!", "C'MON CAN'T U JUST"
- "ご視聴ありがとうございました" (Thank you for watching), "完成" (Done)

---

## 2. Fix Implementation

**Solution:** Detecting audio energy before transcribing user text.
*Reference: https://community.openai.com/t/hallucination-on-audio-with-no-speech/324010*

---

## 3. Validation Testing

### 3.1 Mic Disabled (Complete Silence) - 6 Runs

**Setup:** Microphone permission explicitly denied in System Settings

| Run | Audio Energy | Result |
|-----|--------------|--------|
| 1-6 | 0.0000 | All skipped |

**Result:** 100% success rate - no API calls made, no hallucinations

### 3.2 Mic On, No Speech (Ambient Noise) - 8 Runs

**Setup:** Microphone enabled, no speech, only ambient room noise

| Run | Audio Energy | Result |
|-----|--------------|--------|
| 1 | 0.0007 | Skipped |
| 2 | 0.0008 | Skipped |
| 3 | 0.0007 | Skipped |
| 4 | 0.0009 | Skipped |
| 5 | 0.0006 | Skipped |
| 6 | 0.0008 | Skipped |
| 7 | 0.0010 | Skipped |
| 8 | 0.0012 | Skipped |

**Result:** 100% success rate - ambient noise properly filtered  
**Energy Range:** 0.0006 - 0.0012

### 3.3 Background Noise & Edge Cases - 15 Runs

**Setup:** Various non-speech audio inputs

| Input Type | Audio Energy | Transcription | Result |
|------------|--------------|---------------|--------|
| Cough | 0.0133 | "Bye bye." | Hallucination |
| Cough | 0.0138 | Response in Chinese | Hallucination |
| Cough | 0.0197 | "Bye bye." | Hallucination |
| Music | 0.0236 | Response in Korean | Hallucination |
| Game Audio | 0.0138 | "C'MON CAN'T U JUST" | Hallucination |
| Keyboard | 0.0086 | - | Skipped |
| Keyboard | 0.0065 | - | Skipped |
| Light noise | 0.0106 | "\n" | Edge case |
| Background | 0.0150 | "Oh! POOF! POOF! POOF!" | Hallucination |
| **Speech: "Hi"** | 0.0157 | "Hi." | Valid |
| **Speech: "Hey"** | 0.0156 | "Hey." | Valid |

**Energy Ranges:**
- Complete silence: 0.0000
- Ambient noise: 0.0006 - 0.0012
- Light movement: 0.0065 - 0.0086
- **Threshold:** 0.01
- Loud noise/coughs: 0.0133 - 0.0236
- Valid speech: 0.0150+

**Findings:**
- Energy check filters true silence (0.0000 - 0.0012)
- Coughs/loud background noise still transcribed, leading to hallucinations
- Cannot distinguish cough from quiet speech based on energy alone

---

## 4. Summary

**What's Fixed:**
- Mic permission denial properly skipped (100% success)
- True silence detection working (100% success)
- API cost savings (no wasted calls on silence)

**Limitations:**
- Cough/loud background noise still causes hallucinations (energy > 0.01)
- May require additional filtering of common halucinated phrases
- Requires Voice Activity Detection for full solution (out of scope)