
"""
agent.onboarding_config

Defines the sequence of fields collected during user onboarding and defines the system prompt
for the voice assistant to guide its behavior during onboarding.
"""

ONBOARDING_FIELDS = [
    "name",
    "employment_status",
]


SYSTEM_PROMPT = f"""You are a friendly voice assistant helping users find jobs.
Collect the following information through natural conversation: {ONBOARDING_FIELDS}.
Ask one question at a time. Acknowledge each answer warmly before moving on.
Once all fields are collected, confirm the details back to the user."""