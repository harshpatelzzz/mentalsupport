from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime

from app.models.appointment import Appointment, AppointmentStatus
from app.models.visitor import Visitor
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.core.logging import logger


class AppointmentService:
    """
    Service layer for appointment management.
    Handles appointment creation, updates, and queries.
    """
    
    @staticmethod
    def create_appointment(
        db: Session,
        appointment_data: AppointmentCreate
    ) -> Appointment:
        """
        Create a new appointment with a linked chat session.
        
        Args:
            db: Database session
            appointment_data: Appointment creation data
            
        Returns:
            Created Appointment instance
        """
        # Create or get visitor
        visitor = Visitor(name=appointment_data.visitor_name)
        db.add(visitor)
        db.flush()  # Get visitor ID
        
        # Generate session ID for chat
        session_id = uuid4()
        
        # Create appointment
        appointment = Appointment(
            visitor_id=visitor.id,
            session_id=session_id,
            start_time=appointment_data.start_time,
            status=AppointmentStatus.SCHEDULED
        )
        
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        logger.info(f"Created appointment {appointment.id} with session {session_id}")
        return appointment
    
    @staticmethod
    def get_appointment(db: Session, appointment_id: UUID) -> Optional[Appointment]:
        """
        Get appointment by ID.
        
        Args:
            db: Database session
            appointment_id: Appointment UUID
            
        Returns:
            Appointment instance or None
        """
        return db.query(Appointment)\
            .filter(Appointment.id == appointment_id)\
            .first()
    
    @staticmethod
    def get_all_appointments(
        db: Session,
        status: Optional[AppointmentStatus] = None,
        limit: int = 100
    ) -> List[Appointment]:
        """
        Get all appointments, optionally filtered by status.
        
        Args:
            db: Database session
            status: Optional status filter
            limit: Maximum number of appointments to retrieve
            
        Returns:
            List of Appointment instances
        """
        query = db.query(Appointment)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        appointments = query\
            .order_by(desc(Appointment.start_time))\
            .limit(limit)\
            .all()
        
        return appointments
    
    @staticmethod
    def update_appointment(
        db: Session,
        appointment_id: UUID,
        update_data: AppointmentUpdate
    ) -> Optional[Appointment]:
        """
        Update appointment details.
        
        Args:
            db: Database session
            appointment_id: Appointment UUID
            update_data: Update data
            
        Returns:
            Updated Appointment instance or None
        """
        appointment = db.query(Appointment)\
            .filter(Appointment.id == appointment_id)\
            .first()
        
        if not appointment:
            return None
        
        if update_data.status:
            appointment.status = update_data.status
        
        if update_data.end_time:
            appointment.end_time = update_data.end_time
        
        appointment.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(appointment)
        
        logger.info(f"Updated appointment {appointment_id}")
        return appointment
    
    @staticmethod
    def get_upcoming_appointments(
        db: Session,
        limit: int = 50
    ) -> List[Appointment]:
        """
        Get upcoming scheduled appointments.
        
        Args:
            db: Database session
            limit: Maximum number of appointments
            
        Returns:
            List of upcoming Appointment instances
        """
        now = datetime.utcnow()
        
        appointments = db.query(Appointment)\
            .filter(
                and_(
                    Appointment.status == AppointmentStatus.SCHEDULED,
                    Appointment.start_time >= now
                )
            )\
            .order_by(Appointment.start_time)\
            .limit(limit)\
            .all()
        
        return appointments
    
    @staticmethod
    def get_appointment_by_session(
        db: Session,
        session_id: UUID
    ) -> Optional[Appointment]:
        """
        Get appointment by session ID.
        
        Args:
            db: Database session
            session_id: Session UUID
            
        Returns:
            Appointment instance or None
        """
        return db.query(Appointment)\
            .filter(Appointment.session_id == session_id)\
            .first()


appointment_service = AppointmentService()
