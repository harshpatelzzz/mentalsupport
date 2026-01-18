from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.db.base import Base


class EmotionData(Base):
    """
    Stores aggregated emotion analysis data for analytics.
    Separated from ChatMessage for optimized analytics queries.
    """
    __tablename__ = "emotion_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    message_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    emotion = Column(String, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    message_content = Column(Text, nullable=True)  # Optional: store for context
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
