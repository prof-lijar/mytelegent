# System Architecture

## Overview

tiny-jarvis uses a modular microservices architecture with three core agent types:

1. **Parsing Agent** - Converts natural language to structured JSON via local Gemma LLM
2. **Scheduler Agent** - Manages APScheduler for time-based message delivery
3. **Refiner Agent** - Reparses failed commands with context-aware repair prompt

![Data Flow](https://via.placeholder.com/600x300?text=NL+Input+→+Parsing+→+Validation+→+Scheduling+→+Telegram+Delivery)

## Module Breakdown

| Module        | Responsibility                          | Key Components                   |
|---------------|------------------------------------------|----------------------------------|
| agents/       | Business logic orchestration             | parsing_agent.py, scheduler_agent.py |
| tools/        | Infrastructure integration                | telegram_tool.py, db_tool.py      |
| schemas/      | Data validation and typing               | models.py                       |
| database/     | Persistent storage                        | SQLite                          |

## File Structure
```
project-root/
├── agents/               # Core processing agents
├── tools/                # Infrastructure utilities
├── schemas/              # Data validation models
├── database/             # SQL database files
├── logs/                 # Activity and error logs
├── main.py               # CLI entry point
├── run_scheduler.py      # Background scheduler
└── pyproject.toml        # Dependency management
```

## Tech Stack
- **LLM**: Gemma (local via Ollama) + OpenAI API compatibility
- **Scheduling**: APScheduler 3.x with SQLite persistence
- **Messaging**: Telethon for Telegram bot API
- **Validation**: Pydantic v2 for strict data modeling
- **Storage**: SQLite with type-affine schema

## Security Considerations
1. All credentials stored in .env file (gitignored)
2. Telegram API keys never hardcoded
3. LLM responses validated against Pydantic models
4. Scheduler runs with minimal permissions

## Timezone Handling
All operations use Asia/Seoul timezone (KST) with ISO-8601 format for:
- User input parsing
- Database storage
- Message delivery execution