# Project Progress

## Current Phase
Iteration — Enhancing CLI capabilities and implementing security constraints.

## What Was Completed This Cycle
- Merged PR #38: [Backend] Implement AES-256 Encryption for Message Storage.

## What Is In Progress
- Issue #37: [Backend] Enhance CLI to support specific command-line arguments (In progress)

## What Is Blocked
- None.

## Next Cycle Plan
- Backend to finalize CLI argument support (Issue #37).
- QA to verify CLI enhancements once implemented.

## Module Checklist
- [x] Config loader (.env, python-dotenv)
- [x] Pydantic models (ParsedMessageCommand, ScheduledMessage)
- [x] SQLite db_tool (CRUD for scheduled_messages)
- [x] Local LLM tool (Ollama/OpenAI-compatible)
- [x] Parsing agent (NL → structured JSON)
- [x] Telegram tool (Telethon send with delay)
- [x] Scheduler agent (APScheduler background loop)
- [x] Main CLI (parse → confirm → schedule)
- [x] Logging (activity.log, errors.log)
- [x] Tests (mocked LLM, mocked Telegram, temp DB)
- [ ] CLI: `list` and `cancel` commands
- [ ] CLI: Command-line argument support (argparse)
- [x] Security: AES-256 encryption for DB messages
