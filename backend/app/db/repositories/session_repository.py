from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models.session import WellnessSession, MoodLevel
from app.db.repositories.base_repository import BaseRepository

class SessionRepository(BaseRepository[WellnessSession]):
    def __init__(self, db: Session):
        super().__init__(db, WellnessSession)
    
    def get_by_user_id(
        self, 
        user_id: str, 
        limit: int = 10, 
        skip: int = 0
    ) -> List[WellnessSession]:
        return self.db.query(WellnessSession).filter(
            WellnessSession.user_id == user_id
        ).order_by(desc(WellnessSession.timestamp)).offset(skip).limit(limit).all()
    
    def get_recent_by_user_id(self, user_id: str, days: int = 7) -> List[WellnessSession]:
        since_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(WellnessSession).filter(
            WellnessSession.user_id == user_id,
            WellnessSession.timestamp >= since_date
        ).order_by(desc(WellnessSession.timestamp)).all()
    
    def get_latest_by_user_id(self, user_id: str) -> Optional[WellnessSession]:
        return self.db.query(WellnessSession).filter(
            WellnessSession.user_id == user_id
        ).order_by(desc(WellnessSession.timestamp)).first()
    
    def count_sessions(self, since_date: datetime) -> int:
        return self.db.query(func.count(WellnessSession.id)).filter(
            WellnessSession.timestamp >= since_date
        ).scalar()
    
    def count_active_users(self, since_date: datetime) -> int:
        return self.db.query(func.count(func.distinct(WellnessSession.user_id))).filter(
            WellnessSession.timestamp >= since_date
        ).scalar()
    
    def get_mood_distribution(self, since_date: datetime) -> Dict[str, int]:
        results = self.db.query(
            WellnessSession.mood_level,
            func.count(WellnessSession.id).label('count')
        ).filter(
            WellnessSession.timestamp >= since_date
        ).group_by(WellnessSession.mood_level).all()
        
        return {mood.value: count for mood, count in results}
    
    def get_wellness_trends(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        sessions = self.db.query(WellnessSession).filter(
            WellnessSession.user_id == user_id,
            WellnessSession.timestamp >= since_date
        ).order_by(WellnessSession.timestamp).all()
        
        trends = []
        for session in sessions:
            trends.append({
                "date": session.timestamp.date(),
                "mood_level": session.mood_level,
                "wellness_score": session.ai_wellness_score,
                "voice_sentiment": session.voice_sentiment_score,
                "stress_level": session.voice_stress_indicators
            })
        
        return trends
    
    def get_session_statistics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        sessions = self.get_recent_by_user_id(user_id, days)
        
        if not sessions:
            return {
                "total_sessions": 0,
                "average_mood_score": None,
                "average_wellness_score": None,
                "stress_trend": "unknown"
            }
        
        # Calculate mood scores
        mood_scores = []
        for session in sessions:
            score = {
                "very_sad": 0.0,
                "sad": 0.25,
                "neutral": 0.5,
                "happy": 0.75,
                "very_happy": 1.0
            }.get(session.mood_level.value, 0.5)
            mood_scores.append(score)
        
        # Calculate wellness scores
        wellness_scores = [
            s.ai_wellness_score for s in sessions 
            if s.ai_wellness_score is not None
        ]
        
        # Calculate stress trend
        stress_levels = [
            s.voice_stress_indicators for s in sessions 
            if s.voice_stress_indicators is not None
        ]
        
        stress_trend = "unknown"
        if len(stress_levels) >= 3:
            recent_avg = sum(stress_levels[-2:]) / 2
            older_avg = sum(stress_levels[:-2]) / len(stress_levels[:-2])
            
            if recent_avg > older_avg + 0.1:
                stress_trend = "increasing"
            elif recent_avg < older_avg - 0.1:
                stress_trend = "decreasing"
            else:
                stress_trend = "stable"
        
        return {
            "total_sessions": len(sessions),
            "average_mood_score": sum(mood_scores) / len(mood_scores),
            "average_wellness_score": sum(wellness_scores) / len(wellness_scores) if wellness_scores else None,
            "stress_trend": stress_trend
        }