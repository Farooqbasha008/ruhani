from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DIDDocument(BaseModel):
    """Decentralized Identifier Document"""
    id: str
    created: datetime
    authentication: List[Dict[str, Any]]
    context: str = Field(alias="@context", default="https://www.w3.org/ns/did/v1")

class VerifiableCredential(BaseModel):
    """Verifiable Credential model"""
    id: str
    type: List[str]
    issuer: str
    issuance_date: datetime = Field(alias="issuanceDate")
    expiration_date: Optional[datetime] = Field(alias="expirationDate", default=None)
    credential_subject: Dict[str, Any] = Field(alias="credentialSubject")
    proof: Dict[str, Any]
    context: List[str] = Field(alias="@context", default=["https://www.w3.org/2018/credentials/v1"])

class VerifiablePresentation(BaseModel):
    """Verifiable Presentation model"""
    id: str
    type: List[str]
    holder: str
    verifiable_credential: List[VerifiableCredential] = Field(alias="verifiableCredential")
    proof: Dict[str, Any]
    context: List[str] = Field(alias="@context", default=["https://www.w3.org/2018/credentials/v1"])

class ConsentRequest(BaseModel):
    """Request for consent to access employee data"""
    employee_id: str
    data_categories: List[str]
    purpose: str
    expiration_days: int = 90

class ConsentResponse(BaseModel):
    """Response for consent request"""
    consent_id: str
    employee_id: str
    data_categories: List[str]
    authorized_parties: List[str]
    purpose: str
    credential_id: str
    granted_at: datetime
    expires_at: datetime

class EmployeeOnboardRequest(BaseModel):
    name: str
    github: Optional[str] = None
    linkedin: Optional[str] = None
    role: str
    email: str

class EmployeeOnboardResponse(BaseModel):
    success: bool
    message: str
    employee_id: Optional[str] = None
    did: Optional[str] = None
    created_at: Optional[datetime] = None

class SessionRequest(BaseModel):
    employee_id: str
    scheduled_time: Optional[str] = None
    audio_url: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 encoded audio data

class SessionResponse(BaseModel):
    success: bool
    message: str
    session_id: Optional[str] = None
    transcript: Optional[str] = None
    response: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 encoded audio data
    risk_level: Optional[str] = None  # 'low', 'medium', 'high'
    credential_id: Optional[str] = None

class SentimentLogRequest(BaseModel):
    employee_id: str
    source: str  # e.g., 'email', 'slack', 'chat'
    sentiment: str
    score: float
    timestamp: Optional[str] = None

class SentimentLogResponse(BaseModel):
    success: bool
    message: str
    log_id: Optional[str] = None

class Employee(BaseModel):
    id: str
    name: str
    email: str
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    team: str
    stressors: Optional[List[str]] = None
    onboarding_date: str
    did: Optional[str] = None
    did_document: Optional[Dict[str, Any]] = None

class Session(BaseModel):
    session_id: str
    employee_id: str
    session_time: str
    mood: Optional[str] = None
    summary: Optional[str] = None
    llm_response: Optional[str] = None
    risk_level: Optional[str] = None
    summary_hash: Optional[str] = None
    credential_id: Optional[str] = None

class Credential(BaseModel):
    credential_id: str
    credential_type: str
    issuer_did: str
    subject_did: str
    issuance_date: datetime
    expiration_date: Optional[datetime] = None
    credential_data: Dict[str, Any]
    revoked: bool = False
    revocation_date: Optional[datetime] = None
    created_at: datetime

class ConsentRecord(BaseModel):
    consent_id: str
    employee_id: str
    data_categories: List[str]
    authorized_parties: List[str]
    purpose: str
    credential_id: Optional[str] = None
    granted_at: datetime
    expires_at: Optional[datetime] = None
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    created_at: datetime

class HRInsight(BaseModel):
    id: str
    employee_id: str
    weekly_summary: str
    flags: Optional[List[str]] = None
    trends: Optional[Dict[str, Any]] = None
    created_at: str