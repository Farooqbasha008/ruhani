from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.models.user import User, UserRole
from app.db.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_employees(
        self, 
        department: Optional[str] = None, 
        team: Optional[str] = None,
        is_active: bool = True
    ) -> List[User]:
        query = self.db.query(User).filter(
            User.role == UserRole.EMPLOYEE,
            User.is_active == is_active
        )
        
        if department:
            query = query.filter(User.department == department)
        
        if team:
            query = query.filter(User.team == team)
        
        return query.all()
    
    def get_hr_users(self) -> List[User]:
        return self.db.query(User).filter(User.role == UserRole.HR).all()
    
    def count_employees(self) -> int:
        return self.db.query(func.count(User.id)).filter(
            User.role == UserRole.EMPLOYEE,
            User.is_active == True
        ).scalar()
    
    def update_last_login(self, user_id: str) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def get_departments(self) -> List[str]:
        return [
            row[0] for row in self.db.query(User.department).distinct().all()
            if row[0] is not None
        ]
    
    def get_teams(self, department: Optional[str] = None) -> List[str]:
        query = self.db.query(User.team).distinct()
        
        if department:
            query = query.filter(User.department == department)
        
        return [row[0] for row in query.all() if row[0] is not None]