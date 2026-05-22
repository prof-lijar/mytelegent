# Tiny Jarvis Product Specification

## Technical Requirements

**Core Stack**:
- Python 3.11+
- Pydantic for data validation
- SQLite for local storage
- APScheduler for task scheduling
- Telethon for Telegram integration
- Ollama/OpenAI-compatible LLM (Gemma 2B/7B)
- python-dotenv for config management

**Safety Requirements**:
- No mass messaging (1 command = 1 message)
- 2-5s random delay before sends
- Max 2 retries per message
- No logging of Telegram API keys
- Explicit user confirmation required

## System Architecture

```
[CLI] → [LLM Parser] → [Pydantic Validation] → [SQLite Storage] → [Scheduler] → [Telegram Send]
```

1. **CLI Interface**: Accepts natural language commands
2. **LLM Parser**: Uses local Gemma model via Ollama to extract structured JSON
3. **Validation Layer**: Pydantic models enforce schema
4. **Storage**: SQLite database tracks scheduled messages
5. **Scheduler**: APScheduler triggers at specified times
6. **Telegram**: Telethon userbot sends messages with delay

## Module Breakdown

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| config | Load .env variables | python-dotenv |
| models | Pydantic schemas |  |
| db_tool | SQLite CRUD operations |  |
| llm_tool | Ollama API wrapper |  |
| parser | NLP → structured JSON | llm_tool, models |
| telegram_tool | Telethon send with delay |  |
| scheduler | APScheduler background loop | db_tool |
| cli | Main entry point | parser, scheduler |
| logging | Activity/error logs |  |

## Development Phases

1. **Discovery** (Complete)
2. **Architecture**: Design patterns, directory structure
3. **Development**: Module implementation
4. **Quality**: Testing, PR reviews
5. **Iteration**: Refinement, new features

## Acceptance Criteria
- All modules must have unit tests
- End-to-end test with mock Telegram
- 100% test coverage for critical paths
- No security vulnerabilities in dependencies