"""
scripts.stress_test_sprints

Automates the 'Session Sprints' methodology: Runs 10 consecutive 6-field 
onboarding sessions using gemma3:4b to measure latency drift and model stability.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path

# Add src/app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "app"))

from agent.local_voice_agent import LocalVoiceAgent
from agent.onboarding_config import ONBOARDING_FIELDS

# Configuration
TEST_MODEL = "gemma3:4b"
NUM_SESSIONS = 10
OUTPUT_FILE = "docs/test-results/stress_test_results.json"

# Ground Truth Answers to ensure consistent LLM load
SCRIPTED_ANSWERS = [
    "My name is Robert Perkins.",
    "I am currently a student looking for full-time work.",
    "I have skills in Python, Java, and SQL.",
    "I have 2 years of experience in academic projects and one internship.",
    "I have a Bachelor of Science in Computer Science.",
    "I am looking for software developer roles in Toronto."
]

def run_stress_test():
    print(f"Starting Stress Test: {NUM_SESSIONS} Sessions with {TEST_MODEL}")
    
    # Initialize Agent (once, to simulate sustained usage)
    agent = LocalVoiceAgent(
        recording_duration=5,
        sample_rate=16000,
        whisper_model="base",
        ollama_model=TEST_MODEL,
        ollama_timeout=180,
        ollama_keep_alive="1h",
    )
    
    results = []

    for session_num in range(1, NUM_SESSIONS + 1):
        print(f"\n--- Starting Session {session_num}/{NUM_SESSIONS} ---")
        session_data = {"session": session_num, "turns": []}
        
        # Reset agent conversation history for a new session
        agent.conversation_history = []
        
        # Initial greeting
        start_time = time.time()
        agent.generate_response("Begin the onboarding conversation.")
        greeting_latency = time.time() - start_time
        print(f"Initial Greeting Latency: {greeting_latency:.2f}s")

        for i, field in enumerate(ONBOARDING_FIELDS):
            user_input = SCRIPTED_ANSWERS[i]
            
            print(f"Turn {i+1} ({field}): Processing...")
            
            # Measure LLM Inference Latency
            start_inference = time.time()
            response = agent.generate_response(user_input)
            latency = time.time() - start_inference
            
            session_data["turns"].append({
                "field": field,
                "latency": latency,
                "history_length": len(agent.conversation_history)
            })
            
            print(f"   Latency: {latency:.2f}s")

        results.append(session_data)

    # Save results for analysis
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=4)
    
    analyze_results(results)

def analyze_results(results):
    first_session_avg = sum(t["latency"] for t in results[0]["turns"]) / 6
    last_session_avg = sum(t["latency"] for t in results[-1]["turns"]) / 6
    drift = ((last_session_avg - first_session_avg) / first_session_avg) * 100

    print("\n" + "="*40)
    print("STRESS TEST SUMMARY")
    print("="*40)
    print(f"First Session Avg Latency: {first_session_avg:.2f}s")
    print(f"Last Session Avg Latency:  {last_session_avg:.2f}s")
    print(f"Latency Drift:            {drift:+.2f}%")
    
    if abs(drift) <= 15:
        print("\n SUCCESS: Drift is within +/- 15% tolerance.")
    else:
        print("\nWARNING: Significant performance degradation detected.")
    print("="*40)

if __name__ == "__main__":
    try:
        run_stress_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nTest failed: {e}")