import os
import httpx

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_API_BASE_URL = os.getenv("ELEVENLABS_API_BASE_URL", "https://api.elevenlabs.io/v1")

class ElevenLabsClient:
    def __init__(self):
        self.headers = {"xi-api-key": ELEVENLABS_API_KEY}

    async def generate_tts(self, text: str):
        # TODO: Call ElevenLabs TTS endpoint
        return {"audio_url": "TTS audio (stub)"} 