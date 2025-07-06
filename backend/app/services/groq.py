import os
import httpx
import json
from typing import Dict, Any, Optional

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_BASE_URL = os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/v1")
GROQ_LLM_MODEL = os.getenv("GROQ_LLM_MODEL", "llama3-70b-8192")

class GroqClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=60.0)  # Longer timeout for LLM operations

    async def consult_llm(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Call Groq LLM endpoint to get a response to the prompt"""
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is not set")

        url = f"{GROQ_API_BASE_URL}/chat/completions"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": GROQ_LLM_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            response = await self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            return {
                "response": result["choices"][0]["message"]["content"],
                "raw_response": result
            }
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            return {"error": f"Error calling Groq LLM: {str(e)}"}

    async def transcribe_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """Call Groq STT endpoint to transcribe audio"""
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is not set")

        # Note: As of my knowledge, Groq doesn't have a native STT API
        # This is a placeholder for when they add one, or we can switch to another provider
        # For now, we'll simulate a response
        
        # In a real implementation, you would upload the audio to Groq or another STT service
        # url = f"{GROQ_API_BASE_URL}/audio/transcriptions"
        # files = {"file": audio_data}
        # response = await self.client.post(url, headers=self.headers, files=files)
        
        # For now, return a mock response
        return {
            "transcript": "This is a simulated transcript. In production, this would be the actual transcribed text from the audio.",
            "confidence": 0.95
        }
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()