import os
import httpx
import json
from typing import Dict, Any, Optional
from ..core.config import settings

class GroqClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.base_url = settings.GROQ_API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def consult_llm(self, prompt: str, context: str = "", model: str = None) -> Dict[str, Any]:
        """Consult Groq LLM for psychological support"""
        if not self.api_key:
            return {"response": "I'm here to listen and support you. How are you feeling today?", "confidence": 0.8}
        
        try:
            async with httpx.AsyncClient() as client:
                # Create a culturally-aware, empathetic prompt
                system_prompt = f"""You are RUHANI, a culturally-sensitive AI psychologist. You provide:
                - Empathetic, non-judgmental support
                - Culturally-aware responses
                - Gentle guidance and encouragement
                - Professional boundaries while being warm
                
                Context: {context}
                
                Respond naturally, as if in a therapeutic conversation. Keep responses concise but meaningful."""
                
                payload = {
                    "model": model or settings.DEFAULT_AI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300
                }
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "response": result["choices"][0]["message"]["content"],
                        "confidence": 0.9,
                        "model": model or settings.DEFAULT_AI_MODEL
                    }
                else:
                    return {"response": "I'm here to support you. How are you feeling?", "confidence": 0.5}
                    
        except Exception as e:
            print(f"Groq API error: {e}")
            return {"response": "I'm here to listen. Please continue sharing.", "confidence": 0.5}

    async def transcribe_audio(self, audio_data: bytes, language: str = "en") -> Dict[str, Any]:
        """Transcribe audio using Groq's Whisper model"""
        if not self.api_key:
            return {"transcript": "Audio transcription not available", "confidence": 0.0}
        
        try:
            async with httpx.AsyncClient() as client:
                files = {"file": ("audio.wav", audio_data, "audio/wav")}
                data = {"model": "whisper-large-v3", "language": language}
                
                response = await client.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files=files,
                    data=data,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "transcript": result["text"],
                        "confidence": result.get("confidence", 0.8),
                        "language": result.get("language", language)
                    }
                else:
                    return {"transcript": "Could not transcribe audio", "confidence": 0.0}
                    
        except Exception as e:
            print(f"Groq transcription error: {e}")
            return {"transcript": "Audio processing error", "confidence": 0.0}

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of transcribed text"""
        prompt = f"""Analyze the emotional state and sentiment of this text. 
        Return a JSON with: sentiment (positive/negative/neutral), 
        mood_score (1-5), emotions (list), and urgency (low/medium/high).
        
        Text: "{text}"
        
        Focus on mental health indicators and emotional well-being."""
        
        try:
            result = await self.consult_llm(prompt)
            # Try to parse JSON response
            try:
                import json
                analysis = json.loads(result["response"])
                return analysis
            except:
                # Fallback analysis
                return {
                    "sentiment": "neutral",
                    "mood_score": 3.0,
                    "emotions": ["neutral"],
                    "urgency": "low"
                }
        except Exception as e:
            return {
                "sentiment": "neutral",
                "mood_score": 3.0,
                "emotions": ["neutral"],
                "urgency": "low"
            } 