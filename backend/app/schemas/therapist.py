from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class TherapistNoteCreate(BaseModel):
    """Schema for creating a therapist note"""
    appointment_id: UUID
    note: str = Field(..., min_length=1, max_length=10000)


class TherapistNoteResponse(BaseModel):
    """Schema for therapist note response"""
    id: UUID
    appointment_id: UUID
    note: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
