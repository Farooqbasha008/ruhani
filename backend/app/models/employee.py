from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MoodLevel(str, Enum):
    VERY_SAD = "1"
    SAD = "2"
    NEUTRAL = "3"
    HAPPY = "4"
    VERY_HAPPY = "5"

class SessionStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EmployeeOnboardRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    department: str = Field(..., min_length=1, max_length=50)
    role: str = Field(..., min_length=1, max_length=50)
    github: Optional[str] = None
    linkedin: Optional[str] = None
    cultural_background: Optional[str] = None
    preferred_language: str = Field(default="en", max_length=10)

class EmployeeOnboardResponse(BaseModel):
    success: bool
    employee_id: str
    message: str
    access_token: Optional[str] = None

class EmployeeLoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")

class EmployeeLoginResponse(BaseModel):
    success: bool
    employee_id: str
    name: str
    email: str
    department: str
    role: str
    message: str
    access_token: Optional[str] = None

class SessionRequest(BaseModel):
    employee_id: str
    scheduled_time: Optional[datetime] = None
    session_type: str = Field(default="check_in", description="check_in, therapy, crisis")
    notes: Optional[str] = None

class SessionResponse(BaseModel):
    success: bool
    session_id: str
    message: str
    audio_url: Optional[str] = None
    ai_response: Optional[str] = None

class VoiceSessionRequest(BaseModel):
    employee_id: str
    audio_data: str  # Base64 encoded audio
    session_context: Optional[str] = None
    mood_rating: Optional[MoodLevel] = None

class VoiceSessionResponse(BaseModel):
    success: bool
    session_id: str
    transcript: str
    ai_response: str
    audio_response: Optional[str] = None
    sentiment_analysis: Dict[str, Any]
    mood_score: float
    recommendations: List[str]
    follow_up_needed: bool

class SentimentLogRequest(BaseModel):
    employee_id: str
    source: str = Field(..., description="email, slack, chat, voice_session")
    sentiment: str
    score: float = Field(..., ge=0.0, le=5.0)
    text_content: Optional[str] = None
    timestamp: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None

class SentimentLogResponse(BaseModel):
    success: bool
    log_id: str
    message: str

class WellnessCheckRequest(BaseModel):
    employee_id: str
    mood_rating: MoodLevel
    stress_level: int = Field(..., ge=1, le=10)
    sleep_quality: int = Field(..., ge=1, le=10)
    work_satisfaction: int = Field(..., ge=1, le=10)
    social_support: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None

class WellnessCheckResponse(BaseModel):
    success: bool
    check_id: str
    overall_score: float
    recommendations: List[str]
    risk_level: str  # low, medium, high
    message: str

class EmployeeProfile(BaseModel):
    employee_id: str
    name: str
    email: str
    department: str
    role: str
    cultural_background: Optional[str]
    preferred_language: str
    onboarding_date: datetime
    last_session_date: Optional[datetime]
    total_sessions: int
    average_mood_score: float
    wellness_status: str  # excellent, stable, improving, declining, at_risk
    created_at: datetime
    updated_at: datetime

class SessionRecord(BaseModel):
    session_id: str
    employee_id: str
    session_type: str
    start_time: datetime
    end_time: Optional[datetime]
    status: SessionStatus
    transcript: Optional[str]
    ai_response: Optional[str]
    mood_score: Optional[float]
    sentiment_analysis: Optional[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime 