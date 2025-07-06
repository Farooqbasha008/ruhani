from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from app.models.session import MoodLevel

class HRDashboardCard(BaseModel):
    employee_id: str
    name: str
    email: str
    department: Optional[str] = None
    team: Optional[str] = None
    profile_picture: Optional[str] = None
    last_check_in: Optional[datetime] = None
    current_mood: Optional[str] = None
    mood_trend: List[Dict[str, Any]] = []
    alert_level: str = "gray"  # red, yellow, green, gray
    wellness_score: Optional[float] = None
    total_sessions: int = 0
    engagement_level: str = "low"  # low, medium, high

class EmployeeWellnessReport(BaseModel):
    employee: Dict[str, Any]
    report_period_days: int
    total_sessions: int
    sessions: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    mood_distribution: Dict[str, float]
    wellness_trends: Dict[str, str]
    recommendations: List[str]

class WellnessAlertCreate(BaseModel):
    alert_type: str
    severity: str
    description: str

class WellnessRecommendationCreate(BaseModel):
    recommendation_type: str
    title: str
    description: str
    priority: str = "medium"