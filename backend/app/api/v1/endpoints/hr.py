from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.wellness import HRDashboardCard, EmployeeWellnessReport
from app.services.hr_service import HRService
from app.api.deps import get_db

router = APIRouter()

@router.get("/dashboard", response_model=List[HRDashboardCard])
def get_hr_dashboard(
    department: str = None,
    team: str = None,
    days: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "hr":
        raise HTTPException(
            status_code=403,
            detail="Only HR personnel can access this dashboard"
        )
    
    service = HRService(db)
    return service.get_dashboard_overview(
        department=department,
        team=team,
        days=days
    )

@router.get("/employee/{employee_id}", response_model=EmployeeWellnessReport)
def get_employee_report(
    employee_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "hr":
        raise HTTPException(
            status_code=403,
            detail="Only HR personnel can access employee reports"
        )
    
    service = HRService(db)
    return service.get_employee_detailed_report(employee_id, days=days)

@router.get("/analytics")
def get_analytics_summary(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "hr":
        raise HTTPException(
            status_code=403,
            detail="Only HR personnel can access analytics"
        )
    
    service = HRService(db)
    return service.get_analytics_summary(days=days)