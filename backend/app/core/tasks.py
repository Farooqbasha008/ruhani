from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.services.ai_service import AIService
from app.services.wellness_service import WellnessService
from app.models.session import WellnessSession
from app.utils.logger import logger

def process_session_with_ai(
    background_tasks: BackgroundTasks,
    session_id: str,
    db: Session
):
    """Add session processing to background tasks"""
    background_tasks.add_task(_analyze_and_process_session, session_id, db)

def _analyze_and_process_session(session_id: str, db: Session):
    """Background task to analyze session and generate alerts/recommendations"""
    try:
        session = db.query(WellnessSession).filter(WellnessSession.id == session_id).first()
        if not session:
            return
            
        # AI Analysis
        ai_service = AIService()
        ai_analysis = ai_service.analyze_session(session)
        
        # Update session with AI results
        for key, value in ai_analysis.items():
            setattr(session, f"ai_{key}", value)
        
        db.commit()
        
        # Generate wellness alerts and recommendations
        wellness_service = WellnessService(db)
        wellness_service.check_wellness_alerts(session.user_id)
        wellness_service.generate_recommendations(session.user_id)
        
    except Exception as e:
        logger.error(f"Background processing failed for session {session_id}: {str(e)}")
        db.rollback()