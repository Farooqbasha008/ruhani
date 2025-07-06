import os
import httpx
import json
from typing import Dict, Any, Optional

FETCHAI_API_KEY = os.getenv("FETCHAI_API_KEY")
FETCHAI_API_BASE_URL = os.getenv("FETCHAI_API_BASE_URL", "https://api.fetch.ai/v1")

class FetchAIClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {FETCHAI_API_KEY}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_public_info(self, github: Optional[str] = None, linkedin: Optional[str] = None) -> Dict[str, Any]:
        """Fetch public information about a person using Fetch.ai agents"""
        if not FETCHAI_API_KEY:
            # In development, we'll return mock data
            return self._generate_mock_data(github, linkedin)

        if not github and not linkedin:
            return {"error": "At least one of github or linkedin must be provided"}

        url = f"{FETCHAI_API_BASE_URL}/agents/public-info"
        payload = {}
        
        if github:
            payload["github_url"] = github
        if linkedin:
            payload["linkedin_url"] = linkedin
        
        try:
            response = await self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"FetchAI API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            print(f"Error fetching from FetchAI: {str(e)}")
            return {"error": f"Error fetching from FetchAI: {str(e)}"}
    
    def _generate_mock_data(self, github: Optional[str] = None, linkedin: Optional[str] = None) -> Dict[str, Any]:
        """Generate mock data for development purposes"""
        mock_data = {
            "public_info": {
                "name": "John Doe",
                "skills": ["Python", "JavaScript", "Machine Learning", "Data Analysis"],
                "experience": [
                    {"company": "Tech Corp", "role": "Senior Developer", "years": "2020-2023"},
                    {"company": "Data Inc", "role": "Data Scientist", "years": "2018-2020"}
                ],
                "education": [
                    {"institution": "University of Technology", "degree": "MS Computer Science", "year": "2018"}
                ],
                "interests": ["AI", "Blockchain", "Open Source"],
                "public_repos": 12,
                "contributions": 450,
                "connections": 500
            },
            "source": "mock_data",
            "github": github,
            "linkedin": linkedin
        }
        
        # Customize based on provided URLs
        if github and "john" in github.lower():
            mock_data["public_info"]["name"] = "John Smith"
        elif linkedin and "jane" in linkedin.lower():
            mock_data["public_info"]["name"] = "Jane Wilson"
            mock_data["public_info"]["skills"] = ["Product Management", "UX Design", "Marketing"]
        
        return mock_data
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()