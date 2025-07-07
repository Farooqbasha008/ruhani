from datetime import datetime  # Added missing import
from typing import List, Dict, Any  # Added Dict, Any for type hints
from sqlalchemy.orm import Session
from app.models.session import WellnessSession
from app.models.user import User
from app.schemas.session import WellnessSessionCreate, WellnessSessionUpdate
from app.db.repositories.session_repository import SessionRepository
from app.services.ai_service import AIService
from app.services.snowflake_service import SnowflakeService
from app.services.wellness_service import WellnessService
from fastapi import BackgroundTasks
import uuid

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.ai_service = AIService()
        self.snowflake = SnowflakeService()  # Consider making this async
        self.wellness_service = WellnessService(db)

    async def create_wellness_session(
        self,
        user: User,
        session_data: WellnessSessionCreate,
        background_tasks: BackgroundTasks
    ) -> WellnessSession:
        """Create a new wellness session with AI analysis and Snowflake logging"""
        session_dict = session_data.model_dump()  # Changed from .dict() for Pydantic v2
        session_dict.update({
            "id": str(uuid.uuid4()),
            "user_id": user.id
        })
        
        session = WellnessSession(**session_dict)
        created_session = self.session_repo.create(session)

        # Background processing
        background_tasks.add_task(self._process_session_with_ai, created_session)
        background_tasks.add_task(self.wellness_service.check_wellness_alerts, user.id)

        # Snowflake logging (consider making async)
        self._log_to_snowflake(created_session, user)
        
        return created_session

    def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10,
        skip: int = 0
    ) -> List[WellnessSession]:
        return self.session_repo.get_by_user_id(user_id, limit=limit, skip=skip)

    def get_user_wellness_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get wellness summary with trend analysis"""
        sessions = self.session_repo.get_recent_by_user_id(user_id, days=days)
        
        if not sessions:
            return {
                "total_sessions": 0,
                "average_mood": None,
                "mood_trend": "stable",
                "wellness_score": None,
                "recommendations": []
            }

        metrics = self._calculate_wellness_metrics(sessions)
        return {
            "total_sessions": len(sessions),
            "average_mood": metrics["avg_mood"],
            "mood_trend": metrics["trend"],
            "wellness_score": metrics["avg_wellness"],
            "recommendations": self._generate_recommendations(sessions)
        }

    def _log_to_snowflake(self, session: WellnessSession, user: User):
        """Log session data to Snowflake"""
        self.snowflake.log_wellness_session({
            'session_id': session.id,
            'user_id': user.id,
            'timestamp': datetime.utcnow().isoformat(),
            'wellness_score': session.ai_wellness_score,  # Use actual value from session
            'mood_level': session.mood_level.value  # Assuming enum value
        })

    def _calculate_wellness_metrics(self, sessions: List[WellnessSession]) -> Dict[str, Any]:
        """Calculate wellness metrics from sessions"""
        mood_scores = [self._mood_to_score(s.mood_level) for s in sessions]
        wellness_scores = [s.ai_wellness_score for s in sessions if s.ai_wellness_score is not None]
        
        avg_mood = sum(mood_scores) / len(mood_scores)
        avg_wellness = sum(wellness_scores) / len(wellness_scores) if wellness_scores else None
        
        trend = self._determine_mood_trend(mood_scores)
        
        return {
            "avg_mood": avg_mood,
            "avg_wellness": avg_wellness,
            "trend": trend
        }

    def _determine_mood_trend(self, mood_scores: List[float]) -> str:
        """Determine mood trend from historical scores"""
        if len(mood_scores) < 3:
            return "stable"
            
        recent_avg = sum(mood_scores[-3:]) / 3
        older_avg = sum(mood_scores[:-3]) / len(mood_scores[:-3])
        
        if recent_avg > older_avg + 0.2:
            return "improving"
        elif recent_avg < older_avg - 0.2:
            return "declining"
        return "stable"

    def _process_session_with_ai(self, session: WellnessSession):
        """Background task for AI analysis"""
        try:
            ai_analysis = self.ai_service.analyze_session(session)
            update_data = WellnessSessionUpdate(
                ai_wellness_score=ai_analysis.get("wellness_score"),
                ai_risk_assessment=ai_analysis.get("risk_assessment"),
                ai_recommendations=ai_analysis.get("recommendations"),
                ai_insights=ai_analysis.get("insights")
            )
            self.session_repo.update(session.id, update_data)
        except Exception as e:
            # Add proper error logging here
            pass

    def _mood_to_score(self, mood_level) -> float:
        """Convert mood level to numerical score"""
        mood_map = {
            "very_sad": 0.0,
            "sad": 0.25,
            "neutral": 0.5,
            "happy": 0.75,
            "very_happy": 1.0
        }
        return mood_map.get(mood_level.value if hasattr(mood_level, 'value') else mood_level, 0.5)

    def _generate_recommendations(self, sessions: List[WellnessSession]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        recent_moods = [s.mood_level for s in sessions[-3:]]
        
        if "very_sad" in recent_moods:
            recommendations.append("Consider reaching out to our Employee Assistance Program")
        if recent_moods.count("sad") >= 2:
            recommendations.append("Take some time for self-care activities")
        if len(sessions) >= 7:
            recommendations.append("Great job maintaining regular check-ins!")
            
        return recommendations