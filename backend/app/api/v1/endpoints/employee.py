from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.session import WellnessSessionCreate, WellnessSessionResponse
from app.services.employee_service import EmployeeService
from app.api.deps import get_db

router = APIRouter()

@router.post("/sessions", response_model=WellnessSessionResponse)
def create_wellness_session(
    session_data: WellnessSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "employee":
        raise HTTPException(
            status_code=403,
            detail="Only employees can create wellness sessions"
        )
    
    service = EmployeeService(db)
    session = service.create_wellness_session(current_user, session_data)
    return session

@router.get("/sessions", response_model=List[WellnessSessionResponse])
def get_my_sessions(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = EmployeeService(db)
    return service.get_user_sessions(current_user.id, skip=skip, limit=limit)

@router.get("/wellness-summary")
def get_wellness_summary(
    days: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = EmployeeService(db)
    return service.get_user_wellness_summary(current_user.id, days=days)