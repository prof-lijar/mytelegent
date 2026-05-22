# System Architecture - Tiny Jarvis

## 1. System Overview
Tiny Jarvis is a local-first AI agent for scheduling Telegram messages. It follows a decoupled architecture where the **CLI (main.py)** handles intent capture and the **Scheduler (run_scheduler.py)** handles execution.

### Data Flow
1. **User Input** $\rightarrow$ `main.py` (CLI)
2. `main.py` $\rightarrow$ `agents/parsing_agent.py` (using `tools/local_llm_tool.py`)
3. `parsing_agent.py` $\rightarrow$ `schemas/models.py` (Validation)
4. `main.py` $\rightarrow$ User (Confirmation)
5. `main.py` $\rightarrow$ `tools/db_tool.py` (Save to SQLite)
6. `run_scheduler.py` $\rightarrow$ `agents/scheduler_agent.py` (Polling DB)
7. `scheduler_agent.py` $\rightarrow$ `tools/telegram_tool.py` (Send via Telethon)
8. `telegram_tool.py` $\rightarrow$ `tools/db_tool.py` (Update status to 'sent')

## 2. Module Breakdown

### Agents (`/agents`)
- **Parsing Agent**: Converts NL to JSON. Uses `local_llm_tool` and `refiner_agent` for repair.
- **Scheduler Agent**: The brain of the background process. Manages the APScheduler jobs.
- **Refiner Agent**: Specifically handles JSON repair if the first pass fails.

### Tools (`/tools`)
- **Config**: Loads `.env` variables.
- **Local LLM Tool**: OpenAI-compatible client for Ollama.
- **DB Tool**: SQLite wrapper for the `scheduled_messages` table.
- **Telegram Tool**: Telethon wrapper for sending messages.
- **Time Tool**: Utilities for Asia/Seoul timezone handling.
- **Logging Tool**: Dual-file logging (activity vs errors).

### Schemas (`/schemas`)
- **Models**: Pydantic definitions for `ParsedMessageCommand` and `ScheduledMessage`.

### Prompts (`/prompts`)
- **Parsing Prompt**: System prompt for NL $\rightarrow$ JSON.
- **Refiner Prompt**: System prompt for JSON repair.

## 3. File Structure
```
product-repo/
├── agents/
│   ├── __init__.py
│   ├── parsing_agent.py
│   ├── scheduler_agent.py
│   └── refiner_agent.py
├── tools/
│   ├── __init__.py
│   ├── config.py
│   ├── local_llm_tool.py
│   ├── db_tool.py
│   ├── telegram_tool.py
│   ├── time_tool.py
│   └── logging_tool.py
├── schemas/
│   └── models.py
├── prompts/
│   ├── parsing_prompt.md
│   └── refiner_prompt.md
├── database/
├── logs/
├── tests/
│   ├── test_models.py
│   ├── test_db.py
│   ├── test_parser.py
│   └── test_scheduler.py
├── main.py
├── run_scheduler.py
├── pyproject.toml
├── .env.example
└── .gitignore
```

## 4. Tech Stack & Versions
- **Python**: 3.11+
- **LLM**: Gemma (via Ollama)
- **Database**: SQLite
- **Scheduling**: APScheduler 3.x
- **Telegram**: Telethon
- **Validation**: Pydantic v2
- **Package Manager**: uv

## 5. Security & Reliability
- **Timezone**: All operations locked to `Asia/Seoul`.
- **SQL**: Parameterized queries only.
- **Telegram**: Random delay (2-5s) between sends to prevent spam detection.
- **Confirmation**: Mandatory user `Y/N` before DB insertion.
- **Secrets**: `.env` file excluded from git; `.env.example` provided.
