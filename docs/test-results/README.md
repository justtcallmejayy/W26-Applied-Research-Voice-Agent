
# Test Results

Integration and performance testing for the voice agent prototype.

Applied Research 1, Winter 2026

---

## Overview

This directory contains manual test reports documenting performance benchmarks, error handling validation, and model comparison studies conducted throughout the project.

Each test report includes:
- Test environment details (hardware, OS, models)
- Detailed results with timing data
- Pass/fail validation of expected behaviors
- Findings and recommendations

---

## Test Reports

| Date | Test Focus | Key Findings |
|------|------------|--------------|
| [2026-02-19](2026-02-19-timing-error-handling.md) | Timing & Error Handling | gemma3:1b: 1.22s generation, 18.8s total/turn; emojis in 13.3% of responses |
| [2026-02-23](2026-02-23-cloud-agent-performance.md) | Cloud Agent Performance | GPT-4: 1.40s generation, 18.6s total/turn; 0% emojis, better transcription (10% vs 20% errors) |

---