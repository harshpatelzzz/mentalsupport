from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class Visitor(Base):
    """
    Represents an anonymous visitor to the platform.
    Identified by UUID only - no authentication.
    """
    __tablename__ = "visitors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=True)  # Optional display name
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    appointments = relationship("Appointment", back_populates="visitor", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="visitor", cascade="all, delete-orphan")
