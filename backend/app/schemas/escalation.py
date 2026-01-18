from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class EscalationCreate(BaseModel):
    """Schema for creating a chat escalation"""
    session_id: UUID
    reason: str


class EscalationResponse(BaseModel):
    """Schema for escalation response"""
    id: UUID
    session_id: UUID
    reason: str
    user_accepted: str
    appointment_id: Optional[UUID]
    triggered_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class AutoBookRequest(BaseModel):
    """Schema for auto-booking appointment"""
    session_id: UUID
    visitor_id: Optional[UUID] = None
    visitor_name: Optional[str] = None


class AutoBookResponse(BaseModel):
    """Schema for auto-book response"""
    appointment_id: UUID
    session_id: UUID
    start_time: datetime
    end_time: datetime
    message: str
