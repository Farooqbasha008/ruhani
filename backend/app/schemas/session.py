from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.session import MoodLevel, EmotionalState

class WellnessSessionBase(BaseModel):
    mood_level: MoodLevel
    emotional_state: Optional[EmotionalState] = None
    voice_sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    voice_energy_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    voice_stress_indicators: Optional[float] = Field(None, ge=0.0, le=1.0)
    facial_emotion_primary: Optional[str] = None
    facial_emotion_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    facial_stress_indicators: Optional[float] = Field(None, ge=0.0, le=1.0)
    session_duration_seconds: Optional[int] = Field(None, ge=0)
    session_type: str = "check_in"

class WellnessSessionCreate(WellnessSessionBase):
    pass

class WellnessSessionUpdate(BaseModel):
    ai_wellness_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    ai_risk_assessment: Optional[str] = None
    ai_recommendations: Optional[str] = None
    ai_insights: Optional[str] = None

class WellnessSessionResponse(WellnessSessionBase):
    id: str
    user_id: str
    timestamp: datetime
    ai_wellness_score: Optional[float] = None
    ai_risk_assessment: Optional[str] = None
    ai_recommendations: Optional[str] = None
    ai_insights: Optional[str] = None
    
    class Config:
        orm_mode = True