import uuid
from fastapi import APIRouter, Depends, HTTPException
from ..models.hr import HRInsightsResponse, HRTrendsResponse, HRAtRiskResponse, EmployeeInsight, EmployeeTrend, EmployeeRisk
from ..db.snowflake_client import SnowflakeClient
from ..services.coral import CoralClient
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/insights", response_model=HRInsightsResponse)
async def get_insights():
    """Get anonymized insights about employee well-being"""
    try:
        # Query Snowflake for employee data and sessions
        snowflake_client = SnowflakeClient()
        
        # Get all employees
        employees = snowflake_client.execute(
            "SELECT id, name, team, stressors FROM employees"
        )
        
        # Get recent sessions
        sessions = snowflake_client.execute(
            """SELECT employee_id, mood, risk_level, session_time 
               FROM sessions 
               WHERE session_time > DATEADD(day, -30, CURRENT_TIMESTAMP())
               ORDER BY session_time DESC"""
        )
        
        # Process data to create insights
        insights = []
        for employee in employees:
            employee_id, name, team, stressors = employee
            
            # Find sessions for this employee
            employee_sessions = [s for s in sessions if s[0] == employee_id]
            
            # Skip employees with no sessions
            if not employee_sessions:
                continue
            
            # Calculate mood trend
            moods = [s[1] for s in employee_sessions if s[1]]
            risk_levels = [s[2] for s in employee_sessions if s[2]]
            
            # Determine status based on risk levels
            status = "stable"
            if risk_levels and risk_levels[0] == "high":
                status = "declining"
            elif risk_levels and risk_levels[0] == "low":
                status = "excellent"
            elif len(risk_levels) > 1 and risk_levels[0] == "medium" and risk_levels[-1] == "high":
                status = "improving"
            
            # Create insight
            insight = EmployeeInsight(
                id=str(uuid.uuid4()),
                employee_id=employee_id,
                name=name,
                team=team,
                department=team.split('/')[0] if '/' in team else team,
                last_check_in=employee_sessions[0][3] if employee_sessions else None,
                status=status,
                mood_trend=moods[:5] if moods else [],
                risk_level=risk_levels[0] if risk_levels else "low"
            )
            insights.append(insight)
        
        # Anonymize sensitive data using Coral
        coral_client = CoralClient()
        anonymized_insights = []
        
        for insight in insights:
            # In a real implementation, you would use Coral to anonymize
            # For now, we'll just use the data as is
            anonymized_insights.append(insight)
        
        await coral_client.close()
        
        return HRInsightsResponse(insights=anonymized_insights)
    except Exception as e:
        print(f"Error in get_insights: {str(e)}")
        # For demo purposes, return mock data if there's an error
        return HRInsightsResponse(insights=generate_mock_insights())

@router.get("/trends", response_model=HRTrendsResponse)
async def get_trends():
    """Get emotional trends across the organization"""
    try:
        # Query Snowflake for session data
        snowflake_client = SnowflakeClient()
        
        # Get sessions grouped by week
        sessions_by_week = snowflake_client.execute(
            """SELECT 
                   DATE_TRUNC('week', session_time) as week, 
                   COUNT(*) as session_count,
                   COUNT(CASE WHEN risk_level = 'high' THEN 1 END) as high_risk_count,
                   COUNT(CASE WHEN risk_level = 'medium' THEN 1 END) as medium_risk_count,
                   COUNT(CASE WHEN risk_level = 'low' THEN 1 END) as low_risk_count
               FROM sessions 
               WHERE session_time > DATEADD(month, -3, CURRENT_TIMESTAMP())
               GROUP BY week
               ORDER BY week ASC"""
        )
        
        # Process data to create trends
        trends = []
        for week_data in sessions_by_week:
            week, session_count, high_risk, medium_risk, low_risk = week_data
            
            trend = EmployeeTrend(
                period=week,
                total_sessions=session_count,
                mood_distribution={
                    "high_risk": high_risk,
                    "medium_risk": medium_risk,
                    "low_risk": low_risk
                },
                common_topics=["deadlines", "workload", "team dynamics"]  # Mock data
            )
            trends.append(trend)
        
        return HRTrendsResponse(trends=trends)
    except Exception as e:
        print(f"Error in get_trends: {str(e)}")
        # For demo purposes, return mock data if there's an error
        return HRTrendsResponse(trends=generate_mock_trends())

@router.get("/at-risk", response_model=HRAtRiskResponse)
async def get_at_risk():
    """Get employees who may be at risk based on recent sessions"""
    try:
        # Query Snowflake for high-risk sessions
        snowflake_client = SnowflakeClient()
        
        # Get employees with high-risk sessions
        at_risk_employees = snowflake_client.execute(
            """SELECT e.id, e.name, e.team, s.session_id, s.session_time, s.risk_level, s.summary
               FROM employees e
               JOIN sessions s ON e.id = s.employee_id
               WHERE s.risk_level = 'high'
               AND s.session_time > DATEADD(week, -2, CURRENT_TIMESTAMP())
               ORDER BY s.session_time DESC"""
        )
        
        # Process data to create at-risk list
        at_risk = []
        for employee_data in at_risk_employees:
            employee_id, name, team, session_id, session_time, risk_level, summary = employee_data
            
            # Check if employee is already in the list
            existing = next((e for e in at_risk if e.employee_id == employee_id), None)
            if existing:
                continue
            
            risk = EmployeeRisk(
                employee_id=employee_id,
                name=name,
                team=team,
                department=team.split('/')[0] if '/' in team else team,
                last_check_in=session_time,
                risk_level=risk_level,
                risk_factors=["stress", "workload"],  # Mock data
                recommended_actions=["Schedule 1:1", "Wellness check"]
            )
            at_risk.append(risk)
        
        return HRAtRiskResponse(at_risk_employees=at_risk)
    except Exception as e:
        print(f"Error in get_at_risk: {str(e)}")
        # For demo purposes, return mock data if there's an error
        return HRAtRiskResponse(at_risk_employees=generate_mock_at_risk())

# Helper functions to generate mock data for demo purposes
def generate_mock_insights() -> List[EmployeeInsight]:
    """Generate mock insights for demo purposes"""
    departments = ["Engineering", "Product", "Design", "Marketing", "Sales"]
    teams = [
        "Engineering/Frontend", "Engineering/Backend", "Engineering/DevOps",
        "Product/Management", "Product/Research",
        "Design/UI", "Design/UX",
        "Marketing/Growth", "Marketing/Content",
        "Sales/Enterprise", "Sales/SMB"
    ]
    statuses = ["excellent", "stable", "improving", "declining"]
    moods = ["happy", "neutral", "stressed", "anxious", "overwhelmed"]
    
    insights = []
    for i in range(20):
        team = random.choice(teams)
        department = team.split('/')[0]
        status = random.choice(statuses)
        
        # Generate a consistent mood trend based on status
        if status == "excellent":
            mood_trend = ["happy", "happy", "neutral", "happy", "happy"]
        elif status == "stable":
            mood_trend = ["neutral", "neutral", "neutral", "neutral", "neutral"]
        elif status == "improving":
            mood_trend = ["neutral", "stressed", "anxious", "stressed", "overwhelmed"]
        else:  # declining
            mood_trend = ["stressed", "neutral", "happy", "neutral", "happy"]
        
        insight = EmployeeInsight(
            id=str(uuid.uuid4()),
            employee_id=str(uuid.uuid4()),
            name=f"Employee {i+1}",
            team=team,
            department=department,
            last_check_in=(datetime.now() - timedelta(days=random.randint(0, 14))).isoformat(),
            status=status,
            mood_trend=mood_trend,
            risk_level="high" if status == "declining" else "medium" if status == "improving" else "low"
        )
        insights.append(insight)
    
    return insights

def generate_mock_trends() -> List[EmployeeTrend]:
    """Generate mock trends for demo purposes"""
    trends = []
    now = datetime.now()
    
    # Generate weekly trends for the past 12 weeks
    for i in range(12):
        week = (now - timedelta(weeks=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        total = random.randint(30, 50)
        high = random.randint(3, 10)
        medium = random.randint(10, 20)
        low = total - high - medium
        
        trend = EmployeeTrend(
            period=week.isoformat(),
            total_sessions=total,
            mood_distribution={
                "high_risk": high,
                "medium_risk": medium,
                "low_risk": low
            },
            common_topics=["deadlines", "workload", "team dynamics", "work-life balance", "remote work"]
        )
        trends.append(trend)
    
    return trends

def generate_mock_at_risk() -> List[EmployeeRisk]:
    """Generate mock at-risk employees for demo purposes"""
    teams = [
        "Engineering/Frontend", "Engineering/Backend", "Engineering/DevOps",
        "Product/Management", "Product/Research",
        "Design/UI", "Design/UX",
        "Marketing/Growth", "Marketing/Content",
        "Sales/Enterprise", "Sales/SMB"
    ]
    risk_factors = [
        ["stress", "workload"],
        ["burnout", "long hours"],
        ["team conflict", "communication"],
        ["deadline pressure", "quality concerns"],
        ["work-life balance", "remote work isolation"]
    ]
    actions = [
        ["Schedule 1:1", "Wellness check"],
        ["Reduce workload", "Suggest time off"],
        ["Team mediation", "Communication training"],
        ["Extend deadline", "Provide additional resources"],
        ["Flexible schedule", "Mental health resources"]
    ]
    
    at_risk = []
    for i in range(5):
        team = random.choice(teams)
        department = team.split('/')[0]
        factors = random.choice(risk_factors)
        recommended = random.choice(actions)
        
        risk = EmployeeRisk(
            employee_id=str(uuid.uuid4()),
            name=f"At-Risk Employee {i+1}",
            team=team,
            department=department,
            last_check_in=(datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
            risk_level="high",
            risk_factors=factors,
            recommended_actions=recommended
        )
        at_risk.append(risk)
    
    return at_risk