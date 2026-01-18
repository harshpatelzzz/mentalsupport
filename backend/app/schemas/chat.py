from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.chat import SenderType


class EmotionAnalysis(BaseModel):
    """Schema for emotion analysis result"""
    emotion: str
    confidence: float
    timestamp: datetime


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    session_id: UUID
    sender_type: SenderType
    content: str = Field(..., min_length=1, max_length=5000)
    visitor_id: Optional[UUID] = None


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: UUID
    session_id: UUID
    sender_type: SenderType
    content: str
    emotion: Optional[str]
    confidence: Optional[float]
    is_read: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryRequest(BaseModel):
    """Schema for requesting chat history"""
    session_id: UUID
    limit: int = Field(default=100, ge=1, le=500)
