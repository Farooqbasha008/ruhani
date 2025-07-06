# RUHANI Backend

This is the FastAPI backend for RUHANI — a culturally-inspired, invisible voice-based AI psychologist for enterprise employees.

## Features
- Employee onboarding (Fetch.ai, GitHub, LinkedIn)
- Sentiment monitoring (work signals)
- Session scheduling & recording (Groq STT, LLM, ElevenLabs TTS)
- HR dashboard (insights, trends, at-risk detection)
- Snowflake storage & Coral Protocol logging

## 🚀 Setup for Collaborators

### 1. Install Dependencies
```sh
pip install -r requirements.txt
```

### 2. Environment Variables Setup
```sh
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
# See .env.example for detailed instructions and URLs
```

### 3. Required API Keys
You'll need to obtain API keys from these services:

- **Groq API** ([Console](https://console.groq.com/))
  - Used for: LLM consultation and Speech-to-Text
  - Format: `gsk_...`

- **ElevenLabs API** ([Dashboard](https://elevenlabs.io/))
  - Used for: Text-to-Speech responses
  - Format: `sk_...`

- **Fetch.ai API** ([Console](https://console.fetch.ai/))
  - Used for: Fetching public info (GitHub, LinkedIn)
  - Format: JWT token

- **Snowflake Database** ([App](https://app.snowflake.com/))
  - Used for: Storing employee data and sessions
  - Need: Account, User, Password, Warehouse, Database, Schema, Role

- **Coral Protocol** ([Website](https://coralprotocol.com/))
  - Used for: Activity logging
  - Format: API key

### 4. Run the Backend
```sh
uvicorn app.main:app --reload
```

## 📚 API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔐 Security
- Never commit your `.env` file
- Each collaborator should have their own API keys
- Use `.env.example` as a template 