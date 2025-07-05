from pydantic import BaseModel
from typing import Optional

class EmployeeOnboardRequest(BaseModel):
    name: str
    github: Optional[str]
    linkedin: Optional[str]
    role: str

class EmployeeOnboardResponse(BaseModel):
    success: bool
    message: str

class SessionRequest(BaseModel):
    employee_id: str
    scheduled_time: Optional[str]
    audio_url: Optional[str]

class SessionResponse(BaseModel):
    success: bool
    message: str

class SentimentLogRequest(BaseModel):
    employee_id: str
    source: str  # e.g., 'email', 'slack', 'chat'
    sentiment: str
    score: float
    timestamp: Optional[str]

class SentimentLogResponse(BaseModel):
    success: bool
    message: str 