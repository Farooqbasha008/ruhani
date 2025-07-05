from fastapi import APIRouter, Depends, HTTPException
from ..models.employee import EmployeeOnboardRequest, EmployeeOnboardResponse, SessionRequest, SessionResponse, SentimentLogRequest, SentimentLogResponse

router = APIRouter()

@router.post("/onboard", response_model=EmployeeOnboardResponse)
def onboard_employee(payload: EmployeeOnboardRequest):
    # TODO: Fetch public info via Fetch.ai, store in Snowflake, log via Coral
    return EmployeeOnboardResponse(success=True, message="Onboarded (stub)")

@router.post("/session", response_model=SessionResponse)
def schedule_session(payload: SessionRequest):
    # TODO: Schedule/record session, use Groq STT, LLM, ElevenLabs TTS
    return SessionResponse(success=True, message="Session scheduled/recorded (stub)")

@router.post("/sentiment", response_model=SentimentLogResponse)
def log_sentiment(payload: SentimentLogRequest):
    # TODO: Store sentiment in Snowflake, log via Coral
    return SentimentLogResponse(success=True, message="Sentiment logged (stub)") 