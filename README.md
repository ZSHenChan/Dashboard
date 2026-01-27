# Personal Dashboard

This is a hobby project designed to streamline personal digital communication and productivity using Large Language Models (LLMs). This dashboard acts as a central hub for managing incoming messages across various platforms and maintaining a versatile library of AI prompts for daily tasks.

## Key Features

### 1. Unified Message Dashboard

Consolidate your digital inbox into a single view.

- **Multi-Platform Support:** Ingests messages from major social media platforms (Telegram, Instagram, WhatsApp) and Email services.
- **AI-Powered Processing:** Utilizes LLMs to process incoming text.
- **Intention Summarization:** Automatically tags and summarizes the core intention of each message (e.g., "Urgent Request," "Casual Catch-up," "Spam").
- **Smart Reply Drafts:** Generates context-aware draft replies based on intended sentiment (e.g., Accept, Decline, Neutral, Enthusiastic), with the mimicking of user's tone and wordings.

### 2. Prompt Library

A robust management system for your LLM interactions.

- **System Instruction Management:** Store and organize prompts with distinct system instructions (personas).
- **Easy Customization:** Quickly tweak parameters and context for reusable prompts.
- **One-Shot Task Execution:** specialized templates for immediate tasks without creating new chats with LLM, such as:
  - _Resume Customizer:_ Tailor a CV for a specific job description in one go.
  - _Email Polisher:_ Rephrase rough notes into professional correspondence.

## Roadmap

- [ ] Implement API connectors for Telegram and WhatsApp.
- [ ] Set up Email IMAP/SMTP integration.
- [ ] Integrate LLM provider (OpenAI/Azure OpenAI/Anthropic).
- [ ] Build frontend dashboard for message triage.
- [ ] Develop database schema for storing message history and prompt templates.

## License

[MIT](LICENSE)
