"""
tests.unit.test_pipeline

Unit test related to the OpenRouter API.
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

# Load .env from src/app/
load_dotenv(Path(__file__).parent.parent / "src" / "app" / ".env")

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "google/gemma-3-27b-it:free"
PROMPT  = "Say hello and tell me what model you are."


def check_key(api_key: str) -> dict:
    """ Check API key status and credit balance, if any """
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())


def chat(api_key: str, model: str, prompt: str) -> str:
    """ Send a single chat message and return the response text """
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())

    return data["choices"][0]["message"]["content"]


def main():
    print("=== OpenRouter API Test ===\n")

    # Check key
    print("1. Checking API key...")
    try:
        key_info = check_key(API_KEY)
        print(f"   ✓ Key valid")
        print(f"   Credits remaining : {key_info.get('data', {}).get('limit_remaining', 'N/A')}")
        print(f"   Rate limit        : {key_info.get('data', {}).get('rate_limit', 'N/A')}\n")
    except urllib.error.HTTPError as e:
        print(f"   ✗ Key check failed: {e.code} {e.reason}")
        return

    # Send a test message
    print(f"2. Sending test message to {MODEL}...")
    print(f"   Prompt: \"{PROMPT}\"\n")
    try:
        reply = chat(API_KEY, MODEL, PROMPT)
        print(f"   ✓ Response received:")
        print(f"   {reply}\n")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"   ✗ Request failed: {e.code} {e.reason}")
        print(f"   {body}\n")
        return

    print("=== Test complete ===")


if __name__ == "__main__":
    main()