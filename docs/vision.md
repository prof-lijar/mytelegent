# Tiny Jarvis - Product Vision

## Overview
Tiny Jarvis is a local personal AI agent designed to handle natural language scheduling for Telegram messages. It allows users to express intent in plain English, which is then parsed into structured data and scheduled for delivery via a Telegram userbot.

## Core Value Proposition
- **Local-First**: Uses a local LLM (Gemma via Ollama) to ensure privacy and reduce latency/cost.
- **Simple Interface**: A CLI that transforms "Tell X tomorrow at Y" into a scheduled event.
- **Reliability**: Uses a persistent SQLite database and a robust scheduler to ensure messages are sent at the correct time.

## Key Capabilities
1. **Natural Language Parsing**: Convert unstructured text into structured JSON (recipient, message, timestamp).
2. **Scheduled Delivery**: Background process that monitors the database and triggers sends.
3. **User Confirmation**: Ensures no message is sent without an explicit confirmation step.
4. **Safety-First Messaging**: Implements delays and retry limits to avoid being flagged as spam by Telegram.

## Tech Stack
- **Language**: Python 3.11+
- **LLM**: Local Gemma via Ollama (OpenAI-compatible API)
- **Validation**: Pydantic v2
- **Storage**: SQLite
- **Scheduling**: APScheduler
- **Telegram API**: Telethon (Userbot)
- **Configuration**: python-dotenv
