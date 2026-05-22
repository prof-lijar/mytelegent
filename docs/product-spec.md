# Product Specification

## Core Features

1. **Natural Language Parsing**
   - Input format: `"Tell [Name] [time] that [message]"`
   - Supported time formats: absolute ("May 23 at 3 PM") and relative ("tomorrow at 9 AM")
   - Output format: Structured JSON with `recipient`, `scheduled_time`, `message` fields

2. **Local Processing Stack**
   - Gemma/LLM via Ollama for parsing
   - Pydantic for data validation
   - SQLite for persistent storage

3. **Telegram Integration**
   - Telethon-based userbot
   - Random 2-5s delay before sending
   - Max 2 retries with exponential backoff

4. **Scheduler**
   - APScheduler background task
   - Status tracking (scheduled/pending/failure)

5. **Security**
   - No cloud dependencies
   - Secrets masked in logs
   - Mock-based testing only

## Technical Requirements

- Python 3.11+
- pyproject.toml with exact version pins
- Type hints throughout
- Unit tests for all modules

## Development Phases

1. Architecture design
2. Core module implementation (LLM, DB, Telegram)
3. Scheduler and CLI
4. End-to-end validation
5. Security review

## Success Metrics

- 100% test coverage for critical paths
- Zero Telegram message failures in testing
- 50+ unit tests
- Complete API documentation
- No open P0-critical issues