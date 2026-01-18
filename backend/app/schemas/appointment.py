from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    """Schema for creating a new appointment"""
    visitor_name: Optional[str] = Field(None, max_length=100)
    start_time: datetime
    

class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment"""
    status: Optional[AppointmentStatus] = None
    end_time: Optional[datetime] = None


class AppointmentResponse(BaseModel):
    """Schema for appointment response"""
    id: UUID
    visitor_id: UUID
    session_id: UUID
    start_time: datetime
    end_time: Optional[datetime]
    status: AppointmentStatus
    visitor_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
