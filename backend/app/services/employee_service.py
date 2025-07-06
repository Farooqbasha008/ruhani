from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.session import WellnessSession
from app.models.user import User
from app.schemas.session import WellnessSessionCreate, WellnessSessionUpdate
from app.db.repositories.session_repository import SessionRepository
from app.services.ai_service import AIService
from app.services.wellness_service import WellnessService
import uuid

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.ai_service = AIService()
        self.wellness_service = WellnessService(db)
    
    def create_wellness_session(
        self,
        user: User,
        session_data: WellnessSessionCreate,
        background_tasks: BackgroundTasks
    ) -> WellnessSession:
        # Create session
        session_dict = session_data.dict()
        session_dict["id"] = str(uuid.uuid4())
        session_dict["user_id"] = user.id
        session = WellnessSession(**session_dict)
        created_session = self.session_repo.create(session)

        # Add background tasks
        background_tasks.add_task(
            self._process_session_with_ai,
            created_session
        )
        
        background_tasks.add_task(
            self.wellness_service.check_wellness_alerts,
            user.id
        )

    return created_session
    
    def get_user_sessions(
        self, 
        user_id: str, 
        limit: int = 10, 
        skip: int = 0
    ) -> List[WellnessSession]:
        return self.session_repo.get_by_user_id(user_id, limit=limit, skip=skip)
    
    def get_user_wellness_summary(self, user_id: str, days: int = 7) -> dict:
        sessions = self.session_repo.get_recent_by_user_id(user_id, days=days)
        
        if not sessions:
            return {
                "total_sessions": 0,
                "average_mood": None,
                "mood_trend": "stable",
                "wellness_score": None,
                "recommendations": []
            }
        
        # Calculate metrics
        mood_scores = []
        wellness_scores = []
        
        for session in sessions:
            # Convert mood to numeric score
            mood_score = self._mood_to_score(session.mood_level)
            mood_scores.append(mood_score)
            
            if session.ai_wellness_score:
                wellness_scores.append(session.ai_wellness_score)
        
        avg_mood = sum(mood_scores) / len(mood_scores)
        avg_wellness = sum(wellness_scores) / len(wellness_scores) if wellness_scores else None
        
        # Determine trend
        if len(mood_scores) >= 3:
            recent_avg = sum(mood_scores[-3:]) / 3
            older_avg = sum(mood_scores[:-3]) / len(mood_scores[:-3]) if len(mood_scores) > 3 else recent_avg
            
            if recent_avg > older_avg + 0.2:
                trend = "improving"
            elif recent_avg < older_avg - 0.2:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "total_sessions": len(sessions),
            "average_mood": avg_mood,
            "mood_trend": trend,
            "wellness_score": avg_wellness,
            "recommendations": self._get_recommendations(sessions)
        }
    
    def _process_session_with_ai(self, session: WellnessSession):
        # This would be called asynchronously
        ai_analysis = self.ai_service.analyze_session(session)
        
        update_data = WellnessSessionUpdate(
            ai_wellness_score=ai_analysis.get("wellness_score"),
            ai_risk_assessment=ai_analysis.get("risk_assessment"),
            ai_recommendations=ai_analysis.get("recommendations"),
            ai_insights=ai_analysis.get("insights")
        )
        
        self.session_repo.update(session.id, update_data)
    
    def _mood_to_score(self, mood_level) -> float:
        mood_map = {
            "very_sad": 0.0,
            "sad": 0.25,
            "neutral": 0.5,
            "happy": 0.75,
            "very_happy": 1.0
        }
        return mood_map.get(mood_level, 0.5)
    
    def _get_recommendations(self, sessions: List[WellnessSession]) -> List[str]:
        recommendations = []
        
        # Simple rule-based recommendations
        recent_moods = [s.mood_level for s in sessions[-3:]]
        
        if "very_sad" in recent_moods:
            recommendations.append("Consider reaching out to our Employee Assistance Program")
        
        if recent_moods.count("sad") >= 2:
            recommendations.append("Take some time for self-care activities")
        
        if len(sessions) >= 7:
            recommendations.append("Great job maintaining regular check-ins!")
        
        return recommendations