from sqlalchemy import Column, String, DateTime, Float, Integer, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class MoodLevel(str, enum.Enum):
    VERY_SAD = "very_sad"
    SAD = "sad"
    NEUTRAL = "neutral"
    HAPPY = "happy"
    VERY_HAPPY = "very_happy"

class EmotionalState(str, enum.Enum):
    CALM = "calm"
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    EXCITED = "excited"
    DEPRESSED = "depressed"
    ENERGETIC = "energetic"

class WellnessSession(Base):
    __tablename__ = "wellness_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Mood & Emotion Data
    mood_level = Column(Enum(MoodLevel), nullable=False)
    emotional_state = Column(Enum(EmotionalState), nullable=True)
    
    # Voice Analysis (Privacy-first metadata only)
    voice_sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    voice_energy_level = Column(Float, nullable=True)     # 0.0 to 1.0
    voice_stress_indicators = Column(Float, nullable=True) # 0.0 to 1.0
    
    # Facial Analysis (Privacy-first metadata only)
    facial_emotion_primary = Column(String, nullable=True)
    facial_emotion_confidence = Column(Float, nullable=True)
    facial_stress_indicators = Column(Float, nullable=True)
    
    # Session Metadata
    session_duration_seconds = Column(Integer, nullable=True)
    session_type = Column(String, default="check_in")  # check_in, follow_up, emergency
    
    # AI Analysis Results
    ai_wellness_score = Column(Float, nullable=True)  # 0.0 to 1.0
    ai_risk_assessment = Column(String, nullable=True)  # low, medium, high
    ai_recommendations = Column(Text, nullable=True)
    ai_insights = Column(Text, nullable=True)
    
    # Privacy Compliance
    data_retention_until = Column(DateTime(timezone=True), nullable=True)
    anonymized = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", backref="wellness_sessions")