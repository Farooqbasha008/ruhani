from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class EmployeeInsight(BaseModel):
    """Model for employee insight data"""
    id: str
    employee_id: str
    name: str
    team: str
    department: str
    last_check_in: Optional[str] = None
    status: str = Field(..., description="excellent, stable, improving, or declining")
    mood_trend: List[str] = Field(default_factory=list)
    risk_level: str = Field(..., description="high, medium, or low")

class EmployeeTrend(BaseModel):
    """Model for employee trend data"""
    period: str
    total_sessions: int
    mood_distribution: Dict[str, int]
    common_topics: List[str] = Field(default_factory=list)

class EmployeeRisk(BaseModel):
    """Model for at-risk employee data"""
    employee_id: str
    name: str
    team: str
    department: str
    last_check_in: str
    risk_level: str = Field(..., description="high, medium, or low")
    risk_factors: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)

class HRInsightsResponse(BaseModel):
    """Response model for HR insights endpoint"""
    insights: List[EmployeeInsight] = Field(default_factory=list)

class HRTrendsResponse(BaseModel):
    """Response model for HR trends endpoint"""
    trends: List[EmployeeTrend] = Field(default_factory=list)

class HRAtRiskResponse(BaseModel):
    """Response model for HR at-risk endpoint"""
    at_risk_employees: List[EmployeeRisk] = Field(default_factory=list)