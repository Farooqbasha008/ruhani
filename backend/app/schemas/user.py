from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.EMPLOYEE
    department: Optional[str] = None
    team: Optional[str] = None
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., description="User password (min 8 characters)")
    consent_voice_analysis: bool = Field(False, description="Consent for voice analysis")
    consent_facial_analysis: bool = False
    consent_data_sharing: bool = False

class UserUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    profile_picture: Optional[str] = None
    consent_voice_analysis: Optional[bool] = None
    consent_facial_analysis: Optional[bool] = None
    consent_data_sharing: Optional[bool] = None

class UserInDB(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)  # Correct v2 syntax

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)  # Correct v2 syntax