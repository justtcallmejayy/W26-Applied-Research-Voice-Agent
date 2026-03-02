
# Test Results: Expanded Onboarding Fields (6 Fields) - Agent Performance Comparison

**Date**: March 2, 2026  
**Tester**: Brendan Dileo  
**Branch**: `feat/expand-onboarding-fields`  
**Operating System**: macOS Sonoma 14.1  
**Hardware**: MacBook Air M2, 8GB RAM  
**Models Tested**: LocalVoiceAgent (gemma3:1b + Whisper base + gTTS), VoiceAgent (GPT-4 + Whisper-1 API + TTS-1)

---

## 1. Test Objective

Validate agent performance after expanding onboarding fields from 2 to 6:
- name
- employment_status
- skills (NEW)
- experience (NEW)
- education (NEW)
- job_preferences (NEW)

Focus areas: prompt adherence, confirmation workflow, field collection accuracy, emoji usage, question order.

---

## 2. Test Execution

### 2.1 Local Agent (gemma3:1b) - 7 Sessions

**Session 1:** Brendan, employed, Excel skills, 3 years experience, data career  
**Session 2:** Brendan, looking for job, Excel skills, 2 years experience, data role  
**Session 3:** Brendan, student, Word/Excel, no experience, high school diploma, data industry  
**Session 4:** User corrected agent for not asking a question  
**Session 5:** Jacob, unemployed, Word/Excel, no experience, high school + diploma, data field  
**Session 6:** Jeremy, "something else" status, Word/Excel, no experience, high school diploma, data industry  
**Session 7:** Agent confusion on question order

### 2.2 Cloud Agent (GPT-4) - 5 Sessions

**Session 1:** Brendan, student, Google Docs, no experience, diploma, data engineer (with confirmation)  
**Session 2:** Brendan, employed at Fortinos, Word/Excel, 2 years, diploma, data engineer (with confirmation)  
**Session 3:** Tommy, student, Word/Excel, no experience, diploma, data field (with confirmation)  
**Session 4:** Agent asked follow-up instead of next field, user corrected  
**Session 5:** Jeremy, student, Python/data technologies, 3 years academic, diploma, data engineer (with confirmation)

---

## 3. Performance Metrics

| Metric | Local Agent (gemma3:1b) | Cloud Agent (GPT-4) |
|--------|-------------------------|---------------------|
| **Total Sessions** | 7 | 5 |
| **Complete Sessions** | 5 (71%) | 5 (100%) |
| **Emoji Violations** | 5/7 (71%) | 0/5 (0%) |
| **Proper Confirmation** | 0/7 (0%) | 5/5 (100%) |
| **Question Order Errors** | 2/7 (29%) | 1/5 (20%) |
| **Average Time/Turn** | 10-15s | 10-15s |

---

## 4. Findings

### 4.1 Emoji Violations (Local Agent - CRITICAL ISSUE)

**Problem:** gemma3:1b ignores "Do not use emojis" instruction

**Frequency:** 5/7 sessions (71% violation rate)

**Examples:**
```
Session 1: "Hi there! Welcome... Let's begin with a few quick questions. 😊"
Session 1: "Great to meet you, Brendan! 😊"
Session 3: "That's fantastic! Those are definitely valuable skills. 😊"
Session 6: "Excellent! The data industry is a really exciting field. 👍"
```

**Cloud Agent:** 0/5 sessions with emojis (100% adherence)

---

### 4.2 Confirmation Workflow

**Cloud Agent - Working Correctly:**

All 5 sessions ended with proper confirmation reading back all 6 fields:
```
Session 1: "Let me summarize the information:
- Name: Brendan
- Employment Status: Student
- Skills: Proficiency in Google Docs
- Experience: Limited to academic experiences
- Education: High school diploma, currently pursuing further education
- Job Preferences: Interested in becoming a Data Engineer

Did I get everything correct?"
```

**Local Agent - NOT Working:**

0/7 sessions with proper confirmation. Issues observed:

Session 5:
```
"Fantastic! That's a great starting point. Just to confirm, 
is that a role you're actively seeking, or are you still exploring options?"
```
Asked meta-question instead of confirming collected data

Session 6:
```
"Alright, no problem at all... Would you prefer to share a bit about 
your preferred work environment – for example, a team setting or 
more independent work?"
```
Asked follow-up question instead of reading back fields

---

### 4.3 Question Order Confusion

**Local Agent - Session 4:**
```
Turn 6: User says "You didn't ask me a question"
Agent response: "You are absolutely right! My apologies. Let's start over. 
Could you tell me your name?"
```
Agent lost track and tried to restart from beginning

**Local Agent - Session 7:**
```
Agent asked about work experience details instead of moving to job preferences
User: "I thought you were going to ask me about job preferences"
Agent: "You're right! My apologies. Let's start with the basics – 
what type of role or industry are you most interested in?"
```
Agent went off-script but recovered

**Cloud Agent - Session 4:**
```
Agent asked about degree details instead of job preferences
User: "You were supposed to ask me about job preferences"
Agent: "My apologies for the mix-up... Let's talk about your job 
preferences then. What type of role or industry are you interested in?"
```
One instance, but agent recovered gracefully

---

### 4.4 Field-Specific Issues

**Experience Field - Ambiguity:**

Multiple interpretations observed:
- "I don't have much professional experience beyond school"
- "I have about three years of experience in a professional set"
- "I don't have any professional experience, but this is my third year"
- "I've worked at Fortinos for two years, but I don't have much professional experience"

**Issue:** Prompt doesn't clarify if academic experience counts as experience

**Job Preferences - Scope Creep:**

Agents sometimes ask follow-up questions beyond just collecting the field:

Session 2 (Local): "Just to confirm, is that a role you're actively seeking, or are you still exploring options?"

Session 6 (Local): "Would you prefer to share a bit about your preferred work environment?"

Session 4 (Cloud): "Can you tell me more about the degree you're pursuing?"

---

## 5. Timing Analysis

**Local Agent:**
- Record: ~5.2s (consistent)
- Transcribe: 0.74-0.94s
- Generate: 0.91-1.72s
- TTS: 0.48-2.66s
- Playback: 6-16s
- **Total per turn:** ~10-15s

**Cloud Agent:**
- Record: ~5.2s (consistent)
- Transcribe: 0.84-7.00s (high variance)
- Generate: 1.02-3.43s
- TTS: 1.96-8.96s
- Playback: 5-33s
- **Total per turn:** ~10-15s (can spike to 30s on confirmation)

**Note:** Confirmation turn takes significantly longer due to reading all 6 fields

---

## 6. Transcription Accuracy

Both agents handled various input patterns well:

**Handled Correctly:**
- "My name is Brendan" → captured properly
- "I'm currently employed" → captured properly
- "Microsoft Word and Microsoft Excel" → captured properly
- "I want to be a data engineer" → captured properly

**Minor Errors:**
- "Microsoft X" (cut off) → "Microsoft Word and Microsoft X"
- "Fortinos" → "14-0's" (phonetic misinterpretation)
- "diploma program" → "diploma" (truncated)
- "data rule" → should be "data role"

---

## 7. Summary

### What Works:

**Both Agents:**
- Successfully collect all 6 fields in majority of sessions
- Reasonable timing (~10-15s per turn)
- Handle various user responses appropriately
- No crashes or major errors

**Cloud Agent Specifically:**
- 100% completion rate (5/5 sessions)
- 0% emoji violations (perfect adherence)
- 100% proper confirmation workflow
- Professional, concise responses

### What Needs Improvement:

**Local Agent:**
- **71% emoji violation rate** - gemma3:1b doesn't follow "no emoji" instruction
- **0% proper confirmation** - never reads back all fields correctly
- **29% question order errors** - loses track of conversation flow
- Occasional rambling responses

**Both Agents:**
- Experience field ambiguity (academic vs professional)
- Job preferences scope creep (agents ask follow-ups)
- 20-30% rate of going off-script

### Recommendations:

1. **Strengthen emoji prohibition** in system prompt with explicit examples
2. **Add mandatory confirmation format** with exact template to follow
3. **Clarify experience field** guidance (accept academic or professional)
4. **Limit job preferences scope** (no follow-up questions allowed)
5. **Consider switching local LLM** if gemma3:1b can't follow emoji instruction

---

## 8. Interim Report Status

**Cloud Agent:** Demo-ready for interim presentation  
**Local Agent:** Needs prompt improvements before production use

Both agents successfully demonstrate 6-field onboarding capability. Cloud agent shows production-quality performance. Local agent requires prompt engineering refinements to match cloud agent's adherence to instructions.