from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here for Alembic auto-generation
from app.models.visitor import Visitor  # noqa
from app.models.appointment import Appointment  # noqa
from app.models.chat import ChatMessage  # noqa
from app.models.emotion import EmotionData  # noqa
from app.models.therapist_note import TherapistNote  # noqa
from app.models.chat_escalation import ChatEscalation  # noqa
