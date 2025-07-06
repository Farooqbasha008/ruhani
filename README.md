# RUHANI Monorepo

This monorepo contains the frontend and backend for RUHANI — a culturally-inspired, invisible voice-based AI psychologist for enterprise employees.

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

3. **Get your API keys:**
   - **Groq:** [Console](https://console.groq.com/) (for LLM & STT)
   - **ElevenLabs:** [Dashboard](https://elevenlabs.io/) (for TTS)
   - **Fetch.ai:** [Console](https://console.fetch.ai/) (for public info)
   - **Snowflake:** [App](https://app.snowflake.com/) (database)
   - **Coral Protocol:** [Website](https://coralprotocol.com/) (activity logging)

4. **Run the backend:**
   ```sh
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
