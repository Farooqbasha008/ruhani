# RUHANI Backend

This is the FastAPI backend for RUHANI — a culturally-inspired, invisible voice-based AI psychologist for enterprise employees.

## Features
- Employee onboarding (Fetch.ai, GitHub, LinkedIn)
- Sentiment monitoring (work signals)
- Session scheduling & recording (Groq STT, LLM, ElevenLabs TTS)
- HR dashboard (insights, trends, at-risk detection)
- Snowflake storage & Coral Protocol logging

## Setup
1. Copy `.env.example` to `.env` and fill in your API keys.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the backend:
   ```sh
   uvicorn app.main:app --reload
   ``` 