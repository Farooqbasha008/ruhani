from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.privacy import PrivacyManager
from app.utils.logger import logger

scheduler = BackgroundScheduler()

def schedule_privacy_tasks():
    """Schedule regular privacy and maintenance tasks"""
    try:
        # Anonymize old data daily at 2 AM
        scheduler.add_job(
            anonymize_data_task,
            'cron',
            hour=2,
            minute=0,
            name="anonymize_old_data"
        )
        
        # Enforce data retention weekly
        scheduler.add_job(
            enforce_retention_task,
            'cron',
            day_of_week='sun',
            hour=3,
            minute=0,
            name="enforce_data_retention"
        )
        
        scheduler.start()
    except Exception as e:
        logger.error(f"Failed to schedule tasks: {str(e)}")

def anonymize_data_task():
    """Task to anonymize old session data"""
    db = SessionLocal()
    try:
        privacy = PrivacyManager(db)
        count = privacy.anonymize_old_sessions(days=30)
        logger.info(f"Anonymized {count} old sessions")
    finally:
        db.close()

def enforce_retention_task():
    """Task to enforce data retention policies"""
    db = SessionLocal()
    try:
        privacy = PrivacyManager(db)
        result = privacy.enforce_data_retention()
        logger.info(
            f"Data retention enforcement completed: "
            f"Sessions: {result['sessions_deleted']}, "
            f"Alerts: {result['alerts_deleted']}, "
            f"Recommendations: {result['recommendations_deleted']}"
        )
    finally:
        db.close()