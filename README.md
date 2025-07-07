# RUHANI Monorepo

This monorepo contains the frontend and backend for RUHANI — a culturally-inspired, invisible voice-based AI psychologist for enterprise employees.

## Overview

RUHANI is an AI-powered wellness platform designed to support employee mental health through regular voice-based check-ins. The platform provides a safe space for employees to express their thoughts and feelings, while giving HR teams anonymized insights into organizational well-being.

### Key Features

- **Voice-Based Check-ins**: Employees can have natural conversations with an AI psychologist
- **Personalized Experience**: System remembers past interactions and adapts to individual needs
- **HR Dashboard**: Anonymized insights into organizational well-being trends
- **Privacy-First**: All data is protected using Coral Protocol's decentralized identity (DID) and verifiable credentials system
- **Multi-Modal**: Combines voice, text, and visual elements for a complete experience

## Structure

- `backend/` — FastAPI backend for Employee and HR modes, integrating Groq, ElevenLabs, Fetch.ai, Snowflake, and Coral Protocol.
- `src/` — Frontend (React/Vite)

## 🚀 Quick Start for Collaborators

### 1. Backend Setup

1. **Install Python dependencies:**
   ```sh
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```sh
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your API keys
   # See backend/.env.example for detailed instructions
   ```

3. **Environment variables needed:**
   ```
   # API Keys
   GROQ_API_KEY=your_groq_api_key
   ELEVEN_LABS_API_KEY=your_eleven_labs_api_key
   FETCH_AI_API_KEY=your_fetch_ai_api_key
   CORAL_API_KEY=your_coral_api_key  # For decentralized identity and verifiable credentials
   
   # Snowflake Database
   SNOWFLAKE_ACCOUNT=your_snowflake_account
   SNOWFLAKE_USER=your_snowflake_user
   SNOWFLAKE_PASSWORD=your_snowflake_password
   SNOWFLAKE_DATABASE=your_snowflake_database
   SNOWFLAKE_SCHEMA=your_snowflake_schema
   SNOWFLAKE_WAREHOUSE=your_snowflake_warehouse
   SNOWFLAKE_ROLE=your_snowflake_role
   
   # JWT
   JWT_SECRET=your_jwt_secret
   
   # Application Configuration
   ENVIRONMENT=development  # Set to 'production' in production environment
   FRONTEND_URL=http://localhost:5173
   BACKEND_URL=http://localhost:8000
   
   # Feature Flags
   SEED_SAMPLE_DATA=true  # Set to 'false' to disable sample data seeding
   ```

3. **Get your API keys:**
   - **Groq:** [Console](https://console.groq.com/) (for LLM & STT)
   - **ElevenLabs:** [Dashboard](https://elevenlabs.io/) (for TTS)
   - **Fetch.ai:** [Console](https://console.fetch.ai/) (for public info)
   - **Snowflake:** [App](https://app.snowflake.com/) (database)
   - **Coral Protocol:** [Website](https://coralprotocol.com/) (activity logging)

4. **Test the database setup (optional but recommended):**
   ```sh
   cd backend
   python -m app.db.test_db_setup
   ```

5. **Run the backend:**
   ```sh
   cd backend
   python run.py
   ```
   
   Alternatively, you can use uvicorn directly:
   ```sh
   cd backend
   uvicorn app.main:app --reload
   ```

### 2. Frontend Setup

1. **Install Node.js dependencies:**
   ```sh
   npm install
   ```

2. **Start the frontend:**
   ```sh
   npm run dev
   ```

## 🔐 Security Notes

- **Never commit `.env` files** - they contain sensitive API keys
- Use `.env.example` as a template for your own `.env` file
- Each collaborator should have their own API keys

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

# Welcome to your Lovable project

## Project info

**URL**: https://lovable.dev/projects/e4d3f9fb-486f-47db-b079-04bc69ad5414

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/e4d3f9fb-486f-47db-b079-04bc69ad5414) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/e4d3f9fb-486f-47db-b079-04bc69ad5414) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)
