from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.db.base import Base


class SenderType(str, enum.Enum):
    """Message sender type enumeration"""
    VISITOR = "visitor"
    THERAPIST = "therapist"
    AI = "ai"


class ChatMessage(Base):
    """
    Represents a single message in a chat session.
    Includes emotion analysis data for each message.
    """
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Chat session UUID
    visitor_id = Column(UUID(as_uuid=True), ForeignKey("visitors.id"), nullable=True, index=True)
    
    sender_type = Column(SQLEnum(SenderType), nullable=False)
    content = Column(Text, nullable=False)
    
    # Emotion analysis
    emotion = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Metadata
    is_read = Column(String, default="false")  # Simple read receipt tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    visitor = relationship("Visitor", back_populates="chat_messages")
