
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
| [2026-02-24](2026-02-24-whisper-hallucination-testing.md) | Whisper Hallucination Bug Fix | Audio energy detection (threshold: 0.01) fixes silent audio hallucinations; 100% success on 14 runs |
| [2026-03-02](2026-03-02-expanded-fields-testing.md) | 6-Field Onboarding Testing | Cloud: 100% completion, 0% emojis; Local: 71% completion, 71% emoji violations; both ~10-15s/turn |
| [2026-03-02](2026-03-02-local-agent-baseline.md) | Dashboard UI, Edge Cases & Debug Panel | Core dashboard workflow stable; runtime log disconnect identified; progress bar off-by-one found |
| [2026-03-03](2026-03-03-dashboard-functional-smoke.md) | Dashboard Functional Smoke Test | All config controls and session lifecycle pass; ~2s recording overhead noted; Record button feedback delay (minor UX) |
| [2026-03-10](2026-03-10-local-agent-prompt-improvements.md) | Local Agent Prompt Improvements | Emoji violations fixed (71% -> 0%) via positive constraints; order errors worsened (29% -> 55%); confirmation workflow (0%) requires pipeline-level fix |
| [2026-03-11](2026-03-11-cloud-agent-prompt-validation.md) | Cloud Agent Updated Prompt Validation | No regressions on updated prompt; GPT-4 holds 100% across all metrics; confirms remaining local failures are model-scale issues |

---