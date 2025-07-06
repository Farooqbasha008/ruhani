from sqlalchemy import Column, String, DateTime, Float, Integer, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class WellnessAlert(Base):
    __tablename__ = "wellness_alerts"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    alert_type = Column(String, nullable=False)  # burnout_risk, depression_risk, stress_spike
    severity = Column(String, nullable=False)    # low, medium, high, critical
    description = Column(Text, nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(String, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="wellness_alerts")
    acknowledged_by_user = relationship("User", foreign_keys=[acknowledged_by])

class WellnessRecommendation(Base):
    __tablename__ = "wellness_recommendations"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    recommendation_type = Column(String, nullable=False)  # resource, meeting, break, support
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default="medium")  # low, medium, high
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    actioned_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", backref="wellness_recommendations")