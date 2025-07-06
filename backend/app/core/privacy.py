from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.session import WellnessSession
from app.models.wellness import WellnessAlert, WellnessRecommendation
from app.core.config import settings
from app.utils.logger import logger

class PrivacyManager:
    def __init__(self, db: Session):
        self.db = db

    def anonymize_old_sessions(self, days: int = 30):
        """Anonymize sessions older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            sessions = self.db.query(WellnessSession).filter(
                WellnessSession.timestamp < cutoff_date,
                WellnessSession.anonymized == False
            ).all()
            
            for session in sessions:
                self._anonymize_session(session)
                
            self.db.commit()
            return len(sessions)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Anonymization failed: {str(e)}")
            return 0

    def _anonymize_session(self, session: WellnessSession):
        """Remove personally identifiable data from a session"""
        session.voice_sentiment_score = None
        session.voice_energy_level = None
        session.voice_stress_indicators = None
        session.facial_emotion_primary = None
        session.facial_emotion_confidence = None
        session.facial_stress_indicators = None
        session.ai_insights = "Anonymized"
        session.anonymized = True

    def enforce_data_retention(self):
        """Delete data past retention period"""
        try:
            # Delete sessions past retention
            sessions_deleted = self.db.query(WellnessSession).filter(
                WellnessSession.data_retention_until < datetime.utcnow()
            ).delete()
            
            # Delete old alerts and recommendations
            cutoff_date = datetime.utcnow() - timedelta(days=365)
            alerts_deleted = self.db.query(WellnessAlert).filter(
                WellnessAlert.triggered_at < cutoff_date
            ).delete()
            
            recs_deleted = self.db.query(WellnessRecommendation).filter(
                WellnessRecommendation.created_at < cutoff_date
            ).delete()
            
            self.db.commit()
            return {
                "sessions_deleted": sessions_deleted,
                "alerts_deleted": alerts_deleted,
                "recommendations_deleted": recs_deleted
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Data retention enforcement failed: {str(e)}")
            return {
                "sessions_deleted": 0,
                "alerts_deleted": 0,
                "recommendations_deleted": 0
            }