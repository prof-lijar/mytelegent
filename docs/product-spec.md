# Tiny Jarvis - Product Specification

## 1. System Overview
Tiny Jarvis is a Python CLI application that allows users to schedule Telegram messages using natural language. It leverages a local LLM to parse intent and a background scheduler to execute the send.

## 2. Functional Requirements
- **NL Command Parsing**: The system must take a string input and extract:
    - Recipient (Name or Username)
    - Message content
    - Scheduled time (Absolute or Relative)
- **Confirmation Workflow**: The CLI must present the parsed intent to the user and require a `Y/N` confirmation before saving to the database.
- **Scheduled Execution**: A background process must run independently of the CLI to send messages at the designated time.
- **Persistence**: All scheduled messages must be stored in a SQLite database.
- **Telegram Integration**: Messages are sent via a Telegram Userbot (Telethon).

## 3. Detailed Module Requirements

### 3.1 Config Loader (`tools/config.py`)
- Load environment variables from `.env` using `python-dotenv`.
- Required variables: `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`.

### 3.2 Pydantic Models (`schemas/models.py`)
- `ParsedMessageCommand`: Schema for the LLM output (recipient, message, scheduled_time).
- `ScheduledMessage`: Schema for the database record (id, recipient, message, scheduled_time, status, created_at).

### 3.3 SQLite Tool (`tools/db_tool.py`)
- CRUD operations for `scheduled_messages` table.
- Methods: `add_message`, `get_pending_messages`, `update_message_status`.

### 3.4 Local LLM Tool (`tools/local_llm_tool.py`)
- Client to communicate with Ollama/OpenAI-compatible API.
- Method to send a prompt and receive a JSON response.

### 3.5 Parsing Agent (`agents/parsing_agent.py`)
- Orchestrates the prompt to the LLM.
- Validates the LLM output against the `ParsedMessageCommand` Pydantic model.
- Handles retry/error logic if the LLM returns invalid JSON.

### 3.6 Telegram Tool (`tools/telegram_tool.py`)
- Wrapper around Telethon.
- Method `send_message(recipient, text)` that handles the actual API call.

### 3.7 Scheduler Agent (`agents/scheduler_agent.py`)
- Uses APScheduler to check the DB for pending messages.
- Triggers the Telegram tool for messages whose time has arrived.

### 3.8 Main CLI (`main.py`)
- Entry point for the user.
- Flow: Input $\rightarrow$ Parse $\rightarrow$ Confirm $\rightarrow$ Save to DB.

### 3.9 Scheduler Runner (`run_scheduler.py`)
- Entry point to start the background scheduler process.

### 3.10 Logging Tool (`tools/logging_tool.py`)
- Centralized logging to `activity.log` and `errors.log`.

## 4. Safety Rules
- **No Mass Messaging**: Only one message per command.
- **Anti-Spam Delay**: Implement a random delay of 2-5 seconds before each Telegram send.
- **Retry Limit**: Maximum of 2 retries for any failed message send.
- **Explicit Confirmation**: No message is scheduled without user confirmation in the CLI.
- **Secret Protection**: Never log `API_ID`, `API_HASH`, or other secrets.
- **Test Isolation**: All tests must use mocks. Real Telegram messages must never be sent during tests.

## 5. Technical Constraints
- Python 3.11+
- SQLite for local storage.
- Telethon for Userbot functionality.
- Local Gemma model via Ollama.
