from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.wellness import WellnessAlert, WellnessRecommendation
from app.models.session import WellnessSession
from app.models.user import User
from app.db.repositories.session_repository import SessionRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.wellness import WellnessAlertCreate, WellnessRecommendationCreate

class WellnessService:
    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.user_repo = UserRepository(db)

    def check_wellness_alerts(self, user_id: str) -> List[WellnessAlert]:
        """Check for potential wellness alerts based on recent sessions"""
        recent_sessions = self.session_repo.get_recent_by_user_id(user_id, days=7)
        if not recent_sessions:
            return []

        alerts = []
        
        # Mood-based alerts
        recent_moods = [s.mood_level for s in recent_sessions[-3:]]
        if all(m == "very_sad" for m in recent_moods):
            alerts.append(self._create_alert(
                user_id, 
                "depression_risk", 
                "high",
                "Consistently very low mood detected in recent sessions"
            ))
        elif "very_sad" in recent_moods or recent_moods.count("sad") >= 2:
            alerts.append(self._create_alert(
                user_id,
                "depression_risk",
                "medium",
                "Low mood patterns detected"
            ))

        # Stress-based alerts
        stress_levels = [s.voice_stress_indicators for s in recent_sessions 
                        if s.voice_stress_indicators is not None]
        if stress_levels and sum(stress_levels)/len(stress_levels) > 0.7:
            alerts.append(self._create_alert(
                user_id,
                "stress_spike",
                "high" if max(stress_levels) > 0.8 else "medium",
                "Elevated stress levels detected"
            ))

        # Session frequency alerts
        if len(recent_sessions) < 2:
            alerts.append(self._create_alert(
                user_id,
                "engagement_low",
                "low",
                "Low engagement with wellness program"
            ))

        return alerts

    def _create_alert(self, user_id: str, alert_type: str, severity: str, 
                     description: str) -> WellnessAlert:
        """Helper to create and save a new alert"""
        alert = WellnessAlert(
            user_id=user_id,
            alert_type=alert_type,
            severity=severity,
            description=description,
            triggered_at=datetime.utcnow()
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def generate_recommendations(self, user_id: str) -> List[WellnessRecommendation]:
        """Generate personalized wellness recommendations"""
        recent_sessions = self.session_repo.get_recent_by_user_id(user_id, days=14)
        if not recent_sessions:
            return []

        recommendations = []
        user = self.user_repo.get_by_id(user_id)
        
        # Mood-based recommendations
        mood_counts = {}
        for session in recent_sessions:
            mood_counts[session.mood_level] = mood_counts.get(session.mood_level, 0) + 1
        
        if mood_counts.get("very_sad", 0) >= 2:
            recommendations.append(self._create_recommendation(
                user_id,
                "support",
                "Professional Support Suggested",
                "Based on your recent mood patterns, we recommend connecting with our EAP counselor.",
                "high"
            ))
        
        # Stress-based recommendations
        avg_stress = sum(s.voice_stress_indicators for s in recent_sessions 
                        if s.voice_stress_indicators is not None) / len(recent_sessions)
        if avg_stress > 0.6:
            recommendations.append(self._create_recommendation(
                user_id,
                "break",
                "Mindfulness Break",
                "Consider taking a 5-minute mindfulness break to reduce stress.",
                "medium"
            ))

        # Engagement recommendations
        if len(recent_sessions) < 3:
            recommendations.append(self._create_recommendation(
                user_id,
                "engagement",
                "Regular Check-ins",
                "Regular check-ins help us better support your mental wellness.",
                "low"
            ))

        return recommendations

    def _create_recommendation(self, user_id: str, rec_type: str, title: str,
                             description: str, priority: str) -> WellnessRecommendation:
        """Helper to create and save a new recommendation"""
        recommendation = WellnessRecommendation(
            user_id=user_id,
            recommendation_type=rec_type,
            title=title,
            description=description,
            priority=priority,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Optional[WellnessAlert]:
        """Mark an alert as acknowledged by HR"""
        alert = self.db.query(WellnessAlert).filter(WellnessAlert.id == alert_id).first()
        if alert:
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = acknowledged_by
            self.db.commit()
            self.db.refresh(alert)
        return alert

    def resolve_alert(self, alert_id: str, resolved_by: str) -> Optional[WellnessAlert]:
        """Mark an alert as resolved"""
        alert = self.db.query(WellnessAlert).filter(WellnessAlert.id == alert_id).first()
        if alert:
            alert.resolved_at = datetime.utcnow()
            alert.acknowledged_by = resolved_by
            alert.is_active = False
            self.db.commit()
            self.db.refresh(alert)
        return alert