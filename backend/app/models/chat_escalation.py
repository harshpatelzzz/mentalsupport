from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.db.base import Base


class ChatEscalation(Base):
    """
    Tracks when a chat session has been escalated to a therapist.
    Used for analytics and to prevent multiple escalations per session.
    """
    __tablename__ = "chat_escalations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    # Reason for escalation: "emotional_distress" or "low_ai_confidence"
    reason = Column(String, nullable=False)
    
    # Whether user accepted the appointment suggestion
    user_accepted = Column(String, default="pending")  # "pending", "accepted", "declined"
    
    # Linked appointment ID if accepted
    appointment_id = Column(UUID(as_uuid=True), nullable=True)
    
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
