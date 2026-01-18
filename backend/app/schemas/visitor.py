from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class VisitorCreate(BaseModel):
    """Schema for creating a new visitor"""
    name: Optional[str] = Field(None, max_length=100)


class VisitorResponse(BaseModel):
    """Schema for visitor response"""
    id: UUID
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
