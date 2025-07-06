import os
import httpx
import base64
from typing import Dict, Any, Optional

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_API_BASE_URL = os.getenv("ELEVENLABS_API_BASE_URL", "https://api.elevenlabs.io/v1")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default voice ID (Rachel)

class ElevenLabsClient:
    def __init__(self):
        self.headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        self.client = httpx.AsyncClient(timeout=30.0)  # Longer timeout for TTS operations

    async def generate_tts(self, text: str, voice_id: Optional[str] = None) -> Dict[str, Any]:
        """Call ElevenLabs TTS endpoint to convert text to speech"""
        if not ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")

        voice_id = voice_id or ELEVENLABS_VOICE_ID
        url = f"{ELEVENLABS_API_BASE_URL}/text-to-speech/{voice_id}"
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = await self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            # In a production environment, you would likely save this to a file or cloud storage
            # and return a URL. For simplicity, we'll return the base64-encoded audio.
            audio_data = response.content
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                "audio_data": audio_base64,
                "content_type": "audio/mpeg",
                "success": True
            }
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP error: {e.response.status_code}", 
                "details": e.response.text,
                "success": False
            }
        except Exception as e:
            return {
                "error": f"Error calling ElevenLabs TTS: {str(e)}",
                "success": False
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()