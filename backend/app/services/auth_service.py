from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest
from app.core.security import verify_password, get_password_hash, create_access_token
from app.db.repositories.user_repository import UserRepository
import uuid

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register_user(self, user_data: UserCreate) -> User:
        # Check if user already exists
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_dict = user_data.dict()
        user_dict["id"] = str(uuid.uuid4())
        user_dict["password_hash"] = get_password_hash(user_data.password)
        del user_dict["password"]
        
        user = User(**user_dict)
        return self.user_repo.create(user)
    
    def authenticate_user(self, login_data: LoginRequest) -> Optional[User]:
        user = self.user_repo.get_by_email(login_data.email)
        if not user:
            return None
        
        if not verify_password(login_data.password, user.password_hash):
            return None
        
        # Update last login
        self.user_repo.update_last_login(user.id)
        return user
    
    def create_access_token_for_user(self, user: User) -> str:
        return create_access_token(subject=user.id)