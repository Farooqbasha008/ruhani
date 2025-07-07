import os
import httpx
import base64
from typing import Dict, Any, Optional
from ..core.config import settings

class ElevenLabsClient:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = settings.ELEVENLABS_API_BASE_URL
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    async def generate_tts(self, text: str, voice_id: str = None, model_id: str = "eleven_monolingual_v1") -> Dict[str, Any]:
        """Generate text-to-speech with empathetic voice"""
        if not self.api_key:
            return {"audio_url": None, "error": "ElevenLabs API key not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "text": text,
                    "model_id": model_id,
                    "voice_settings": {
                        "stability": 0.7,  # Balanced stability
                        "similarity_boost": 0.8,  # Maintain voice consistency
                        "style": 0.3,  # Slight style variation
                        "use_speaker_boost": True
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/text-to-speech/{voice_id or settings.DEFAULT_VOICE_ID}",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    # Save audio to temporary file or return as base64
                    audio_data = response.content
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    
                    return {
                        "audio_url": f"data:audio/mpeg;base64,{audio_base64}",
                        "duration": len(audio_data) / 16000,  # Approximate duration
                        "voice_id": voice_id or settings.DEFAULT_VOICE_ID,
                        "success": True
                    }
                else:
                    return {
                        "audio_url": None,
                        "error": f"ElevenLabs API error: {response.status_code}",
                        "success": False
                    }
                    
        except Exception as e:
            print(f"ElevenLabs API error: {e}")
            return {
                "audio_url": None,
                "error": str(e),
                "success": False
            }

    async def get_available_voices(self) -> Dict[str, Any]:
        """Get available voices for selection"""
        if not self.api_key:
            return {"voices": [], "error": "ElevenLabs API key not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    voices = response.json()
                    # Filter for empathetic, professional voices
                    empathetic_voices = [
                        voice for voice in voices.get("voices", [])
                        if voice.get("category") == "premade" and 
                        voice.get("description", "").lower() in ["warm", "empathetic", "professional", "caring"]
                    ]
                    
                    return {
                        "voices": empathetic_voices[:5],  # Return top 5
                        "success": True
                    }
                else:
                    return {
                        "voices": [],
                        "error": f"Failed to fetch voices: {response.status_code}",
                        "success": False
                    }
                    
        except Exception as e:
            print(f"ElevenLabs voices error: {e}")
            return {
                "voices": [],
                "error": str(e),
                "success": False
            }

    async def clone_voice(self, name: str, description: str, files: list) -> Dict[str, Any]:
        """Clone a voice for personalized experience"""
        if not self.api_key:
            return {"voice_id": None, "error": "ElevenLabs API key not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "name": name,
                    "description": description,
                    "labels": '{"accent": "neutral", "age": "adult", "gender": "neutral"}'
                }
                
                response = await client.post(
                    f"{self.base_url}/voices/add",
                    headers={"xi-api-key": self.api_key},
                    data=payload,
                    files=[("files", file) for file in files],
                    timeout=120.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "voice_id": result.get("voice_id"),
                        "success": True
                    }
                else:
                    return {
                        "voice_id": None,
                        "error": f"Voice cloning failed: {response.status_code}",
                        "success": False
                    }
                    
        except Exception as e:
            print(f"Voice cloning error: {e}")
            return {
                "voice_id": None,
                "error": str(e),
                "success": False
            } 