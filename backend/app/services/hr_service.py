from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.user import User, UserRole
from app.models.session import WellnessSession
from app.models.wellness import WellnessAlert
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.session_repository import SessionRepository
from app.schemas.wellness import HRDashboardCard, EmployeeWellnessReport

class HRService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)
    
    def get_dashboard_overview(
        self, 
        department: Optional[str] = None,
        team: Optional[str] = None,
        days: int = 7
    ) -> List[HRDashboardCard]:
        # Get all employees
        employees = self.user_repo.get_employees(department=department, team=team)
        
        dashboard_cards = []
        
        for employee in employees:
            # Get recent sessions
            recent_sessions = self.session_repo.get_recent_by_user_id(
                employee.id, days=days
            )
            
            # Calculate metrics
            card = self._create_dashboard_card(employee, recent_sessions)
            dashboard_cards.append(card)
        
        # Sort by risk level (red first)
        dashboard_cards.sort(key=lambda x: self._risk_priority(x.alert_level))
        
        return dashboard_cards
    
    def get_employee_detailed_report(
        self, 
        employee_id: str, 
        days: int = 30
    ) -> EmployeeWellnessReport:
        employee = self.user_repo.get_by_id(employee_id)
        if not employee:
            raise ValueError("Employee not found")
        
        sessions = self.session_repo.get_recent_by_user_id(employee_id, days=days)
        alerts = self.db.query(WellnessAlert).filter(
            WellnessAlert.user_id == employee_id,
            WellnessAlert.triggered_at >= datetime.utcnow() - timedelta(days=days)
        ).all()
        
        return self._generate_detailed_report(employee, sessions, alerts, days)
    
    def get_analytics_summary(self, days: int = 30) -> Dict:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Total employees
        total_employees = self.user_repo.count_employees()
        
        # Active employees (had at least one session)
        active_employees = self.session_repo.count_active_users(since_date)
        
        # Total sessions
        total_sessions = self.session_repo.count_sessions(since_date)
        
        # Mood distribution
        mood_distribution = self.session_repo.get_mood_distribution(since_date)
        
        # Risk distribution
        risk_distribution = self._calculate_risk_distribution()
        
        # Trends
        trends = self._calculate_trends(days)
        
        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "total_sessions": total_sessions,
            "mood_distribution": mood_distribution,
            "risk_distribution": risk_distribution,
            "trends": trends,
            "generated_at": datetime.utcnow()
        }
    
    def _create_dashboard_card(
        self, 
        employee: User, 
        sessions: List[WellnessSession]
    ) -> HRDashboardCard:
        # Calculate current mood
        current_mood = sessions[0].mood_level if sessions else None
        
        # Calculate mood trend
        mood_trend = []
        for session in sessions[-7:]:  # Last 7 sessions
            mood_trend.append({
                "date": session.timestamp.isoformat(),
                "mood": session.mood_level,
                "score": self._mood_to_score(session.mood_level)
            })
        
        # Calculate alert level
        alert_level = self._calculate_alert_level(sessions)
        
        # Get wellness score
        wellness_scores = [s.ai_wellness_score for s in sessions if s.ai_wellness_score]
        avg_wellness_score = sum(wellness_scores) / len(wellness_scores) if wellness_scores else None
        
        return HRDashboardCard(
            employee_id=employee.id,
            name=employee.name,
            email=employee.email,
            department=employee.department,
            team=employee.team,
            profile_picture=employee.profile_picture,
            last_check_in=sessions[0].timestamp if sessions else None,
            current_mood=current_mood,
            mood_trend=mood_trend,
            alert_level=alert_level,
            wellness_score=avg_wellness_score,
            total_sessions=len(sessions),
            engagement_level=self._calculate_engagement_level(sessions)
        )
    
    def _calculate_alert_level(self, sessions: List[WellnessSession]) -> str:
        if not sessions:
            return "gray"
        
        # Check recent sessions (last 3)
        recent_sessions = sessions[:3]
        
        # Count concerning moods
        concerning_moods = sum(1 for s in recent_sessions 
                             if s.mood_level in ["very_sad", "sad"])
        
        # Check AI risk assessments
        high_risk = sum(1 for s in recent_sessions 
                       if s.ai_risk_assessment == "high")
        
        if high_risk > 0 or concerning_moods >= 2:
            return "red"
        elif concerning_moods >= 1:
            return "yellow"
        else:
            return "green"
    
    def _calculate_engagement_level(self, sessions: List[WellnessSession]) -> str:
        if len(sessions) >= 5:
            return "high"
        elif len(sessions) >= 2:
            return "medium"
        else:
            return "low"
    
    def _mood_to_score(self, mood_level) -> float:
        mood_map = {
            "very_sad": 0.0,
            "sad": 0.25,
            "neutral": 0.5,
            "happy": 0.75,
            "very_happy": 1.0
        }
        return mood_map.get(mood_level, 0.5)
    
    def _risk_priority(self, alert_level: str) -> int:
        priority_map = {"red": 0, "yellow": 1, "green": 2, "gray": 3}
        return priority_map.get(alert_level, 3)
    
    def _calculate_risk_distribution(self) -> Dict[str, int]:
        # This would calculate across all employees
        return {
            "low": 0,
            "medium": 0,
            "high": 0
        }
    
    def _calculate_trends(self, days: int) -> Dict:
        # Calculate various trends
        return {
            "mood_trend": "stable",
            "engagement_trend": "increasing",
            "wellness_trend": "improving"
        }
    
    def _generate_detailed_report(
        self, 
        employee: User, 
        sessions: List[WellnessSession], 
        alerts: List[WellnessAlert], 
        days: int
    ) -> EmployeeWellnessReport:
        # Generate comprehensive report
        return EmployeeWellnessReport(
            employee=employee,
            report_period_days=days,
            total_sessions=len(sessions),
            sessions=sessions,
            alerts=alerts,
            mood_distribution=self._calculate_mood_distribution(sessions),
            wellness_trends=self._calculate_wellness_trends(sessions),
            recommendations=self._generate_recommendations(sessions, alerts)
        )