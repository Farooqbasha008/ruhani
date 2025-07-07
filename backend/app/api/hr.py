from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ..models.hr import HRInsightsResponse, HRTrendsResponse, HRAtRiskResponse
from ..services.session_service import SessionService
from ..core.auth import get_current_user
from ..db.snowflake_client import SnowflakeClient

router = APIRouter()
session_service = SessionService()
db_client = SnowflakeClient()

@router.get("/insights", response_model=HRInsightsResponse)
async def get_insights():  # Temporarily removed authentication for testing
    """Get comprehensive wellness insights for the organization"""
    try:
        # Get overall statistics
        query = """
        SELECT 
            COUNT(DISTINCT employee_id) as total_employees,
            AVG(mood_score) as avg_mood,
            COUNT(*) as total_sessions,
            AVG(CASE WHEN mood_score <= 2.0 THEN 1 ELSE 0 END) as low_mood_percentage,
            AVG(CASE WHEN mood_score >= 4.0 THEN 1 ELSE 0 END) as high_mood_percentage
        FROM employee_sessions 
        WHERE status = 'completed' AND start_time >= DATEADD(day, -30, CURRENT_DATE())
        """
        
        result = db_client.execute(query)
        if result:
            row = result[0]
            total_employees = row[0] or 0
            avg_mood = row[1] or 3.0
            total_sessions = row[2] or 0
            low_mood_percentage = row[3] or 0.0
            high_mood_percentage = row[4] or 0.0
            
            # Get department breakdown
            dept_query = """
            SELECT 
                e.department,
                COUNT(DISTINCT e.employee_id) as employee_count,
                AVG(es.mood_score) as avg_mood,
                COUNT(es.session_id) as session_count
            FROM employees e
            LEFT JOIN employee_sessions es ON e.employee_id = es.employee_id 
                AND es.status = 'completed' 
                AND es.start_time >= DATEADD(day, -30, CURRENT_DATE())
            GROUP BY e.department
            ORDER BY avg_mood DESC
            """
            
            dept_result = db_client.execute(dept_query)
            department_insights = []
            for dept_row in dept_result:
                department_insights.append({
                    "department": dept_row[0],
                    "employee_count": dept_row[1],
                    "average_mood": dept_row[2] or 3.0,
                    "session_count": dept_row[3] or 0
                })
            
            insights = {
                "total_employees": total_employees,
                "average_mood": round(avg_mood, 2),
                "total_sessions_30_days": total_sessions,
                "low_mood_percentage": round(low_mood_percentage * 100, 1),
                "high_mood_percentage": round(high_mood_percentage * 100, 1),
                "department_insights": department_insights,
                "overall_wellness_status": _get_overall_status(avg_mood, low_mood_percentage),
                "recommendations": _get_org_recommendations(avg_mood, low_mood_percentage, total_sessions)
            }
            
            return HRInsightsResponse(data=insights)
        
        return HRInsightsResponse(data={"message": "No data available"})
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Insights retrieval failed: {str(e)}"
        )

@router.get("/trends", response_model=HRTrendsResponse)
async def get_trends():  # Temporarily removed authentication for testing
    """Get emotional and wellness trends over time"""
    try:
        # Get daily mood trends for the last 30 days
        trend_query = """
        SELECT 
            DATE(start_time) as date,
            AVG(mood_score) as avg_mood,
            COUNT(*) as session_count,
            AVG(CASE WHEN mood_score <= 2.0 THEN 1 ELSE 0 END) as low_mood_percentage
        FROM employee_sessions 
        WHERE status = 'completed' 
            AND start_time >= DATEADD(day, -30, CURRENT_DATE())
        GROUP BY DATE(start_time)
        ORDER BY date
        """
        
        result = db_client.execute(trend_query)
        daily_trends = []
        
        for row in result:
            daily_trends.append({
                "date": row[0].strftime("%Y-%m-%d"),
                "average_mood": round(row[1] or 3.0, 2),
                "session_count": row[2] or 0,
                "low_mood_percentage": round((row[3] or 0.0) * 100, 1)
            })
        
        # Get weekly patterns
        weekly_query = """
        SELECT 
            DAYOFWEEK(start_time) as day_of_week,
            AVG(mood_score) as avg_mood,
            COUNT(*) as session_count
        FROM employee_sessions 
        WHERE status = 'completed' 
            AND start_time >= DATEADD(day, -30, CURRENT_DATE())
        GROUP BY DAYOFWEEK(start_time)
        ORDER BY day_of_week
        """
        
        weekly_result = db_client.execute(weekly_query)
        weekly_patterns = []
        day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        
        for row in weekly_result:
            weekly_patterns.append({
                "day": day_names[row[0] - 1],
                "average_mood": round(row[1] or 3.0, 2),
                "session_count": row[2] or 0
            })
        
        # Get sentiment trends
        sentiment_query = """
        SELECT 
            sentiment,
            COUNT(*) as count,
            AVG(score) as avg_score
        FROM sentiment_logs 
        WHERE timestamp >= DATEADD(day, -30, CURRENT_DATE())
        GROUP BY sentiment
        ORDER BY count DESC
        """
        
        sentiment_result = db_client.execute(sentiment_query)
        sentiment_trends = []
        
        for row in sentiment_result:
            sentiment_trends.append({
                "sentiment": row[0],
                "count": row[1],
                "average_score": round(row[2] or 3.0, 2)
            })
        
        trends = {
            "daily_trends": daily_trends,
            "weekly_patterns": weekly_patterns,
            "sentiment_trends": sentiment_trends,
            "analysis": _analyze_trends(daily_trends, weekly_patterns)
        }
        
        return HRTrendsResponse(data=trends)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trends retrieval failed: {str(e)}"
        )

@router.get("/at-risk", response_model=HRAtRiskResponse)
async def get_at_risk():  # Temporarily removed authentication for testing
    """Get employees who may need attention"""
    try:
        # Find employees with declining mood or low engagement
        risk_query = """
        SELECT 
            e.employee_id,
            e.name,
            e.department,
            e.role,
            AVG(es.mood_score) as avg_mood,
            COUNT(es.session_id) as session_count,
            MAX(es.start_time) as last_session,
            AVG(CASE WHEN es.mood_score <= 2.0 THEN 1 ELSE 0 END) as low_mood_percentage
        FROM employees e
        LEFT JOIN employee_sessions es ON e.employee_id = es.employee_id 
            AND es.status = 'completed' 
            AND es.start_time >= DATEADD(day, -14, CURRENT_DATE())
        GROUP BY e.employee_id, e.name, e.department, e.role
        HAVING avg_mood <= 2.5 OR low_mood_percentage >= 0.5 OR session_count = 0
        ORDER BY avg_mood ASC, low_mood_percentage DESC
        LIMIT 20
        """
        
        result = db_client.execute(risk_query)
        at_risk_employees = []
        
        for row in result:
            employee_id = row[0]
            avg_mood = row[4] or 3.0
            low_mood_percentage = row[7] or 0.0
            
            # Determine risk level
            if avg_mood <= 2.0 or low_mood_percentage >= 0.7:
                risk_level = "high"
            elif avg_mood <= 2.5 or low_mood_percentage >= 0.5:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Get personalized recommendations
            wellness_summary = await session_service.get_employee_wellness_summary(employee_id)
            
            at_risk_employees.append({
                "employee_id": employee_id,
                "name": row[1],
                "department": row[2],
                "role": row[3],
                "average_mood": round(avg_mood, 2),
                "session_count": row[5] or 0,
                "last_session": row[6],
                "low_mood_percentage": round(low_mood_percentage * 100, 1),
                "risk_level": risk_level,
                "recommendations": wellness_summary.get("recommendations", []),
                "wellness_status": wellness_summary.get("wellness_status", "stable")
            })
        
        # Get overall risk statistics
        total_employees_query = "SELECT COUNT(*) FROM employees"
        total_result = db_client.execute(total_employees_query)
        total_employees = total_result[0][0] if total_result else 0
        
        risk_stats = {
            "total_employees": total_employees,
            "at_risk_count": len(at_risk_employees),
            "high_risk_count": len([e for e in at_risk_employees if e["risk_level"] == "high"]),
            "medium_risk_count": len([e for e in at_risk_employees if e["risk_level"] == "medium"]),
            "low_risk_count": len([e for e in at_risk_employees if e["risk_level"] == "low"])
        }
        
        return HRAtRiskResponse(data={
            "at_risk_employees": at_risk_employees,
            "risk_statistics": risk_stats,
            "recommendations": _get_risk_management_recommendations(risk_stats)
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"At-risk analysis failed: {str(e)}"
        )

@router.get("/employees")
async def get_all_employees():  # Temporarily removed authentication for testing
    """Get all employees with their wellness status"""
    try:
        query = """
        SELECT 
            e.employee_id,
            e.name,
            e.email,
            e.department,
            e.role,
            e.created_at,
            AVG(es.mood_score) as avg_mood,
            COUNT(es.session_id) as session_count,
            MAX(es.start_time) as last_session
        FROM employees e
        LEFT JOIN employee_sessions es ON e.employee_id = es.employee_id 
            AND es.status = 'completed'
        GROUP BY e.employee_id, e.name, e.email, e.department, e.role, e.created_at
        ORDER BY e.name
        """
        
        result = db_client.execute(query)
        employees = []
        
        for row in result:
            employee_id = row[0]
            avg_mood = row[6] or 3.0
            
            # Get wellness summary
            wellness_summary = await session_service.get_employee_wellness_summary(employee_id)
            
            employees.append({
                "employee_id": employee_id,
                "name": row[1],
                "email": row[2],
                "department": row[3],
                "role": row[4],
                "onboarding_date": row[5],
                "average_mood": round(avg_mood, 2),
                "total_sessions": row[7] or 0,
                "last_session": row[8],
                "wellness_status": wellness_summary.get("wellness_status", "stable"),
                "recommendations": wellness_summary.get("recommendations", [])
            })
        
        return {"employees": employees, "total_count": len(employees)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Employee list retrieval failed: {str(e)}"
        )

def _get_overall_status(avg_mood: float, low_mood_percentage: float) -> str:
    """Determine overall organizational wellness status"""
    if avg_mood >= 4.0 and low_mood_percentage < 0.2:
        return "excellent"
    elif avg_mood >= 3.5 and low_mood_percentage < 0.3:
        return "good"
    elif avg_mood >= 3.0 and low_mood_percentage < 0.4:
        return "stable"
    elif low_mood_percentage > 0.5:
        return "concerning"
    else:
        return "needs_attention"

def _get_org_recommendations(avg_mood: float, low_mood_percentage: float, total_sessions: int) -> List[str]:
    """Generate organizational wellness recommendations"""
    recommendations = []
    
    if avg_mood < 3.0:
        recommendations.append("Consider implementing stress management workshops")
        recommendations.append("Review workload distribution across teams")
    
    if low_mood_percentage > 0.3:
        recommendations.append("Increase mental health awareness programs")
        recommendations.append("Consider flexible work arrangements")
    
    if total_sessions < 50:  # Assuming 50+ employees
        recommendations.append("Encourage more regular wellness check-ins")
        recommendations.append("Promote the voice-based therapy feature")
    
    if avg_mood >= 4.0:
        recommendations.append("Maintain current wellness initiatives")
        recommendations.append("Share best practices across departments")
    
    return recommendations

def _analyze_trends(daily_trends: List[Dict], weekly_patterns: List[Dict]) -> Dict[str, Any]:
    """Analyze trends and provide insights"""
    if not daily_trends:
        return {"insights": ["Insufficient data for trend analysis"]}
    
    # Calculate trend direction
    recent_moods = [day["average_mood"] for day in daily_trends[-7:]]
    if len(recent_moods) >= 2:
        trend_direction = "improving" if recent_moods[-1] > recent_moods[0] else "declining"
    else:
        trend_direction = "stable"
    
    # Find best and worst days
    best_day = max(weekly_patterns, key=lambda x: x["average_mood"]) if weekly_patterns else None
    worst_day = min(weekly_patterns, key=lambda x: x["average_mood"]) if weekly_patterns else None
    
    insights = [
        f"Overall mood trend is {trend_direction}",
        f"Most active day for sessions: {max(weekly_patterns, key=lambda x: x['session_count'])['day'] if weekly_patterns else 'Unknown'}"
    ]
    
    if best_day and worst_day:
        insights.append(f"Best mood day: {best_day['day']}, Worst mood day: {worst_day['day']}")
    
    return {
        "trend_direction": trend_direction,
        "best_day": best_day,
        "worst_day": worst_day,
        "insights": insights
    }

def _get_risk_management_recommendations(risk_stats: Dict[str, Any]) -> List[str]:
    """Generate risk management recommendations"""
    recommendations = []
    
    if risk_stats["high_risk_count"] > 0:
        recommendations.append("Immediate intervention needed for high-risk employees")
        recommendations.append("Consider one-on-one check-ins with HR")
    
    if risk_stats["at_risk_count"] > risk_stats["total_employees"] * 0.2:
        recommendations.append("Consider organization-wide wellness initiatives")
        recommendations.append("Review workplace policies and culture")
    
    if risk_stats["medium_risk_count"] > 0:
        recommendations.append("Implement targeted wellness programs")
        recommendations.append("Provide additional mental health resources")
    
    return recommendations 