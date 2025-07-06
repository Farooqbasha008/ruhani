import os
import httpx
import json
import uuid
from datetime import datetime
from typing import Dict, Any

CORAL_API_KEY = os.getenv("CORAL_API_KEY")
CORAL_API_BASE_URL = os.getenv("CORAL_API_BASE_URL", "https://api.coralprotocol.com/v1")

class CoralClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {CORAL_API_KEY}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=10.0)

    async def log_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Log activity to Coral Protocol for privacy and compliance"""
        if not CORAL_API_KEY:
            # In development, we'll just log to console and return success
            print(f"[CORAL MOCK] Would log activity: {json.dumps(activity, indent=2)}")
            return {"logged": True, "mock": True, "activity_id": str(uuid.uuid4())}

        # Add timestamp and activity ID if not present
        if "timestamp" not in activity:
            activity["timestamp"] = datetime.utcnow().isoformat()
        if "activity_id" not in activity:
            activity["activity_id"] = str(uuid.uuid4())

        url = f"{CORAL_API_BASE_URL}/activities"
        
        try:
            response = await self.client.post(url, headers=self.headers, json=activity)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Coral API error: {e.response.status_code} - {e.response.text}")
            # In production, you might want to retry or queue the activity for later
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            print(f"Error logging to Coral: {str(e)}")
            return {"error": f"Error logging to Coral: {str(e)}"}

    async def anonymize_data(self, data: Dict[str, Any], fields_to_anonymize: list) -> Dict[str, Any]:
        """Anonymize sensitive data fields"""
        if not CORAL_API_KEY:
            # In development, we'll just mock anonymization
            anonymized_data = data.copy()
            for field in fields_to_anonymize:
                if field in anonymized_data:
                    anonymized_data[field] = f"[ANONYMIZED {field}]"
            return {"anonymized": anonymized_data, "mock": True}

        url = f"{CORAL_API_BASE_URL}/anonymize"
        payload = {
            "data": data,
            "fields": fields_to_anonymize
        }
        
        try:
            response = await self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Coral API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            print(f"Error anonymizing with Coral: {str(e)}")
            return {"error": f"Error anonymizing with Coral: {str(e)}"}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()