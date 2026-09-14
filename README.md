# Proxy

An AI agent that completes real, multi-step web tasks on a user's behalf — with a security layer that detects and blocks prompt-injection attempts hidden in page content before it can hijack the agent, and a human-gated flow for sensitive fields (SSN, DOB, account numbers) that keeps those values out of the AI's context entirely.

Built for the AI Builders Hackathon 2026.

## What it does

Give Proxy a plain-language task (e.g. "Complete the housing benefits application") and it will:

1. Read the real page and decide its next action dynamically — no fixed script
2. Show a split-screen view: your conversation with the agent on the left, a live view of the actual page on the right
3. Pause for your approval before high-consequence actions (like submitting a form)
4. Pause and ask *you* to type sensitive fields (SSN, DOB, account numbers) directly — the AI never sees or stores that value
5. Detect and block indirect prompt injection hidden in page content (invisible text, white-on-white styling, malicious alt attributes) before it can manipulate the agent

## Session-first workflow

Proxy starts at `frontend/session.html`. The user enters ordinary profile
details once for the active session, then continues to the live split-screen
agent. Sensitive values such as date of birth and SSN are never collected on
the session page. They are requested directly only when the live form needs
them.

Starting a new session creates a fresh in-memory profile and clears the
previous session context.

## Architecture

```
Frontend (split-screen UI)
        │  WebSocket / REST
Backend (FastAPI)
        │
Agent loop: Perceive → Reason → Gate → Execute → Observe
        │
Real browser (Playwright + Chromium)
```

Every proposed action passes through a policy gate (allowlist + injection scanner) before it's allowed to execute. See `THREAT_MODEL.md` and `ARCHITECTURE_OVERVIEW.md` for the full design.

## Setup

```bash
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env   # add provider keys
```

## Run

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/app/session.html` to start a session.

After saving the profile, Proxy opens the main task view at
`http://127.0.0.1:8000/app/index.html`.

Reasoning providers run in this order: Groq, Gemini, then local Ollama. If all providers are unavailable, the demo uses synthetic non-sensitive values; DOB and other sensitive fields remain human-only and never enter provider context.

**Windows:** don't use `--reload` — see `backend/main.py` for why (a Playwright/asyncio event-loop compatibility issue).

## Demo flow

1. Start a session and save ordinary demo details.
2. Choose **Normal application** and start the housing-benefits task.
3. Enter the requested sensitive demo values directly when Proxy pauses.
4. Approve the final submission when the approval card appears.
5. Run **Attack demo** to show Proxy blocking hidden page instructions.

Use demo values only. Never record or commit real personal information.

The repository thumbnail is available at `proxy-thumbnail.png`, and the
recommended narration is in `DEMO_SCRIPT_FINAL.md`.

## Project structure

```
agent/          agent loop, reasoning, browser automation
policy/         security gate, injection scanner, PII field handling
backend/        FastAPI server, WebSocket streaming, audit log
frontend/       task runner UI + case-worker dashboard
demo-sites/     clean and injection-seeded demo forms
eval/           tests and standalone demo/verification scripts
```

## Tests

```bash
pytest eval/test_gate.py eval/test_pii.py -v
```
