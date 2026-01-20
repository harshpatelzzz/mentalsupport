"""
Chat Session Model

Tracks the state of each chat session to determine if bot or therapist is active.
"""

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from app.db.base import Base


class SessionMode(str, enum.Enum):
    """Session mode enum"""
    BOT_ONLY = "bot_only"
    THERAPIST_JOINED = "therapist_joined"


class ChatSession(Base):
    """
    Chat session state tracking.
    Determines whether bot should respond or therapist is active.
    """
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    mode = Column(SQLEnum(SessionMode), default=SessionMode.BOT_ONLY, nullable=False)
    therapist_joined_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
