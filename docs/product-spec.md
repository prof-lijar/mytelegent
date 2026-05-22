# Tiny Jarvis Product Specification

## Technical Architecture

### Core Components
1. **CLI Interface** - Command-line entry point for user interaction
2. **LLM Parser** - Local Gemma model via Ollama for NLP parsing
3. **Validation Engine** - Pydantic models for structured data validation
4. **Persistence Layer** - SQLite database for scheduled messages
5. **Scheduler** - APScheduler background worker for timing
6. **Telegram Client** - Telethon userbot for message delivery
7. **Config System** - python-dotenv for environment variables

### Module Dependency Diagram
```mermaid
graph TD
    CLI --> Parser
    Parser --> Validator
    Validator --> Scheduler
    Scheduler --> DB
    Scheduler --> Telegram
    DB <-- Config
    Telegram <-- Config
```

## API Requirements

### Public CLI API
- `jarvis schedule <message>` - Schedule a new message
- `jarvis list` - Show pending messages
- `jarvis cancel <id>` - Cancel a scheduled message

### Internal APIs
- `parse_command(text: str) -> ParsedCommand`
- `validate_command(command: ParsedCommand) -> ValidatedCommand`
- `schedule_message(command: ValidatedCommand) -> MessageID`

## Security Constraints
1. **Data Encryption**: All message content stored in DB with AES-256
2. **Secret Management**: Telegram API hash stored in environment variables
3. **Rate Limiting**: Max 1 message per 30 seconds to prevent spam
4. **Retry Limits**: Max 2 retries with exponential backoff
5. **Audit Logging**: All actions logged to `activity.log` with timestamps

## Safety Requirements
- Random 2-5s delay before sending messages
- User confirmation required before scheduling
- Never send messages without explicit approval
- All tests must use mocked Telegram and LLM interfaces