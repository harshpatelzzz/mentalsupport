from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.db.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.schemas.escalation import AutoBookRequest, AutoBookResponse
from app.models.appointment import AppointmentStatus, Appointment
from app.models.chat_escalation import ChatEscalation
from app.models.visitor import Visitor
from app.services.appointment_service import appointment_service
from app.core.logging import logger

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new appointment.
    Automatically creates a visitor and linked chat session.
    """
    try:
        new_appointment = appointment_service.create_appointment(db, appointment)
        
        # Include visitor name in response
        response_data = AppointmentResponse.from_orm(new_appointment)
        response_data.visitor_name = new_appointment.visitor.name
        
        return response_data
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[AppointmentResponse])
def get_appointments(
    status: Optional[AppointmentStatus] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all appointments, optionally filtered by status.
    """
    appointments = appointment_service.get_all_appointments(db, status, limit)
    
    # Add visitor names to responses
    responses = []
    for appt in appointments:
        response = AppointmentResponse.from_orm(appt)
        response.visitor_name = appt.visitor.name if appt.visitor else None
        responses.append(response)
    
    return responses


@router.get("/upcoming", response_model=List[AppointmentResponse])
def get_upcoming_appointments(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get upcoming scheduled appointments.
    """
    appointments = appointment_service.get_upcoming_appointments(db, limit)
    
    responses = []
    for appt in appointments:
        response = AppointmentResponse.from_orm(appt)
        response.visitor_name = appt.visitor.name if appt.visitor else None
        responses.append(response)
    
    return responses


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific appointment by ID.
    """
    appointment = appointment_service.get_appointment(db, appointment_id)
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    response = AppointmentResponse.from_orm(appointment)
    response.visitor_name = appointment.visitor.name if appointment.visitor else None
    
    return response


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: UUID,
    update_data: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an appointment (status, end_time, etc.).
    """
    appointment = appointment_service.update_appointment(db, appointment_id, update_data)
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    response = AppointmentResponse.from_orm(appointment)
    response.visitor_name = appointment.visitor.name if appointment.visitor else None
    
    return response


@router.get("/session/{session_id}", response_model=AppointmentResponse)
def get_appointment_by_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get appointment by chat session ID.
    """
    appointment = appointment_service.get_appointment_by_session(db, session_id)
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found for this session")
    
    response = AppointmentResponse.from_orm(appointment)
    response.visitor_name = appointment.visitor.name if appointment.visitor else None
    
    return response


@router.post("/auto-book", response_model=AutoBookResponse)
def auto_book_appointment(
    request: AutoBookRequest,
    db: Session = Depends(get_db)
):
    """
    Automatically book an appointment when chat escalation is triggered.
    Finds next available slot and creates appointment linked to chat session.
    """
    try:
        # Check if appointment already exists for this session
        existing_appointment = db.query(Appointment)\
            .filter(Appointment.session_id == request.session_id)\
            .first()
        
        if existing_appointment:
            logger.info(f"Appointment already exists for session {request.session_id}")
            return AutoBookResponse(
                appointment_id=existing_appointment.id,
                session_id=existing_appointment.session_id,
                start_time=existing_appointment.start_time,
                end_time=existing_appointment.end_time or existing_appointment.start_time + timedelta(minutes=45),
                message="Your appointment has been confirmed."
            )
        
        # Find or create visitor
        if request.visitor_id:
            visitor = db.query(Visitor).filter(Visitor.id == request.visitor_id).first()
            if not visitor:
                visitor = Visitor(name=request.visitor_name)
                db.add(visitor)
                db.flush()
        else:
            visitor = Visitor(name=request.visitor_name or "Anonymous")
            db.add(visitor)
            db.flush()
        
        # Calculate next available slot (for demo: 2 hours from now)
        start_time = datetime.utcnow() + timedelta(hours=2)
        end_time = start_time + timedelta(minutes=45)
        
        # Create appointment
        appointment = Appointment(
            visitor_id=visitor.id,
            session_id=request.session_id,
            start_time=start_time,
            end_time=end_time,
            status=AppointmentStatus.SCHEDULED
        )
        
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        # Update escalation record with appointment ID
        escalation = db.query(ChatEscalation)\
            .filter(ChatEscalation.session_id == request.session_id)\
            .first()
        
        if escalation:
            escalation.appointment_id = appointment.id
            escalation.resolved_at = datetime.utcnow()
            db.commit()
        
        logger.info(f"Auto-booked appointment {appointment.id} for session {request.session_id}")
        
        # Format confirmation message
        time_str = start_time.strftime("%B %d at %I:%M %p UTC")
        confirmation_message = f"✅ Your appointment has been booked.\n🕒 {time_str}\nA therapist will join you here at that time."
        
        return AutoBookResponse(
            appointment_id=appointment.id,
            session_id=appointment.session_id,
            start_time=start_time,
            end_time=end_time,
            message=confirmation_message
        )
        
    except Exception as e:
        logger.error(f"Error auto-booking appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))
