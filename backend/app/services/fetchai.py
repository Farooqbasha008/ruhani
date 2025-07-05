import os
import httpx

FETCHAI_API_KEY = os.getenv("FETCHAI_API_KEY")
FETCHAI_API_BASE_URL = os.getenv("FETCHAI_API_BASE_URL", "https://api.fetch.ai/v1")

class FetchAIClient:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {FETCHAI_API_KEY}"}

    async def fetch_public_info(self, github: str = None, linkedin: str = None):
        # TODO: Call Fetch.ai agent to get public info
        return {"info": "Public info (stub)"} 