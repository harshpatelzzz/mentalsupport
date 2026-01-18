from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.therapist import TherapistNoteCreate, TherapistNoteResponse
from app.schemas.analytics import EmotionTrend
from app.schemas.escalation import EscalationResponse
from app.models.therapist_note import TherapistNote
from app.models.chat_escalation import ChatEscalation
from app.services.analytics_service import analytics_service
from app.core.logging import logger

router = APIRouter(prefix="/api/therapist", tags=["therapist"])


@router.post("/notes", response_model=TherapistNoteResponse)
def create_note(
    note_data: TherapistNoteCreate,
    db: Session = Depends(get_db)
):
    """
    Create a private therapist note for an appointment.
    These notes are NOT visible to visitors.
    """
    try:
        note = TherapistNote(
            appointment_id=note_data.appointment_id,
            note=note_data.note
        )
        
        db.add(note)
        db.commit()
        db.refresh(note)
        
        logger.info(f"Created therapist note for appointment {note_data.appointment_id}")
        return note
    
    except Exception as e:
        logger.error(f"Error creating therapist note: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notes/appointment/{appointment_id}", response_model=List[TherapistNoteResponse])
def get_appointment_notes(
    appointment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all therapist notes for a specific appointment.
    """
    notes = db.query(TherapistNote)\
        .filter(TherapistNote.appointment_id == appointment_id)\
        .order_by(TherapistNote.created_at.desc())\
        .all()
    
    return notes


@router.get("/emotion-timeline/{session_id}", response_model=List[EmotionTrend])
def get_session_emotion_timeline(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get emotion timeline for a specific chat session.
    Used for therapist dashboard visualization.
    """
    timeline = analytics_service.get_session_emotion_timeline(db, session_id)
    return timeline


@router.get("/active-sessions")
def get_active_sessions():
    """
    Get list of currently active chat sessions.
    Used for therapist to see which sessions they can join.
    """
    from app.websocket.connection_manager import manager
    
    active_sessions = manager.get_active_sessions()
    
    return {
        "active_sessions": active_sessions,
        "count": len(active_sessions)
    }


@router.get("/session/{session_id}/participants")
def get_session_participants(
    session_id: str
):
    """
    Get number of participants in a session.
    """
    from app.websocket.connection_manager import manager
    
    count = manager.get_connection_count(session_id)
    
    return {
        "session_id": session_id,
        "participant_count": count
    }


@router.get("/escalations", response_model=List[EscalationResponse])
def get_all_escalations(
    db: Session = Depends(get_db)
):
    """
    Get all chat escalations for therapist visibility.
    Shows which sessions needed professional intervention.
    """
    escalations = db.query(ChatEscalation)\
        .order_by(ChatEscalation.triggered_at.desc())\
        .limit(100)\
        .all()
    
    return escalations


@router.get("/escalations/session/{session_id}", response_model=EscalationResponse)
def get_session_escalation(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get escalation details for a specific session.
    """
    escalation = db.query(ChatEscalation)\
        .filter(ChatEscalation.session_id == UUID(session_id))\
        .first()
    
    if not escalation:
        raise HTTPException(status_code=404, detail="No escalation found for this session")
    
    return escalation
