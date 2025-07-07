from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import uuid
from datetime import datetime

from ..models.employee import (
    EmployeeOnboardRequest, EmployeeOnboardResponse, 
    EmployeeLoginRequest, EmployeeLoginResponse,
    SessionRequest, SessionResponse, 
    VoiceSessionRequest, VoiceSessionResponse,
    SentimentLogRequest, SentimentLogResponse,
    WellnessCheckRequest, WellnessCheckResponse,
    EmployeeProfile
)
from ..services.session_service import SessionService
from ..services.fetchai import FetchAIClient
from ..core.auth import create_employee_token, get_current_user
from ..db.snowflake_client import SnowflakeClient

router = APIRouter()
session_service = SessionService()
fetchai_client = FetchAIClient()
db_client = SnowflakeClient()

@router.post("/onboard", response_model=EmployeeOnboardResponse)
async def onboard_employee(payload: EmployeeOnboardRequest):
    """Onboard a new employee with public info gathering"""
    try:
        employee_id = str(uuid.uuid4())
        
        # Gather public information if available
        public_info = {}
        if payload.github or payload.linkedin:
            public_info = await fetchai_client.fetch_public_info(
                github=payload.github,
                linkedin=payload.linkedin
            )
        
        # Store employee data in database
        query = """
        INSERT INTO employees (
            employee_id, name, email, department, role, github, linkedin,
            cultural_background, preferred_language, public_info, created_at
        ) VALUES (%(employee_id)s, %(name)s, %(email)s, %(department)s, %(role)s, %(github)s, %(linkedin)s, %(cultural_background)s, %(preferred_language)s, %(public_info)s, %(created_at)s)
        """
        
        params = {
            "employee_id": employee_id,
            "name": payload.name,
            "email": payload.email,
            "department": payload.department,
            "role": payload.role,
            "github": payload.github,
            "linkedin": payload.linkedin,
            "cultural_background": payload.cultural_background,
            "preferred_language": payload.preferred_language,
            "public_info": str(public_info),
            "created_at": datetime.utcnow()
        }
        
        db_client.execute(query, params)
        
        # Create access token
        access_token = create_employee_token(employee_id)
        
        return EmployeeOnboardResponse(
            success=True,
            employee_id=employee_id,
            message="Employee onboarded successfully",
            access_token=access_token
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Onboarding failed: {str(e)}"
        )

@router.post("/login", response_model=EmployeeLoginResponse)
async def login_employee(payload: EmployeeLoginRequest):
    """Login an existing employee by email"""
    try:
        # Check if employee exists
        query = """
        SELECT employee_id, name, email, department, role, created_at
        FROM employees 
        WHERE email = %(email)s
        """
        
        result = db_client.execute(query, {"email": payload.email})
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found. Please register first."
            )
        
        employee = result[0]
        
        # Create access token
        access_token = create_employee_token(employee[0])
        
        return EmployeeLoginResponse(
            success=True,
            employee_id=employee[0],
            name=employee[1],
            email=employee[2],
            department=employee[3],
            role=employee[4],
            message="Login successful",
            access_token=access_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/voice-session", response_model=VoiceSessionResponse)
async def process_voice_session(payload: VoiceSessionRequest, current_user: str = Depends(get_current_user)):
    """Process a voice-based therapy session"""
    try:
        # Verify employee owns the session
        if payload.employee_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this session"
            )
        
        # Process the voice session
        result = await session_service.process_voice_session(payload)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session processing failed: {str(e)}"
        )

@router.post("/session", response_model=SessionResponse)
async def schedule_session(payload: SessionRequest, current_user: str = Depends(get_current_user)):
    """Schedule a therapy session"""
    try:
        session_id = str(uuid.uuid4())
        
        # Store session in database
        query = """
        INSERT INTO employee_sessions (
            session_id, employee_id, session_type, start_time, status, notes, created_at
        ) VALUES (%(session_id)s, %(employee_id)s, %(session_type)s, %(start_time)s, %(status)s, %(notes)s, %(created_at)s)
        """
        
        params = {
            "session_id": session_id,
            "employee_id": payload.employee_id,
            "session_type": payload.session_type,
            "start_time": payload.scheduled_time or datetime.utcnow(),
            "status": "scheduled",
            "notes": payload.notes,
            "created_at": datetime.utcnow()
        }
        
        db_client.execute(query, params)
        
        return SessionResponse(
            success=True,
            session_id=session_id,
            message="Session scheduled successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session scheduling failed: {str(e)}"
        )

@router.post("/sentiment", response_model=SentimentLogResponse)
async def log_sentiment(payload: SentimentLogRequest, current_user: str = Depends(get_current_user)):
    """Log sentiment data from various sources"""
    try:
        log_id = str(uuid.uuid4())
        
        # Store sentiment log
        query = """
        INSERT INTO sentiment_logs (
            log_id, employee_id, source, sentiment, score, text_content, 
            timestamp, context, created_at
        ) VALUES (%(log_id)s, %(employee_id)s, %(source)s, %(sentiment)s, %(score)s, %(text_content)s, %(timestamp)s, %(context)s, %(created_at)s)
        """
        
        params = {
            "log_id": log_id,
            "employee_id": payload.employee_id,
            "source": payload.source,
            "sentiment": payload.sentiment,
            "score": payload.score,
            "text_content": payload.text_content,
            "timestamp": payload.timestamp or datetime.utcnow(),
            "context": str(payload.context) if payload.context else None,
            "created_at": datetime.utcnow()
        }
        
        db_client.execute(query, params)
        
        return SentimentLogResponse(
            success=True,
            log_id=log_id,
            message="Sentiment logged successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sentiment logging failed: {str(e)}"
        )

@router.post("/wellness-check", response_model=WellnessCheckResponse)
async def submit_wellness_check(payload: WellnessCheckRequest, current_user: str = Depends(get_current_user)):
    """Submit a comprehensive wellness check"""
    try:
        check_id = str(uuid.uuid4())
        
        # Calculate overall wellness score
        scores = [
            float(payload.mood_rating),
            payload.stress_level,
            payload.sleep_quality,
            payload.work_satisfaction,
            payload.social_support
        ]
        overall_score = sum(scores) / len(scores)
        
        # Determine risk level
        if overall_score <= 3.0:
            risk_level = "high"
        elif overall_score <= 4.0:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate recommendations
        recommendations = []
        if payload.stress_level > 7:
            recommendations.append("Consider stress management techniques")
        if payload.sleep_quality < 6:
            recommendations.append("Focus on improving sleep hygiene")
        if payload.work_satisfaction < 6:
            recommendations.append("Discuss work satisfaction with your manager")
        if payload.social_support < 6:
            recommendations.append("Consider joining team activities or social groups")
        
        # Store wellness check
        query = """
        INSERT INTO wellness_checks (
            check_id, employee_id, mood_rating, stress_level, sleep_quality,
            work_satisfaction, social_support, overall_score, risk_level,
            notes, created_at
        ) VALUES (%(check_id)s, %(employee_id)s, %(mood_rating)s, %(stress_level)s, %(sleep_quality)s, %(work_satisfaction)s, %(social_support)s, %(overall_score)s, %(risk_level)s, %(notes)s, %(created_at)s)
        """
        
        params = {
            "check_id": check_id,
            "employee_id": payload.employee_id,
            "mood_rating": payload.mood_rating,
            "stress_level": payload.stress_level,
            "sleep_quality": payload.sleep_quality,
            "work_satisfaction": payload.work_satisfaction,
            "social_support": payload.social_support,
            "overall_score": overall_score,
            "risk_level": risk_level,
            "notes": payload.notes,
            "created_at": datetime.utcnow()
        }
        
        db_client.execute(query, params)
        
        return WellnessCheckResponse(
            success=True,
            check_id=check_id,
            overall_score=overall_score,
            recommendations=recommendations,
            risk_level=risk_level,
            message="Wellness check submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Wellness check failed: {str(e)}"
        )

@router.get("/profile/{employee_id}", response_model=EmployeeProfile)
async def get_employee_profile(employee_id: str, current_user: str = Depends(get_current_user)):
    """Get employee profile and wellness summary"""
    try:
        # Get basic profile
        query = """
        SELECT name, email, department, role, cultural_background, preferred_language, created_at
        FROM employees WHERE employee_id = %(employee_id)s
        """
        
        result = db_client.execute(query, {"employee_id": employee_id})
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        row = result[0]
        
        # Get wellness summary
        wellness_summary = await session_service.get_employee_wellness_summary(employee_id)
        
        return EmployeeProfile(
            employee_id=employee_id,
            name=row[0],
            email=row[1],
            department=row[2],
            role=row[3],
            cultural_background=row[4],
            preferred_language=row[5],
            onboarding_date=row[6],
            last_session_date=wellness_summary.get("last_session"),
            total_sessions=wellness_summary.get("total_sessions", 0),
            average_mood_score=wellness_summary.get("average_mood", 3.0),
            wellness_status=wellness_summary.get("wellness_status", "stable"),
            created_at=row[6],
            updated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile retrieval failed: {str(e)}"
        )

@router.get("/wellness-summary/{employee_id}")
async def get_wellness_summary(employee_id: str, current_user: str = Depends(get_current_user)):
    """Get detailed wellness summary for an employee"""
    try:
        summary = await session_service.get_employee_wellness_summary(employee_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Wellness summary failed: {str(e)}"
        ) 