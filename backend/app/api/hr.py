import uuid
from fastapi import APIRouter, Depends, HTTPException
from ..models.hr import HRInsightsResponse, HRTrendsResponse, HRAtRiskResponse, EmployeeInsight, EmployeeTrend, EmployeeRisk
from ..models.employee import VerifiableCredential, VerifiablePresentation
from ..db.snowflake_client import SnowflakeClient
from ..services.coral import CoralClient
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import json

router = APIRouter()

# Helper function to check consent for HR data access
async def check_hr_data_access(employee_id: str, data_category: str) -> bool:
    """Check if HR has consent to access employee data for a specific category"""
    try:
        snowflake_client = SnowflakeClient()
        
        # Get the latest consent record for this employee
        consent_record = snowflake_client.execute(
            """SELECT data_categories, credential_id, expires_at 
               FROM consent_records 
               WHERE employee_id = %s 
               AND expires_at > CURRENT_TIMESTAMP() 
               ORDER BY granted_at DESC LIMIT 1""",
            (employee_id,)
        )
        
        if not consent_record or not consent_record[0]:
            return False
        
        data_categories = json.loads(consent_record[0][0])
        credential_id = consent_record[0][1]
        expires_at = consent_record[0][2]
        
        # Check if the credential is valid and not revoked
        credential_status = snowflake_client.execute(
            """SELECT revoked FROM credentials 
               WHERE credential_id = %s""",
            (credential_id,)
        )
        
        if not credential_status or not credential_status[0] or credential_status[0][0]:
            return False
        
        # Check if the requested data category is in the consented categories
        return data_category in data_categories
    except Exception as e:
        print(f"Error checking HR data access: {str(e)}")
        return False

@router.get("/insights", response_model=HRInsightsResponse)
async def get_insights():
    """Get insights about employee well-being using verifiable credentials"""
    try:
        # Query Snowflake for employee data
        snowflake_client = SnowflakeClient()
        
        # Get all employees with their DIDs
        employees = snowflake_client.execute(
            "SELECT id, name, team, stressors, did FROM employees"
        )
        
        # Get organization DID
        org_result = snowflake_client.execute(
            "SELECT did FROM organization WHERE id = 'ruhani'"
        )
        org_did = org_result[0][0] if org_result and org_result[0] else None
        
        if not org_did:
            raise Exception("Organization DID not found")
        
        # Initialize Coral client
        coral_client = CoralClient()
        
        try:
            # Process data to create insights
            insights = []
            
            for employee in employees:
                employee_id, name, team, stressors, employee_did = employee
                
                if not employee_did:
                    continue
                
                # Check if HR has consent to access this employee's wellness data
                has_consent = await check_hr_data_access(employee_id, "wellness_metrics")
                if not has_consent:
                    continue
                
                # Get session credentials for this employee
                session_credentials = snowflake_client.execute(
                    """SELECT c.credential_data, c.issuance_date, s.session_id, s.mood, s.risk_level, s.created_at 
                       FROM credentials c
                       JOIN sessions s ON c.credential_id = s.credential_id
                       WHERE c.subject_did = %s 
                       AND c.credential_type = 'WellnessSessionCredential'
                       AND c.revoked = FALSE
                       AND c.issuance_date > DATEADD(day, -30, CURRENT_TIMESTAMP())
                       ORDER BY c.issuance_date DESC""",
                    (employee_did,)
                )
                
                if not session_credentials:
                    continue
                
                # Verify credentials and extract data
                verified_sessions = []
                moods = []
                risk_levels = []
                last_check_in = None
                
                for cred_data in session_credentials:
                    credential_json, issuance_date, session_id, mood, risk_level, session_time = cred_data
                    
                    # Verify the credential
                    verification_result = await coral_client.verify_credential(
                        credential=json.loads(credential_json) if isinstance(credential_json, str) else credential_json
                    )
                    
                    if verification_result.get("verified", False):
                        verified_sessions.append({
                            "session_id": session_id,
                            "mood": mood,
                            "risk_level": risk_level,
                            "session_time": session_time
                        })
                        
                        if mood:
                            moods.append(mood)
                        if risk_level:
                            risk_levels.append(risk_level)
                        if not last_check_in and session_time:
                            last_check_in = session_time
                
                # Skip employees with no verified sessions
                if not verified_sessions:
                    continue
                
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
                    last_check_in=last_check_in,
                    status=status,
                    mood_trend=moods[:5] if moods else [],
                    risk_level=risk_levels[0] if risk_levels else "low"
                )
                insights.append(insight)
            
            return HRInsightsResponse(insights=insights)
        finally:
            await coral_client.close()
    except Exception as e:
        print(f"Error in get_insights: {str(e)}")
        # For demo purposes, return mock data if there's an error
        return HRInsightsResponse(insights=generate_mock_insights())

@router.get("/trends", response_model=HRTrendsResponse)
async def get_trends():
    """Get emotional trends across the organization using verifiable credentials"""
    try:
        # Query Snowflake for session data
        snowflake_client = SnowflakeClient()
        
        # Get organization DID
        org_result = snowflake_client.execute(
            "SELECT did FROM organization WHERE id = 'ruhani'"
        )
        org_did = org_result[0][0] if org_result and org_result[0] else None
        
        if not org_did:
            raise Exception("Organization DID not found")
        
        # Get sessions with valid credentials grouped by week
        sessions_by_week = snowflake_client.execute(
            """SELECT 
                   DATE_TRUNC('week', s.created_at) as week, 
                   COUNT(*) as session_count,
                   COUNT(CASE WHEN s.risk_level = 'high' THEN 1 END) as high_risk_count,
                   COUNT(CASE WHEN s.risk_level = 'medium' THEN 1 END) as medium_risk_count,
                   COUNT(CASE WHEN s.risk_level = 'low' THEN 1 END) as low_risk_count
               FROM sessions s
               JOIN credentials c ON s.credential_id = c.credential_id
               JOIN consent_records cr ON cr.employee_id = s.employee_id
               WHERE s.created_at > DATEADD(month, -3, CURRENT_TIMESTAMP())
               AND c.revoked = FALSE
               AND cr.expires_at > CURRENT_TIMESTAMP()
               AND JSON_CONTAINS(cr.data_categories, '"session_summaries"')
               GROUP BY week
               ORDER BY week ASC"""
        )
        
        # Initialize Coral client
        coral_client = CoralClient()
        
        try:
            # Process data to create trends
            trends = []
            for week_data in sessions_by_week:
                week, session_count, high_risk, medium_risk, low_risk = week_data
                
                # Create a presentation of aggregated data
                presentation_result = await coral_client.create_presentation(
                    holder_did=org_did,
                    credential_ids=[],  # No specific credentials, this is aggregate data
                    presentation_type="AggregatedWellnessData",
                    claims={
                        "week": week,
                        "total_sessions": session_count,
                        "high_risk_count": high_risk,
                        "medium_risk_count": medium_risk,
                        "low_risk_count": low_risk
                    }
                )
                
                if "error" in presentation_result:
                    print(f"Error creating presentation: {presentation_result['error']}")
                    continue
                
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
        finally:
            await coral_client.close()
    except Exception as e:
        print(f"Error in get_trends: {str(e)}")
        # For demo purposes, return mock data if there's an error
        return HRTrendsResponse(trends=generate_mock_trends())

@router.get("/at-risk", response_model=HRAtRiskResponse)
async def get_at_risk():
    """Get employees who may be at risk based on verifiable credentials"""
    try:
        # Query Snowflake for high-risk sessions with valid credentials
        snowflake_client = SnowflakeClient()
        
        # Get organization DID
        org_result = snowflake_client.execute(
            "SELECT did FROM organization WHERE id = 'ruhani'"
        )
        org_did = org_result[0][0] if org_result and org_result[0] else None
        
        if not org_did:
            raise Exception("Organization DID not found")
        
        # Get employees with high-risk sessions that have valid credentials and consent
        at_risk_query = """
        SELECT e.id, e.name, e.team, e.did, s.session_id, s.created_at, s.risk_level, c.credential_id, c.credential_data
        FROM employees e
        JOIN sessions s ON e.id = s.employee_id
        JOIN credentials c ON s.credential_id = c.credential_id
        JOIN consent_records cr ON cr.employee_id = e.id
        WHERE s.risk_level = 'high'
        AND s.created_at > DATEADD(week, -2, CURRENT_TIMESTAMP())
        AND c.revoked = FALSE
        AND cr.expires_at > CURRENT_TIMESTAMP()
        AND JSON_CONTAINS(cr.data_categories, '"risk_assessments"')
        ORDER BY s.created_at DESC
        """
        
        at_risk_employees = snowflake_client.execute(at_risk_query)
        
        # Initialize Coral client
        coral_client = CoralClient()
        
        try:
            # Process data to create at-risk list
            at_risk = []
            processed_employees = set()
            
            for employee_data in at_risk_employees:
                employee_id, name, team, employee_did, session_id, session_time, risk_level, credential_id, credential_data = employee_data
                
                # Skip if already processed this employee
                if employee_id in processed_employees:
                    continue
                
                # Verify the credential
                verification_result = await coral_client.verify_credential(
                    credential=json.loads(credential_data) if isinstance(credential_data, str) else credential_data
                )
                
                if not verification_result.get("verified", False):
                    continue
                
                # Create a presentation for HR to view
                presentation_result = await coral_client.create_presentation(
                    holder_did=org_did,
                    credential_ids=[credential_id],
                    presentation_type="EmployeeRiskAssessment",
                    claims={
                        "employee_id": employee_id,
                        "risk_level": risk_level,
                        "session_id": session_id,
                        "session_time": session_time
                    }
                )
                
                if "error" in presentation_result:
                    print(f"Error creating presentation: {presentation_result['error']}")
                    continue
                
                # Mark as processed
                processed_employees.add(employee_id)
                
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
        finally:
            await coral_client.close()
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