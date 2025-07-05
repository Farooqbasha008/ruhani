import os
import httpx

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_BASE_URL = os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/v1")

class GroqClient:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    async def consult_llm(self, prompt: str):
        # TODO: Call Groq LLM endpoint
        return {"response": "LLM response (stub)"}

    async def transcribe_audio(self, audio_url: str):
        # TODO: Call Groq STT endpoint
        return {"transcript": "Transcribed text (stub)"} 