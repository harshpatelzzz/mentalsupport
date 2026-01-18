from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.models.appointment import AppointmentStatus
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
