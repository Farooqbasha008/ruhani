from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class EmployeeOnboardRequest(BaseModel):
    name: str
    github: Optional[str] = None
    linkedin: Optional[str] = None
    role: str

class EmployeeOnboardResponse(BaseModel):
    success: bool
    message: str
    employee_id: Optional[str] = None

class SessionRequest(BaseModel):
    employee_id: str
    scheduled_time: Optional[str] = None
    audio_url: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 encoded audio data

class SessionResponse(BaseModel):
    success: bool
    message: str
    session_id: Optional[str] = None
    transcript: Optional[str] = None
    response: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 encoded audio data
    risk_level: Optional[str] = None  # 'low', 'medium', 'high'

class SentimentLogRequest(BaseModel):
    employee_id: str
    source: str  # e.g., 'email', 'slack', 'chat'
    sentiment: str
    score: float
    timestamp: Optional[str] = None

class SentimentLogResponse(BaseModel):
    success: bool
    message: str
    log_id: Optional[str] = None

class Employee(BaseModel):
    id: str
    name: str
    email: str
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    team: str
    stressors: Optional[List[str]] = None
    onboarding_date: str

class Session(BaseModel):
    session_id: str
    employee_id: str
    session_time: str
    mood: Optional[str] = None
    summary: Optional[str] = None
    llm_response: Optional[str] = None
    risk_level: Optional[str] = None

class HRInsight(BaseModel):
    id: str
    employee_id: str
    weekly_summary: str
    flags: Optional[List[str]] = None
    trends: Optional[Dict[str, Any]] = None
    created_at: str