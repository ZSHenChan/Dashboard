# Telegram Userbot Service

This package contains the worker service for the Personal Dashboard that integrates directly with Telegram. It functions as a "userbot" (running on your personal account) to triage messages, draft replies, and manage your calendar.

## Features

- **Intelligent Message Collection**:
  - Monitors incoming private messages.
  - Implements a customizable **debounce timer (default: 45s)** to batch consecutive messages from the same sender, ensuring the LLM has full context before processing.

- **LLM Processing & Style Mimicry**:
  - Uses Google Gemini to analyze conversation history.
  - Generates summaries and drafts reply options that strictly **mimic the user's tone**, slang, and typing habits (e.g., lowercase, specific regional slang).

- **Event-Driven Architecture**:
  - **Redis Pub/Sub**: Publishes processed message cards to the dashboard.
  - **Command Execution**: Subscribes to `userbot:commands` to execute actions triggered by the user from the dashboard, such as sending the drafted replies via the Telegram API.

- **Calendar Integration**:
  - Automatically identifies scheduling intents within the chat.
  - Adds events to the native OS calendar (via macOS EventKit) upon confirmation.

## Configuration

Set the following environment variables in your `.env` file:

```bash
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
GEMINI_API_KEY=your_gemini_key
REDIS_URL=localhost
REDIS_PORT=6379
REDIS_PASSWORD=optional
```

## Workflow

1.  **Ingest**: Messages are received and buffered.
2.  **Process**: After the debounce period, the batch is sent to the LLM.
3.  **Notify**: A summary card is pushed to Redis.
4.  **React**: The bot listens for return commands to autonomously reply or schedule events.
